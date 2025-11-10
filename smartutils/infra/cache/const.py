from enum import Enum

INCR_DECR_SCRIPT = """
local op = ARGV[1]
local current
if op == 'incr' then
    current = redis.call('incr', KEYS[1])
elseif op == 'decr' then
    current = redis.call('decr', KEYS[1])
else
    return redis.error_reply('unknown op: ' .. op)
end
if ARGV[2] ~= '' then
    redis.call('expire', KEYS[1], ARGV[2])
end
return current
"""
RPOP_ZADD_SCRIPT = """
local msg = redis.call('rpop', KEYS[1])
if msg then
    redis.call('zadd', KEYS[2], ARGV[1], msg)
end
return msg
"""
ZREM_RPUSH_SCRIPT = """
redis.call('ZREM', KEYS[1], ARGV[1])
redis.call('RPUSH', KEYS[2], ARGV[1])
return ARGV[1]
"""
ZPOPMIN_ZADD_SCRIPT = """
local items = redis.call('zpopmin', KEYS[1], 1)
if items and #items > 0 then
    redis.call('zadd', KEYS[2], ARGV[1], items[1])
    return items[1]
end
return nil
"""
ZREM_ZADD_SCRIPT = """
redis.call('zrem', KEYS[1], ARGV[1])
redis.call('zadd', KEYS[2], ARGV[2], ARGV[1])
return ARGV[1]
"""


class LuaName(Enum):
    INCR_DECR = "incr_decr"
    RPOP_ZADD = "rpop_zadd"
    ZREM_RPUSH = "zrem_rpush"
    ZPOPMIN_ZADD = "zpopmin_zadd"
    ZREM_ZADD = "zrem_zadd"


LUAS = {
    LuaName.INCR_DECR: INCR_DECR_SCRIPT,
    LuaName.RPOP_ZADD: RPOP_ZADD_SCRIPT,
    LuaName.ZREM_RPUSH: ZREM_RPUSH_SCRIPT,
    LuaName.ZPOPMIN_ZADD: ZPOPMIN_ZADD_SCRIPT,
    LuaName.ZREM_ZADD: ZREM_ZADD_SCRIPT,
}
