#!/bin/bash

# 运行测试并收集代码覆盖率

if [[ "$1" == "real" ]]; then
    if [[ -n "$2" ]]; then
        pytest --cov=smartutils --cov-report=xml "$2" --maxfail=1 -v > test_output.log
    else
        pytest --cov=smartutils --cov-report=xml tests tests_real --maxfail=1 -v > test_output.log
    fi
else
    pytest --cov=smartutils --cov-report=xml tests --maxfail=1 -v > test_output.log
fi

coverage report -m > test_cover_output.log
coverage html
