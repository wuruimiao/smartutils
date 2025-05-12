import ast
import sys
import re


def extract_defs(filename):
    with open(filename, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    result = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            if not node.name.startswith("_"):
                result.append(node.name)
        elif isinstance(node, ast.ClassDef):
            if not node.name.startswith("_"):
                result.append(node.name)
    return result


def find_docstring_and_imports(lines):
    """返回(docstring_end_line, import_end_line)"""
    idx = 0
    n = len(lines)

    # 跳过 shebang
    if idx < n and lines[idx].startswith("#!"):
        idx += 1

    # 跳过空行
    while idx < n and lines[idx].strip() == "":
        idx += 1

    docstring_end = idx
    if idx < n and (lines[idx].startswith('"""') or lines[idx].startswith("'''")):
        quote = lines[idx][:3]
        idx2 = idx
        if lines[idx].count(quote) >= 2:
            docstring_end = idx + 1  # 单行docstring
        else:
            idx2 += 1
            while idx2 < n:
                if quote in lines[idx2]:
                    docstring_end = idx2 + 1
                    break
                idx2 += 1
    else:
        docstring_end = idx

    # 跳过空行
    idx = docstring_end
    while idx < n and lines[idx].strip() == "":
        idx += 1

    # 跳过import语句
    import_end = idx
    while idx < n and (
        lines[idx].startswith("import ") or lines[idx].startswith("from ")
    ):
        import_end += 1
        idx += 1
    return docstring_end, import_end


def remove_existing_all(lines):
    """去除已有的__all__定义，返回新行列表"""
    pattern = re.compile(r"^\s*__all__\s*=")
    in_all = False
    new_lines = []
    for line in lines:
        if pattern.match(line):
            in_all = True
            continue
        if in_all and line.strip().endswith("]"):
            in_all = False
            continue
        if not in_all:
            new_lines.append(line)
    return new_lines


def main(filename):
    names = extract_defs(filename)
    if not names:
        print(f"No public classes or functions found in {filename}")
        return

    with open(filename, encoding="utf-8") as f:
        lines = f.readlines()

    # 移除已有 __all__
    lines = remove_existing_all(lines)

    doc_end, import_end = find_docstring_and_imports(lines)
    insert_at = max(doc_end, import_end)

    # 格式化 __all__ 行
    all_line = f"__all__ = {names!r}\n"

    # 插入 __all__ 行
    new_lines = lines[:insert_at]
    # 如果上一行不是空行，则补一个空行
    if new_lines and new_lines[-1].strip() != "":
        new_lines.append("\n")
    new_lines.append(all_line)
    # 再补一个空行
    new_lines.append("\n")
    new_lines.extend(lines[insert_at:])

    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"Updated {filename} with __all__: {names}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python add_all.py your_file.py")
        sys.exit(1)
    main(sys.argv[1])
