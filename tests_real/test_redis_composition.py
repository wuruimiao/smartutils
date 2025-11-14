import pytest


@pytest.mark.parametrize("group", ["default", "decode"])
async def test_incr_and_decr(group):
    from smartutils.infra import RedisManager

    mgr = RedisManager()

    @mgr.use(group)
    async def test():
        cli = mgr.curr
        key = "pytest:composition:safe:str"
        await cli.delete(key)

        val = await cli.safe_str.incr(key)
        assert isinstance(val, int)
        assert int(val) == 1
        val = await cli.safe_str.incr(key)
        assert isinstance(val, int)
        assert int(val) == 2
        val = await cli.safe_str.decr(key)
        assert isinstance(val, int)
        assert int(val) == 1

        await cli.delete(key)

    await test()


@pytest.mark.parametrize("group", ["default", "decode"])
async def test_safe_queue_by_list(group):
    from smartutils.infra import RedisManager

    mgr = RedisManager()

    @mgr.use(group)
    async def test():
        cli = mgr.curr
        ready = "pytest:composition:list_ready"
        pending = "pytest:composition:zset_pending"
        await cli.delete(ready, pending)

        # 先准备任务
        assert await cli.safe_q_list.enqueue_task(ready, ("task1", 2))

        # 用 safe_rpop_zadd 弹出一个任务并放入 zset_pending
        async with cli.safe_q_list.fetch_task_ctx(ready, pending) as msg:
            # 先进先出，应该弹出 task1
            assert msg == "task1"
            # zset_pending 应该有这个任务
            members = await cli.zrange(pending, 0, -1)
            assert msg in members
            assert await cli.safe_q_list.is_task_pending(pending, msg)
        # 弹出后 zset_pending 已被清理
        assert not await cli.safe_q_list.is_task_pending(pending, msg)
        members = await cli.zrange(pending, 0, -1)
        assert msg not in members

        # 应该弹出2
        async with cli.safe_q_list.fetch_task_ctx(ready, pending, priority=1111) as msg:
            assert msg == "2"
            # taskA 应该在 pending
            members = await cli.zrange(pending, 0, -1)
            assert msg in members
            assert await cli.safe_q_list.is_task_pending(pending, msg)
            assert await cli.zscore(pending, msg) == 1111

        # 再手动放一个任务到 zset_pending，测试 requeue_task
        msg = "task3"
        await cli.zadd(pending, {msg: 100})
        assert await cli.safe_q_list.requeue_task(ready, pending, msg)
        # task3 应该在 list_ready
        vals = await cli.lrange(ready, 0, -1)
        assert msg in vals
        # task3 应该不在 zset_pending
        assert not await cli.safe_q_list.is_task_pending(pending, msg)
        members = await cli.zrange(pending, 0, -1)
        assert msg not in members

        await cli.delete(ready, pending)

    await test()


@pytest.mark.parametrize("group", ["default", "decode"])
async def test_safe_queue_by_zset(group):
    from smartutils.infra import RedisManager

    mgr = RedisManager()

    @mgr.use(group)
    async def test():
        cli = mgr.curr
        ready = "pytest:composition:zset_ready"
        pending = "pytest:composition:zset_pending2"
        await cli.delete(ready, pending)

        # 准备任务
        assert await cli.safe_q_zset.enqueue_task(ready, {"taskA": 2, "taskB": 1})
        # 应该弹出 score 最大的 taskA
        async with cli.safe_q_zset.fetch_task_ctx(ready, pending) as msg:
            assert msg == "taskA"
            # taskA 应该在 pending
            members = await cli.zrange(pending, 0, -1)
            assert msg in members
            assert await cli.safe_q_zset.is_task_pending(pending, msg)
            # 优先级应该是原始的 score 2
            assert await cli.zscore(pending, msg) == 2
        # 弹出后 pending 已被清理
        members = await cli.zrange(pending, 0, -1)
        assert msg not in members
        assert not await cli.safe_q_zset.is_task_pending(pending, msg)

        # 应该弹出 score 次大的 taskB，同时判断优先级
        async with cli.safe_q_zset.fetch_task_ctx(ready, pending, priority=1111) as msg:
            assert msg == "taskB"
            # taskA 应该在 pending
            members = await cli.zrange(pending, 0, -1)
            assert msg in members
            assert await cli.safe_q_zset.is_task_pending(pending, msg)
            assert await cli.zscore(pending, msg) == 1111
        # 弹出后 pending 已被清理
        members = await cli.zrange(pending, 0, -1)
        assert msg not in members, "pending should be empty after context exit"
        assert not await cli.safe_q_zset.is_task_pending(pending, msg)

        # 再把 taskC 放到 pending，safe_zrem_zadd 归还到 ready
        msg = "taskC"
        await cli.zadd(pending, {msg: 99})
        assert await cli.safe_q_zset.requeue_task(ready, pending, msg, 5)
        # taskC 应该在 ready，score 为 5
        ready_members = await cli.zrange(ready, 0, -1, withscores=True)
        found = [x for x in ready_members if x[0] == msg and x[1] == 5.0]
        assert found, f"{msg} with score 5 not found in ready"
        # taskC 应该不在 pending
        pending_members = await cli.zrange(pending, 0, -1)
        assert (
            msg not in pending_members
        ), f"{msg} should not be in pending after requeue"
        assert not await cli.safe_q_zset.is_task_pending(pending, msg)

        # 再把 taskD 放到 pending，safe_zrem_zadd 归还到 ready
        msg = "taskD"
        await cli.zadd(pending, {msg: 999})
        assert await cli.safe_q_zset.requeue_task(ready, pending, msg)
        # taskD 应该在 ready，score 为 9999
        ready_members = await cli.zrange(ready, 0, -1, withscores=True)
        found = [x for x in ready_members if x[0] == msg and x[1] == 999.0]
        assert found, "taskD with score 5 not found in ready"
        # taskD 应该不在 pending
        pending_members = await cli.zrange(pending, 0, -1)
        assert (
            msg not in pending_members
        ), f"{msg} should not be in pending after requeue"
        assert not await cli.safe_q_zset.is_task_pending(pending, msg)

        await cli.delete(ready, pending)

    await test()


@pytest.mark.parametrize("group", ["default", "decode"])
async def test_bitmap_util(group):
    """
    真正执行RedisBitmapUtil的端到端测试。
    """

    key = "pytest:composition:bitmap"
    from smartutils.infra.cache.redis import RedisManager

    mgr = RedisManager()

    @mgr.use(group)
    async def biz():
        cli = mgr.curr
        await cli.delete(key)
        assert await cli.bitmap.get_all_set_bits(key) is None

        # 清空，初始应无内容
        await cli.bitmap.set_bit(key, 3, True)
        await cli.bitmap.set_bit(key, 6, True)
        ret3 = await cli.bitmap.get_bit(key, 3)
        ret6 = await cli.bitmap.get_bit(key, 6)
        ret2 = await cli.bitmap.get_bit(key, 2)
        assert ret3 is True
        assert ret6 is True
        assert ret2 is False
        bits = await cli.bitmap.get_all_set_bits(key, max_offset=7)
        assert bits == {3, 6}
        # 关闭一个bit
        await cli.bitmap.set_bit(key, 6, False)
        bits2 = await cli.bitmap.get_all_set_bits(key, max_offset=7)
        assert bits2 == {3}
        # 全部关闭
        await cli.bitmap.set_bit(key, 3, False)
        bits3 = await cli.bitmap.get_all_set_bits(key, max_offset=7)
        assert bits3 == set() or bits3 is None

        await cli.bitmap.set_bit(key, 1, True)
        assert await cli.bitmap.get_all_set_bits(key, max_offset=0) == set()

        assert await cli.delete(key) == 1

    await biz()
