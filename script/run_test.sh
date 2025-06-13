#!/bin/bash

# 运行测试并收集代码覆盖率
pytest --cov=smartutils --cov-report=xml tests tests_real --maxfail=1 -v > test_output.log

coverage report -m > test_cover_output.log
