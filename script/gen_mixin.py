import argparse
import ast
import importlib
import inspect
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="自动生成 Mixin 壳方法(proxy)，带 __init__(proxy)"
    )
    parser.add_argument("--source_file", required=True, help=".py 文件路径")
    parser.add_argument("--class_name", required=True, help="Mixin 类名")
    parser.add_argument(
        "--delegate_class",
        required=True,
        help="代理的类（点号全路径，如redis.asyncio.Redis）",
    )
    return parser.parse_args()


def get_defined_methods(file_path, class_name):
    tree = ast.parse(Path(file_path).read_text(encoding="utf-8"))
    method_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for body_item in node.body:
                if isinstance(body_item, ast.FunctionDef) or isinstance(
                    body_item, ast.AsyncFunctionDef
                ):
                    name = body_item.name
                    if not name.startswith("_"):
                        method_names.add(name)
    return method_names


def get_delegate_methods(delegate_cls):
    result = {}
    is_async = {}
    for name, member in inspect.getmembers(delegate_cls):
        if not name.startswith("_") and inspect.isfunction(member):
            try:
                sig = inspect.signature(member)
            except ValueError:
                continue
            params = []
            for pname, p in sig.parameters.items():
                if p.kind == inspect.Parameter.VAR_POSITIONAL:
                    params.append(f"*{pname}")
                elif p.kind == inspect.Parameter.VAR_KEYWORD:
                    params.append(f"**{pname}")
                elif pname == "self":
                    params.append("self")
                elif p.default is not inspect.Parameter.empty:
                    # 用真实默认值
                    default_val = p.default
                    # 仅简单类型/None特殊处理，复杂类型可用None/False/True，否则用...
                    if isinstance(default_val, str):
                        params.append(f"{pname}='{default_val}'")
                    elif default_val is None:
                        params.append(f"{pname}=None")
                    elif isinstance(default_val, bool):
                        params.append(f"{pname}={default_val}")
                    elif isinstance(default_val, (int, float)):
                        params.append(f"{pname}={default_val}")
                    else:
                        params.append(f"{pname}=...")
                else:
                    params.append(pname)
            result[name] = ", ".join(params)
            is_async[name] = inspect.iscoroutinefunction(member)
    return result, is_async


def gen_mixin_code(class_name, delegate_cls, existing_methods, delegate_class_path):
    delegate_methods, is_async = get_delegate_methods(delegate_cls)
    # 取类型名用于注解
    delegate_type = delegate_cls.__name__
    delegate_mod = ".".join(delegate_class_path.split(".")[:-1])
    code_lines = [
        "from __future__ import annotations",
        "from typing import TYPE_CHECKING",
        "try:",
        f"    from {delegate_mod} import {delegate_type}",
        "except ImportError:",
        "    ...",
        "if TYPE_CHECKING:  # pragma: no cover",
        f"    from {delegate_mod} import {delegate_type}",
        "",
        "class ProxyMixin:",
        "    # 自动生成的壳方法，只包含未自定义部分",
        "    # WARNING: 此文件为自动生成，修改后可能会被覆盖\n",
        f"    def __init__(self, proxy: {delegate_type}):",
        f"        self._proxy: {delegate_type} = proxy\n",
    ]
    for name in sorted(delegate_methods):
        if name not in existing_methods:
            params = delegate_methods[name]
            arg_names = []
            after_star = False
            kw_assigns = []
            for p in params.split(", "):
                if p == "self":
                    continue
                if p.startswith("**"):
                    arg_names.append(f"{p}")
                elif p.startswith("*"):
                    after_star = True
                    arg_names.append(f"{p}")
                elif after_star:
                    # 只要是*args之后的形参，用关键字参数转发
                    kw_assigns.append(f"{p.split('=')[0]}={p.split('=')[0]}")
                    arg_names.append(p)
                else:
                    arg_names.append(p)
            call_args = ", ".join(
                [
                    a.split("=")[0]
                    for a in arg_names
                    if not a.startswith("**") and not a.startswith("*") and "=" not in a
                ]
            )
            star_arg = (
                [a for a in arg_names if a.startswith("*")][0]
                if any(a.startswith("*") for a in arg_names)
                else ""
            )
            star_star_arg = (
                [a for a in arg_names if a.startswith("**")][0]
                if any(a.startswith("**") for a in arg_names)
                else ""
            )
            final_args = []
            if call_args:
                final_args.extend(call_args.split(", "))
            if star_arg:
                final_args.append(star_arg)
            final_call = ", ".join(final_args + kw_assigns)
            code_lines.append(f"    def {name}({params}):")
            code_lines.append(f"        return self._proxy.{name}({final_call})")
            code_lines.append("")
    return code_lines


def get_output_path(source_file):
    path = Path(source_file)
    return str(path.with_name(path.stem + "_proxy_mixin.py"))


if __name__ == "__main__":
    args = parse_args()
    *module_path, cls_short = args.delegate_class.split(".")
    delegate_mod = importlib.import_module(".".join(module_path))
    delegate_cls = getattr(delegate_mod, cls_short)
    existing_methods = get_defined_methods(args.source_file, args.class_name)
    mixin_lines = gen_mixin_code(
        args.class_name, delegate_cls, existing_methods, args.delegate_class
    )
    output_path = get_output_path(args.source_file)
    Path(output_path).write_text("\n".join(mixin_lines), encoding="utf-8")
    print(f"Mixin 壳方法已生成并覆盖写入：{output_path}")
