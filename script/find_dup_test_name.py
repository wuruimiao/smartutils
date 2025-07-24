#!/usr/bin/env python3
import ast
import glob
from collections import defaultdict


def find_test_functions(pyfile):
    with open(pyfile, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), pyfile)
    for node in ast.walk(tree):
        if isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef)
        ) and node.name.startswith("test_"):
            yield node.name, pyfile, node.lineno


def scan_test_functions(root_dirs):
    test_funcs = defaultdict(list)
    for root_dir in root_dirs:
        for pyfile in glob.glob(f"{root_dir}/**/*.py", recursive=True):
            print(f"scanning {pyfile}")
            for name, file, lineno in find_test_functions(pyfile):
                print(f"find {name}")
                test_funcs[name].append((file, lineno))
    return test_funcs


if __name__ == "__main__":
    funcs = scan_test_functions(["./tests", "./tests_real"])
    print("扫描重复结果：==============================")
    for name, locations in funcs.items():
        if len(locations) > 1:
            print(f"重复的测试函数名: {name}")
            for file, lineno in locations:
                print(f"  文件: {file}, 行号: {lineno}")
