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


class LuaName(Enum):
    INCR_DECR = "incr_decr"
    RPOP_ZADD = "RPOP_ZADD"


LUAS = {
    LuaName.INCR_DECR: INCR_DECR_SCRIPT,
    LuaName.RPOP_ZADD: RPOP_ZADD_SCRIPT,
}
