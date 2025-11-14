"""
group分为default，redis不自动解码；decode，应用层自动解码
不管设置内容是什么类型，redis实际存储的都是对应的字符串字节（除了zset score以float存储）。
设置和判断类操作的返回值，一般都是数字或True/False，不会是字节类型。
获取内容的操作，返回值类型通常取决于 decode_responses 的配置，但像 zset 的 score 这类本质就是数值的字段，获取时总会以 float 类型返回而不是 str/bytes。
"""

import pytest


# ======================测试string======================
@pytest.mark.parametrize("group", ["default", "decode"])
@pytest.mark.parametrize("my_decode_responses", [True, False])
async def test_redis_string(my_decode_responses, group):
    from smartutils.infra import RedisManager

    mgr = RedisManager()
    if group == "decode":
        # redis解码开启时，assert需要判断解码时的情况
        my_decode_responses = True

    @mgr.use(group)
    async def func():
        cli = mgr.curr
        key = "pytest:getattr:string"
        if not my_decode_responses:
            key += ":no:decode"
        assert cli is not None
        val = await cli.delete(key)

        # 设置字符串
        val = await cli.set(key, "123", ex=10, my_decode_responses=my_decode_responses)
        assert val == 1
        val = await cli.get(key, my_decode_responses=my_decode_responses)
        assert val == ("123" if my_decode_responses else b"123")
        val = await cli.getrange(key, 1, 1, my_decode_responses=my_decode_responses)
        assert val == ("2" if my_decode_responses else b"2")
        val = await cli.incr(key, my_decode_responses=my_decode_responses)
        assert val == 124
        val = await cli.get(key, my_decode_responses=my_decode_responses)
        assert val == ("124" if my_decode_responses else b"124")

        # 设置数字
        val = await cli.set(key, 123, ex=10, my_decode_responses=my_decode_responses)
        assert val == 1
        val = await cli.get(key, my_decode_responses=my_decode_responses)
        assert val == ("123" if my_decode_responses else b"123")
        val = await cli.incr(key, my_decode_responses=my_decode_responses)
        assert val == 124
        val = await cli.get(key, my_decode_responses=my_decode_responses)
        assert val == ("124" if my_decode_responses else b"124")
        val = await cli.decr(key, my_decode_responses=my_decode_responses)
        assert val == 123
        val = await cli.get(key, my_decode_responses=my_decode_responses)
        assert val == ("123" if my_decode_responses else b"123")

        # 查询替换
        val = await cli.getset(key, 456, my_decode_responses=my_decode_responses)
        assert val == ("123" if my_decode_responses else b"123")
        val = await cli.get(key, my_decode_responses=my_decode_responses)
        assert val == ("456" if my_decode_responses else b"456")

        val = await cli.delete(key, my_decode_responses=my_decode_responses)
        assert val == 1

    await func()


# ======================测试hash======================
@pytest.mark.parametrize("group", ["default", "decode"])
@pytest.mark.parametrize("my_decode_responses", [True, False])
async def test_redis_hash(my_decode_responses, group):
    from smartutils.infra import RedisManager

    mgr = RedisManager()

    if group == "decode":
        # redis解码开启时，assert需要判断解码时的情况
        my_decode_responses = True

    @mgr.use(group)
    async def func():
        cli = mgr.curr
        key = "pytest:getattr:hash:no:decode"
        if not my_decode_responses:
            key += ":no:decode"
        assert cli is not None
        await cli.delete(key)

        val = await cli.hset(key, "a", 1, my_decode_responses=my_decode_responses)
        assert val == 1
        val = await cli.hget(key, "a", my_decode_responses=my_decode_responses)
        assert val == ("1" if my_decode_responses else b"1")
        val = await cli.hset(
            key, mapping={"a": 2, "b": 3, 1: 4}, my_decode_responses=my_decode_responses
        )
        assert val == 2

        val = await cli.hkeys(key, my_decode_responses=my_decode_responses)
        assert val == (["a", "b", "1"] if my_decode_responses else [b"a", b"b", b"1"])
        val = await cli.hmget(key, "a", 1, my_decode_responses=my_decode_responses)
        assert val == (["2", "4"] if my_decode_responses else [b"2", b"4"])
        val = await cli.hexists(key, "a", my_decode_responses=my_decode_responses)
        assert val is True
        val = await cli.hexists(key, 1, my_decode_responses=my_decode_responses)
        assert val is True
        val = await cli.hgetall(key, my_decode_responses=my_decode_responses)
        assert val == (
            {"1": "4", "a": "2", "b": "3"}
            if my_decode_responses
            else {b"1": b"4", b"a": b"2", b"b": b"3"}
        )
        val = await cli.hdel(key, "a", my_decode_responses=my_decode_responses)
        assert val == 1
        val = await cli.hget(key, "a", my_decode_responses=my_decode_responses)
        assert val is None
        val = await cli.hgetall(key, my_decode_responses=my_decode_responses)
        assert val == (
            {"1": "4", "b": "3"} if my_decode_responses else {b"1": b"4", b"b": b"3"}
        )

        val = await cli.delete(key, my_decode_responses=my_decode_responses)
        assert val == 1

    await func()


# ======================测试list======================
@pytest.mark.parametrize("group", ["default", "decode"])
@pytest.mark.parametrize("my_decode_responses", [True, False])
async def test_redis_list(my_decode_responses, group):
    from smartutils.infra import RedisManager

    mgr = RedisManager()

    if group == "decode":
        # redis解码开启时，assert需要判断解码时的情况
        my_decode_responses = True

    @mgr.use(group)
    async def test():
        cli = mgr.curr
        key = "pytest:getattr:list"
        if not my_decode_responses:
            key += ":no:decode"
        assert cli is not None
        await cli.delete(key, my_decode_responses=my_decode_responses)

        val = await cli.rpush(
            key, "a", "b", 3, 4, my_decode_responses=my_decode_responses
        )
        assert val == 4
        val = await cli.lpush(key, "e", "f", my_decode_responses=my_decode_responses)
        assert val == 6
        val = await cli.lindex(key, 1, my_decode_responses=my_decode_responses)
        assert val == ("e" if my_decode_responses else b"e")
        val = await cli.lrange(key, 1, 4, my_decode_responses=my_decode_responses)
        assert val == (
            ["e", "a", "b", "3"] if my_decode_responses else [b"e", b"a", b"b", b"3"]
        )
        llen = await cli.llen(key, my_decode_responses=my_decode_responses)
        assert llen == 6
        val = await cli.rpop(key, my_decode_responses=my_decode_responses)
        assert val == ("4" if my_decode_responses else b"4")
        llen = await cli.llen(key, my_decode_responses=my_decode_responses)
        assert llen == 5
        val = await cli.lpop(key, my_decode_responses=my_decode_responses)
        assert val == ("f" if my_decode_responses else b"f")
        llen = await cli.llen(key, my_decode_responses=my_decode_responses)
        assert llen == 4
        val = await cli.rpop(key, 3, my_decode_responses=my_decode_responses)
        assert val == (["3", "b", "a"] if my_decode_responses else [b"3", b"b", b"a"])

        val = await cli.delete(key, my_decode_responses=my_decode_responses)
        assert val == 1

    await test()


# ======================测试set======================
@pytest.mark.parametrize("group", ["default", "decode"])
@pytest.mark.parametrize("my_decode_responses", [True, False])
async def test_redis_set(my_decode_responses, group):
    from smartutils.infra import RedisManager

    mgr = RedisManager()

    if group == "decode":
        # redis解码开启时，assert需要判断解码时的情况
        my_decode_responses = True

    @mgr.use(group)
    async def test():
        cli = mgr.curr
        key = "pytest:getattr:set"
        key2 = key + ":2"
        if not my_decode_responses:
            key += ":no:decode"
            key2 += ":no:decode"
        await cli.delete(key)
        await cli.delete(key2)
        # print(111111, key, key2)
        val = await cli.sadd(key, "a", 1, "a", my_decode_responses=my_decode_responses)
        assert val == 2
        val = await cli.sadd(
            key2, "b", 1, 2, "2", "1", my_decode_responses=my_decode_responses
        )
        assert val == 3

        val = await cli.scard(key, my_decode_responses=my_decode_responses)
        assert val == 2
        val = await cli.scard(key2, my_decode_responses=my_decode_responses)
        assert val == 3

        val = await cli.smembers(key, my_decode_responses=my_decode_responses)
        assert val == ({"a", "1"} if my_decode_responses else {b"a", b"1"})
        val = await cli.smembers(key2, my_decode_responses=my_decode_responses)
        assert val == ({"b", "1", "2"} if my_decode_responses else {b"b", b"1", b"2"})

        val = await cli.sdiff(key, key2, my_decode_responses=my_decode_responses)
        assert val == ({"a"} if my_decode_responses else {b"a"})
        val = await cli.sdiff(key2, key, my_decode_responses=my_decode_responses)
        assert val == ({"2", "b"} if my_decode_responses else {b"2", b"b"})

        val = await cli.sinter(key, key2, my_decode_responses=my_decode_responses)
        assert val == ({"1"} if my_decode_responses else {b"1"})

        val = await cli.srem(key, "a", my_decode_responses=my_decode_responses)
        assert val == 1
        count2 = await cli.scard(key, my_decode_responses=my_decode_responses)
        assert count2 == 1

        val = await cli.srem(key2, 2, my_decode_responses=my_decode_responses)
        assert val == 1
        count2 = await cli.scard(key2, my_decode_responses=my_decode_responses)
        assert count2 == 2
        val = await cli.srem(key2, "2", my_decode_responses=my_decode_responses)
        assert val == 0
        count2 = await cli.scard(key2, my_decode_responses=my_decode_responses)
        assert count2 == 2

        val = await cli.delete(key, my_decode_responses=my_decode_responses)
        assert val == 1
        val = await cli.delete(key2, my_decode_responses=my_decode_responses)
        assert val == 1

    await test()


# ======================测试zset======================
@pytest.mark.parametrize("group", ["default", "decode"])
@pytest.mark.parametrize("my_decode_responses", [True, False])
async def test_redis_zset_int(my_decode_responses, group):
    from smartutils.infra import RedisManager

    mgr = RedisManager()

    if group == "decode":
        # redis解码开启时，assert需要判断解码时的情况
        my_decode_responses = True

    @mgr.use(group)
    async def test():
        cli = mgr.curr
        key = "pytest:getattr:zset:int"
        if not my_decode_responses:
            key += ":no:decode"
        await cli.delete(key, my_decode_responses=my_decode_responses)

        # zset一次添加一个
        val = await cli.zadd(key, {"a": 20}, my_decode_responses=my_decode_responses)
        assert val == 1
        assert await cli.zcard(key, my_decode_responses=my_decode_responses) == 1
        # zset一次添加两个
        val = await cli.zadd(
            key, {"b": 30, 1: 10}, my_decode_responses=my_decode_responses
        )
        assert val == 2
        assert await cli.zcard(key, my_decode_responses=my_decode_responses) == 3

        # key为数字时，redis其实存的字符串
        val = await cli.zscore(key, "1", my_decode_responses=my_decode_responses)
        assert isinstance(val, float)
        assert val == 10
        val = await cli.zscore(key, 1, my_decode_responses=my_decode_responses)
        assert isinstance(val, float)
        assert val == 10

        # 排序输出
        val = await cli.zrevrange(key, 0, -1, my_decode_responses=my_decode_responses)
        assert val == (["b", "a", "1"] if my_decode_responses else [b"b", b"a", b"1"])
        val = await cli.zrevrange(
            key, 0, -1, withscores=True, my_decode_responses=my_decode_responses
        )
        assert val == (
            [("b", 30.0), ("a", 20.0), ("1", 10.0)]
            if my_decode_responses
            else [(b"b", 30.0), (b"a", 20.0), (b"1", 10.0)]
        )

        # 获取区间内的元素
        # 获取0-30内的元素
        val = await cli.zrangebyscore(
            key, 0, 30, my_decode_responses=my_decode_responses
        )
        # 从小到大返回
        assert val == (["1", "a", "b"] if my_decode_responses else [b"1", b"a", b"b"])
        # 所有区间
        val = await cli.zrangebyscore(
            key, "-inf", "+inf", my_decode_responses=my_decode_responses
        )
        # 从小到大返回
        assert val == (["1", "a", "b"] if my_decode_responses else [b"1", b"a", b"b"])
        # 获取10-11内的元素
        val = await cli.zrangebyscore(
            key, 10, 11, my_decode_responses=my_decode_responses
        )
        assert val == (["1"] if my_decode_responses else [b"1"])

        # 弹出最大分数元素，默认带分数
        val = await cli.zpopmax(key, 1, my_decode_responses=my_decode_responses)
        assert val == ([("b", 30.0)] if my_decode_responses else [(b"b", 30.0)])

        # 删除所有元素后，验证为空
        await cli.zrem(key, "a", "b", "1", my_decode_responses=my_decode_responses)
        val = await cli.zrangebyscore(
            key, 0, 30, my_decode_responses=my_decode_responses
        )
        assert not val

        # 前面的zset元素清空，zset自动清除
        val = await cli.delete(key, my_decode_responses=my_decode_responses)
        assert val == 0

    await test()


@pytest.mark.parametrize("group", ["default", "decode"])
@pytest.mark.parametrize("my_decode_responses", [True, False])
async def test_redis_zset_float(my_decode_responses, group):
    from smartutils.infra import RedisManager

    mgr = RedisManager()

    if group == "decode":
        # redis解码开启时，assert需要判断解码时的情况
        my_decode_responses = True

    @mgr.use(group)
    async def test():
        cli = mgr.curr
        key = "pytest:getattr:zset:float"
        if not my_decode_responses:
            key += ":no:decode"
        await cli.delete(key, my_decode_responses=my_decode_responses)

        # 测试浮点分数
        val = await cli.zadd(
            key, {"c": 10.5, "d": 10.7}, my_decode_responses=my_decode_responses
        )
        val = await cli.zscore(key, "c", my_decode_responses=my_decode_responses)
        assert isinstance(val, float)
        assert val == 10.5

        # 测试顺序
        val = await cli.zrevrange(key, 0, -1, my_decode_responses=my_decode_responses)
        assert val == (["d", "c"] if my_decode_responses else [b"d", b"c"])

        # 弹出最大分数元素，默认带分数
        val = await cli.zpopmax(key, 1, my_decode_responses=my_decode_responses)
        assert val == ([("d", 10.7)] if my_decode_responses else [(b"d", 10.7)])

        val = await cli.delete(key, my_decode_responses=my_decode_responses)
        assert val == 1, "delete zset failed"

    await test()


@pytest.mark.parametrize("group", ["default", "decode"])
@pytest.mark.parametrize("my_decode_responses", [True, False])
async def test_redis_zset_str_mix(my_decode_responses, group):
    from smartutils.infra import RedisManager

    mgr = RedisManager()

    if group == "decode":
        # redis解码开启时，assert需要判断解码时的情况
        my_decode_responses = True

    @mgr.use(group)
    async def test():
        cli = mgr.curr
        key = "pytest:getattr:zset:str:mix"
        if not my_decode_responses:
            key += ":no:decode"
        await cli.delete(key, my_decode_responses=my_decode_responses)

        val = await cli.zadd(
            key,
            {"e": "10.9", "g": 10.1},
            my_decode_responses=my_decode_responses,
        )
        val = await cli.zscore(key, "e", my_decode_responses=my_decode_responses)
        assert isinstance(val, float), "e score should be float"
        assert val == 10.9
        val = await cli.zscore(key, "g", my_decode_responses=my_decode_responses)
        assert isinstance(val, float)
        assert val == 10.1

        # 测试顺序
        val = await cli.zrevrange(key, 0, -1, my_decode_responses=my_decode_responses)
        assert val == (["e", "g"] if my_decode_responses else [b"e", b"g"])

        # 弹出最大分数元素
        val = await cli.zpopmax(key, 1, my_decode_responses=my_decode_responses)
        assert val == ([("e", 10.9)] if my_decode_responses else [(b"e", 10.9)])

        val = await cli.delete(key, my_decode_responses=my_decode_responses)
        assert val == 1

    await test()


# @pytest.mark.parametrize("group", ["default", "decode"])
# @pytest.mark.parametrize("my_decode_responses", [True, False])
# async def test_redis_zset_score_str_invalid(my_decode_responses, group):
#     from smartutils.infra import RedisManager

#     mgr = RedisManager()

#     if group == "decode":
#         # redis解码开启时，assert需要判断解码时的情况
#         my_decode_responses = True

#     @mgr.use(group)
#     async def test():
#         cli = mgr.curr
#         key = "pytest:getattr:zset:str:invalid"
#         if not my_decode_responses:
#             key += ":no:decode"
#         await cli.delete(key, my_decode_responses=my_decode_responses)

#         from smartutils.error.sys import CacheError

#         # 测试非法字符串分数
#         with pytest.raises(CacheError) as exec:
#             await cli.zadd(
#                 key,
#                 {"e": "abc", "f": "def"},
#                 my_decode_responses=my_decode_responses,
#             )
#         assert "value is not a valid float" in str(exec.value)

#         val = await cli.delete(key, my_decode_responses=my_decode_responses)
#         assert val == 1

#     await test()


# ======================测试stream======================
@pytest.mark.parametrize("group", ["default", "decode"])
@pytest.mark.parametrize("my_decode_responses", [True, False])
async def test_redis_stream(my_decode_responses, group):
    from smartutils.infra import RedisManager

    mgr = RedisManager()

    if group == "decode":
        # redis解码开启时，assert需要判断解码时的情况
        my_decode_responses = True

    @mgr.use(group)
    async def test():
        cli = mgr.curr
        key = "pytest:getattr:key"
        group = "pytestgroup"
        await cli.delete(key)

        await cli.safe_q_stream.ensure_stream_and_group(key, group)

        await cli.xadd(key, {"foo": "bar"}, my_decode_responses=my_decode_responses)

        # 确保 group 存在
        async with cli.safe_q_stream.xread_xack(key, group, count=1) as msg_iter:
            assert msg_iter["foo"] == "bar"  # type: ignore

        await cli.delete(key)

    await test()
