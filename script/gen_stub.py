import argparse
import ast
import importlib
import inspect
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="生成 pyi stub 文件")
    parser.add_argument("--source_file", required=True, help=".py 文件路径")
    parser.add_argument("--class_name", required=True, help="类名")
    parser.add_argument(
        "--delegate_class", required=True, help="要代理的类（点号全路径）"
    )
    parser.add_argument("--stub_file", default=None, help="自定义输出 .pyi 文件路径")
    return parser.parse_args()


def get_self_methods(file_path, class_name):
    tree = ast.parse(Path(file_path).read_text(encoding="utf-8"))
    methods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for body_item in node.body:
                if isinstance(body_item, ast.FunctionDef):
                    name = body_item.name
                    if not name.startswith("_"):
                        args = [a.arg for a in body_item.args.args if a.arg != "self"]
                        arg_list = ["self"] + [f"{a}=..." for a in args]
                        methods.add((name, ", ".join(arg_list)))
    return dict(methods)


def get_delegate_methods(cls):
    result = {}
    for name, member in inspect.getmembers(cls):
        if not name.startswith("_") and inspect.isfunction(member):
            try:
                sig = inspect.signature(member)
            except ValueError:
                sig = None
            if sig:
                params = []
                for pname, p in sig.parameters.items():
                    if pname == "self":
                        params.append("self")
                    else:
                        params.append(f"{pname}=...")
                line = ", ".join(params)
            else:
                line = "self, *args, **kwargs"
            result[name] = line
    return result


def gen_stub(self_path, class_name, delegate_cls, stub_path):
    self_methods = get_self_methods(self_path, class_name)
    delegate_methods = get_delegate_methods(delegate_cls)
    stub_lines = [f"class {class_name}(object):"]
    # 先加入自定义方法
    for name, line in sorted(self_methods.items()):
        stub_lines.append(f"    def {name}({line}): ...")
    # 再加入代理方法（如本地实现未重复）
    for name, line in sorted(delegate_methods.items()):
        if name not in self_methods:
            stub_lines.append(f"    def {name}({line}): ...")
    result = "\n".join(stub_lines)
    Path(stub_path).write_text(result, encoding="utf-8")
    print(f"Stub 文件已生成：{stub_path}")


if __name__ == "__main__":
    args = parse_args()
    # 动态import代理类
    *module_path, cls_name = args.delegate_class.split(".")
    mod = importlib.import_module(".".join(module_path))
    delegate_cls = getattr(mod, cls_name)
    stub_file = args.stub_file or Path(args.source_file).with_suffix(".pyi")
    gen_stub(args.source_file, args.class_name, delegate_cls, stub_file)
