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
