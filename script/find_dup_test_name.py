#!/usr/bin/env python3
import ast
import os
from collections import defaultdict


def find_test_functions(pyfile):
    with open(pyfile, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), pyfile)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            yield node.name, pyfile, node.lineno


def scan_test_functions(root_dir):
    test_funcs = defaultdict(list)
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".py") and not filename.endswith(".pyc"):
                print(f"scanning {filename}")
                pyfile = os.path.join(dirpath, filename)
                for name, file, lineno in find_test_functions(pyfile):
                    print(f"find {name}")
                    test_funcs[name].append((file, lineno))
    return test_funcs


if __name__ == "__main__":
    root = "."  # 项目根目录
    funcs = scan_test_functions(root)
    print("扫描重复结果：==============================")
    for name, locations in funcs.items():
        if len(locations) > 1:
            print(f"重复的测试函数名: {name}")
            for file, lineno in locations:
                print(f"  文件: {file}, 行号: {lineno}")
