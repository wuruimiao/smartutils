#!/bin/bash

# 运行测试并收集代码覆盖率

if [[ -n "$1" ]]; then
    if [[ -n "$2" ]]; then
        pytest --cov=smartutils --cov-report=xml "$2" --maxfail=1 -v > test_output.log
        elif [[ "$1" == "real" ]]; then
        pytest --cov=smartutils --cov-report=xml tests tests_real --maxfail=1 -v > test_output.log
    fi
else
    pytest --cov=smartutils --cov-report=xml tests --maxfail=1 -v > test_output.log
fi

status=$?
if [ $status -ne 0 ]; then
    echo "❌ pytest 执行失败，退出。"
    exit $status
else
    echo "✅ pytest 执行成功。"
fi

coverage report -m > test_cover_output.log
coverage html
