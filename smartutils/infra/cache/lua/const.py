from enum import Enum

INCR_DECR_SCRIPT = """
local op = ARGV[1]
local current
if op == 'incr' then
    current = redis.call('INCR', KEYS[1])
elseif op == 'decr' then
    current = redis.call('DECR', KEYS[1])
else
    return redis.error_reply('unknown op: ' .. op)
end
if ARGV[2] ~= '' then
    redis.call('EXPIRE', KEYS[1], ARGV[2])
end
return current
"""
RPOP_ZADD_SCRIPT = """
local msg = redis.call('RPOP', KEYS[1])
if msg then
    redis.call('ZADD', KEYS[2], ARGV[1], msg)
end
return msg
"""
ZREM_RPUSH_SCRIPT = """
redis.call('ZREM', KEYS[1], ARGV[1])
redis.call('RPUSH', KEYS[2], ARGV[1])
return ARGV[1]
"""
ZPOPMAX_ZADD_SCRIPT = """
local items = redis.call('ZPOPMAX', KEYS[1], 1)
if items and #items > 0 then
    local score = ARGV[1]
    if not score or score == '' then
        score = items[2]
    end
    redis.call('ZADD', KEYS[2], score, items[1])
    return items[1]
end
return nil
"""
ZREM_ZADD_SCRIPT = """
local score = ARGV[2]
if not score or score == '' then
    local orig_score = redis.call('ZSCORE', KEYS[2], ARGV[1])
    score = orig_score
end
redis.call('ZREM', KEYS[2], ARGV[1])
redis.call('ZADD', KEYS[1], score, ARGV[1])
return ARGV[1]
"""


class LuaName(Enum):
    INCR_DECR = "incr_decr"
    RPOP_ZADD = "rpop_zadd"
    ZREM_RPUSH = "zrem_rpush"
    ZPOPMAX_ZADD = "zpopmax_zadd"
    ZREM_ZADD = "zrem_zadd"


LUAS = {
    LuaName.INCR_DECR: INCR_DECR_SCRIPT,
    LuaName.RPOP_ZADD: RPOP_ZADD_SCRIPT,
    LuaName.ZREM_RPUSH: ZREM_RPUSH_SCRIPT,
    LuaName.ZPOPMAX_ZADD: ZPOPMAX_ZADD_SCRIPT,
    LuaName.ZREM_ZADD: ZREM_ZADD_SCRIPT,
}
