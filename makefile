.PHONY: install update activate publish checktest covweb test updatepyproject

# 安装虚拟环境及依赖
install:
	poetry install

init:
	poetry lock
	poetry install --all-extras

# 更新虚拟环境依赖
update:
	poetry lock
	poetry update

# 激活虚拟环境
activate:
	source $(poetry env info --path)/bin/activate

# 构建并发布包
publish:
	rm -rf dist && poetry publish --build

# 检查重复单元测试函数名
checktest:
	python3 ./script/find_dup_test_name.py

# 启动单元测试覆盖率web服务
covweb:
	cd htmlcov && python -m http.server 8888

# 运行单元测试，real运行正式环境测试，或者测试指定的文件
test:
	poetry run bash script/run_test.sh $(filter-out $@,$(MAKECMDGOALS))

updatepyproject:
	python3 ./script/update_all_extra.py

%:
	@:
