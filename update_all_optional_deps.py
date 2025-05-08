from tomlkit import parse, dumps, array
from tomlkit.toml_file import TOMLFile
from collections import OrderedDict

PYPROJECT_FILE = "pyproject.toml"


def main():
    # 读取原始 pyproject.toml
    tomlfile = TOMLFile(PYPROJECT_FILE)
    doc = tomlfile.read()

    opt_deps = doc["project"]["optional-dependencies"]

    # 合并所有分组依赖，去重，排除 'all' 和 'dev'
    deps_set = OrderedDict()
    for key, dep_list in opt_deps.items():
        if key in ("all", "dev"):
            continue
        for dep in dep_list:
            deps_set[dep] = None

    # 用 tomlkit 的 array，美观输出多行
    all_array = array()
    for dep in deps_set.keys():
        all_array.append(dep)
    all_array.multiline(True)

    opt_deps["all"] = all_array

    # 写回
    with open(PYPROJECT_FILE, "w", encoding="utf-8") as f:
        f.write(dumps(doc))

    print(f"已美观更新 all 分组（不包含 dev），当前依赖数：{len(deps_set)}")


if __name__ == "__main__":
    main()
