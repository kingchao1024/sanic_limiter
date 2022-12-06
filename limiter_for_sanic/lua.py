transaction = {
    "once": """
        local key = KEYS[1]
        local limit = tonumber(ARGV[1])
        local splitNum = tonumber(ARGV[2])

        if redis.pcall('exists', key) == 0 then
            redis.pcall('rpush', key, 0)
        end

        local window = tonumber(redis.pcall('lindex', key, -1))

        if window >= limit then
            if tonumber(redis.pcall('llen', key)) >= splitNum then
                return 0
            end
            redis.pcall('rpushx', key, 0)
            window = 0
        end

        window = window + 1

        redis.pcall('lset', key, -1, window)
        redis.pcall('sadd', 'purge_tasks', key)

        return 1
    """,
    "pop": """
        local key = KEYS[1]
        if redis.pcall('exists', key) == 0 then
            return
        end
        return redis.pcall('lpop', key)
    """,
    "purge_tasks": """
        local array = {}
        for i, k in pairs(redis.pcall('smembers', 'purge_tasks')) do
            if redis.pcall('exists', k) == 0 or redis.pcall('llen', k) == 0 then
                redis.pcall('srem', k)
                array[i] = k
            end
        end
        return array
    """
}
