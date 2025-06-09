import tomlkit

PYPROJECT_FILE = "pyproject.toml"


def main():
    with open(PYPROJECT_FILE, "r", encoding="utf-8") as f:
        doc = tomlkit.parse(f.read())

    poetry_deps = doc["tool"]["poetry"]["dependencies"]
    extras = doc["tool"]["poetry"]["extras"]

    # 只收集 optional=true 的依赖（不包含主依赖和python本身）
    all_pkgs = []
    for pkg, val in poetry_deps.items():
        if pkg == "python":
            continue
        if isinstance(val, dict) and val.get("optional", False):
            all_pkgs.append(pkg)
    # 去重并排序美观
    all_pkgs = sorted(
        set(all_pkgs), key=lambda x: all_pkgs.index(x) if x in all_pkgs else 9999
    )
    all_array = tomlkit.array()
    for pkg in all_pkgs:
        all_array.append(pkg)
    all_array.multiline(True)

    # 更新 all 分组
    extras["all"] = all_array

    with open(PYPROJECT_FILE, "w", encoding="utf-8") as f:
        f.write(tomlkit.dumps(doc))

    print(f"已更新 all 分组，包含依赖: {all_pkgs}")


if __name__ == "__main__":
    main()
