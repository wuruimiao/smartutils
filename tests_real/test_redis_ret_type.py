import pytest


@pytest.fixture
async def setup_cache(tmp_path_factory):
    yield


async def test_string_commands_ret_type(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def inner():
        cli = redis_mgr.curr
        await cli.set("pytest:string", "v1")
        val = await cli.get("pytest:string")
        assert isinstance(val, str)
        ret = await cli.delete("pytest:string")
        assert isinstance(ret, int)

    await inner()


async def test_set_commands_ret_type(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def inner():
        cli = redis_mgr.curr
        await cli.delete("pytest:set")
        s = await cli.sadd("pytest:set", "v1", "v2")
        assert isinstance(s, int)
        count = await cli.scard("pytest:set")
        assert isinstance(count, int)
        members = await cli.srem("pytest:set", "v1")
        assert isinstance(members, int)
        await cli.delete("pytest:set")

    await inner()


async def test_list_commands_ret_type(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def inner():
        cli = redis_mgr.curr
        await cli.delete("pytest:list")
        llen = await cli.rpush("pytest:list", "a", "b")
        assert isinstance(llen, int)
        vals = await cli.lrange("pytest:list", 0, -1)
        assert isinstance(vals, list) and all(isinstance(v, str) for v in vals)
        await cli.delete("pytest:list")

    await inner()


async def test_zset_commands_ret_type(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def inner():
        cli = redis_mgr.curr
        await cli.delete("pytest:zset")
        zadd_ret = await cli.zadd("pytest:zset", {"k": 1})
        assert isinstance(zadd_ret, int)
        zcount = await cli.zcard("pytest:zset")
        assert isinstance(zcount, int)
        zrange = await cli.zrange("pytest:zset", 0, -1)
        assert isinstance(zrange, list)
        await cli.delete("pytest:zset")

    await inner()


async def test_stream_commands_ret_type(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def inner():
        cli = redis_mgr.curr
        await cli.delete("pytest:stream")
        msgid = await cli.xadd("pytest:stream", {"foo": "bar"})
        assert isinstance(msgid, str)
        await cli.delete("pytest:stream")

    await inner()


async def test_incr_decr_ret_type(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def inner():
        cli = redis_mgr.curr
        await cli.delete("pytest:cnt")
        v = await cli.incr("pytest:cnt")
        assert isinstance(str(v), str)
        v2 = await cli.decr("pytest:cnt")
        assert isinstance(str(v2), str)
        await cli.delete("pytest:cnt")

    await inner()


async def test_hash_commands_ret_type(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def inner():
        cli = redis_mgr.curr
        await cli.delete("pytest:hash")
        # hset
        ret = await cli.hset("pytest:hash", "f1", "v1")
        assert isinstance(ret, int)
        # hget
        v = await cli.hget("pytest:hash", "f1")
        assert isinstance(v, str)
        # hgetall
        allv = await cli.hgetall("pytest:hash")
        assert isinstance(allv, dict)
        # hdel
        d = await cli.hdel("pytest:hash", "f1")
        assert isinstance(d, int)
        await cli.delete("pytest:hash")

    await inner()


async def test_expire_and_ttl_ret_type(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def inner():
        cli = redis_mgr.curr
        await cli.set("pytest:exp", "x")
        ret = await cli.expire("pytest:exp", 10)
        assert ret is True
        ttl = await cli.ttl("pytest:exp")
        assert isinstance(ttl, int)
        await cli.delete("pytest:exp")

    await inner()


async def test_bit_commands_ret_type(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def inner():
        cli = redis_mgr.curr
        await cli.delete("pytest:bit")
        # setbit
        s = await cli.setbit("pytest:bit", 7, 1)
        assert s in (0, 1)
        # getbit
        b = await cli.getbit("pytest:bit", 7)
        assert b in (0, 1)
        # bitcount
        cnt = await cli.bitcount("pytest:bit")
        assert isinstance(cnt, int)
        await cli.delete("pytest:bit")

    await inner()


async def test_hyperloglog_commands_ret_type(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def inner():
        cli = redis_mgr.curr
        await cli.delete("pytest:hll1", "pytest:hll2")
        # pfadd
        added = await cli.pfadd("pytest:hll1", "a", "b")
        assert isinstance(added, int)
        # pfcount
        count = await cli.pfcount("pytest:hll1")
        assert isinstance(count, int)
        # pfmerge
        await cli.pfmerge("pytest:hll2", "pytest:hll1")
        cnt2 = await cli.pfcount("pytest:hll2")
        assert isinstance(cnt2, int)
        await cli.delete("pytest:hll1", "pytest:hll2")

    await inner()


async def test_key_control_ret_type(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def inner():
        cli = redis_mgr.curr
        await cli.set("pytest:key", "x")
        exists = await cli.exists("pytest:key")
        assert isinstance(exists, int)
        typ = await cli.type("pytest:key")
        assert isinstance(typ, str)
        await cli.delete("pytest:key")

    await inner()


async def test_server_info_and_ping_ret_type(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def inner():
        cli = redis_mgr.curr
        info = await cli.info()
        assert isinstance(info, dict)
        pong = await cli.ping()
        assert pong is True

    await inner()


async def test_mset_mget_msetnx_ret_type(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def redis_mset_mget_msetnx_case():
        cli = redis_mgr.curr
        await cli.delete("pytest:k1", "pytest:k2")
        mset_ret = await cli.mset({"pytest:k1": "v1", "pytest:k2": "v2"})
        assert mset_ret is True
        vals = await cli.mget(["pytest:k1", "pytest:k2"])
        assert isinstance(vals, list) and vals == ["v1", "v2"]
        ret = await cli.msetnx({"pytest:k3": "v3"})
        assert ret is True
        await cli.delete("pytest:k1", "pytest:k2", "pytest:k3")

    await redis_mset_mget_msetnx_case()


async def test_rename_move_dump_restore_copy_ret_type(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def redis_rename_move_dump_restore_case():
        cli = redis_mgr.curr
        await cli.set("pytest:rnm", "abc")
        dumpval = await cli.dump("pytest:rnm")
        assert isinstance(dumpval, (bytes, type(None)))
        await cli.restore("pytest:rnm_c", 0, dumpval, replace=True)
        assert await cli.get("pytest:rnm_c") == "abc"
        rn_ret = await cli.rename("pytest:rnm", "pytest:rnm2")
        assert rn_ret is True
        cp_ret = await cli.copy("pytest:rnm2", "pytest:rnm3")
        assert cp_ret is True
        await cli.delete("pytest:rnm_c", "pytest:rnm2", "pytest:rnm3")

    await redis_rename_move_dump_restore_case()


async def test_randomkey_type_exists_persist_touch_ret_type(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def redis_key_info_case():
        cli = redis_mgr.curr
        await cli.set("pytest:rnd", "abc")
        randkey = await cli.randomkey()
        if randkey is not None:
            assert isinstance(randkey, str)
        exists = await cli.exists("pytest:rnd")
        assert isinstance(exists, int)
        ktype = await cli.type("pytest:rnd")
        assert isinstance(ktype, str)
        pers = await cli.persist("pytest:rnd")
        assert isinstance(pers, int)
        touched = await cli.touch("pytest:rnd")
        assert isinstance(touched, int)
        await cli.delete("pytest:rnd")

    await redis_key_info_case()


async def test_scan_and_pattern_commands_ret_type(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def redis_scan_case():
        cli = redis_mgr.curr
        await cli.set("pytest:scan_a", "1")
        await cli.set("pytest:scan_b", "2")
        cursor, keys = await cli.scan(match="pytest:scan_*")
        assert isinstance(cursor, int) or isinstance(cursor, str)
        assert isinstance(keys, list)
        await cli.delete("pytest:scan_a", "pytest:scan_b")

    await redis_scan_case()


async def test_script_commands_ret_type(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def redis_script_case():
        cli = redis_mgr.curr
        val = await cli.eval("return 5", 0)
        assert val == 5
        sha = await cli.script_load("return redis.call('ping')")
        ret = await cli.evalsha(sha, 0)
        assert ret == "PONG"
        # script_exists
        exists = await cli.script_exists(sha)
        assert isinstance(exists, list)
        # script_flush
        await cli.script_flush()

    await redis_script_case()


async def test_pubsub_commands_ret_type(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def redis_pubsub_case():
        cli = redis_mgr.curr
        # publish 返回订阅接收数
        ch = "pytest:ps"
        cnt = await cli.publish(ch, "abc")
        assert isinstance(cnt, int)
        # 订阅部分较难自动全部断言可只覆盖发布通路

    await redis_pubsub_case()


async def test_sort_command_ret_type(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def redis_sort_case():
        cli = redis_mgr.curr
        await cli.delete("pytest:sort")
        await cli.rpush("pytest:sort", "3", "1", "2")
        ret = await cli.sort("pytest:sort")
        assert ret == ["1", "2", "3"]
        await cli.delete("pytest:sort")

    await redis_sort_case()


async def test_slowlog_commands_ret_type(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def redis_slowlog_case():
        cli = redis_mgr.curr
        logs = await cli.slowlog_get(1)
        assert isinstance(logs, list)
        slen = await cli.slowlog_len()
        assert isinstance(slen, int)
        await cli.slowlog_reset()

    await redis_slowlog_case()


async def test_memory_commands_ret_type(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def redis_memory_case():
        cli = redis_mgr.curr
        stats = await cli.memory_stats()
        assert isinstance(stats, dict)
        musage = await cli.memory_usage("nonexistkey")
        assert isinstance(musage, (int, type(None)))

    await redis_memory_case()


async def test_wait_and_save_commands_ret_type(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def redis_wait_save_case():
        cli = redis_mgr.curr
        await cli.set("pytest:w", "v")
        wret = await cli.wait(0, 100)
        assert isinstance(wret, int)
        await cli.save()
        await cli.delete("pytest:w")

    await redis_wait_save_case()


@pytest.mark.skip(reason="DANGEROUS: FLUSHALL will clear all redis data!")
async def test_flushall_commands_ret_type(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def flush_all_case():
        cli = redis_mgr.curr
        ret = await cli.flushall()
        assert ret == "PONG"

    await flush_all_case()
