from sanic import Sanic
from sanic.log import logger
from asyncio import sleep
from aioredis import Redis
from aioredis.client import Pipeline
from .lua import transaction
from .errors import RateLimitExceeded


async def client_list(redis: Redis, redis_flag: dict, app: Sanic):
    while True:
        await sleep(8)
        logger.debug(f"redis client {[client['name'] for client in await redis.client_list()]}")
        logger.debug(redis_flag)
        logger.debug(f"tasks {len([task for task in app.tasks])}")


def key_func_g(func, request): return f"{func.__name__}_{request.method}"


async def once(key: str, redis: Redis, limit: int, splitNum: int):
    if not await redis.exists(key):
        await redis.rpush(key, 0)
    window = int((await redis.lindex(key, -1)).decode())
    if window >= limit:
        if await redis.llen(key) >= splitNum:
            #    return RateLimitExceeded()
            raise RateLimitExceeded()
        await redis.rpushx(key, 0)
        window = 0
    window += 1
    await redis.lset(key, -1, window)


async def pop(app: Sanic, key: str, redis: Redis, recovery_frequency: float):
    await redis.client_setname(key)

    async def _pop(pipe: Pipeline):
        if not await redis.exists(key):
            return
        await pipe.lpop(key)
    while app.ctx.redis_flag[key]:
        await sleep(recovery_frequency)
        # logger.debug(f"pop {await redis.transaction(_pop, key)}")
        # ret = await redis.transaction(_pop)

        ret = await redis.evalsha(transaction['pop'], 1, key)
        logger.debug(f"pop {ret}") if ret else None
    await redis.close()


async def purge_tasks(app: Sanic, redis: Redis, windowSize: int):
    redis_flag: dict = app.ctx.redis_flag
    await redis.client_setname('purge_tasks')

    async def _purge_tasks(pipe: Pipeline):
        for key in await redis.smembers('purge_tasks'):
            key = key.decode()
            if not (await redis.exists(key) and await redis.llen(key)):
                await pipe.srem('purge_tasks', key)
                redis_flag[key] = False
                # await app.cancel_task(key, raise_exception=False)
    while redis_flag['purge_tasks']:
        await sleep(windowSize / 1000)
        logger.debug([
            [key, await app.cancel_task(key, raise_exception=False), redis_flag.pop(key)]
            for key in set(redis_flag.keys()) if not redis_flag[key]
        ]) if False in redis_flag.values() else None
        app.purge_tasks()
        if not await redis.exists('purge_tasks'):
            continue
        # keys = [key.decode() for key in await redis.smembers('purge_tasks')]
        # logger.debug(f"purge_tasks {await redis.transaction(_purge_tasks, *keys)}")
        # ret = await redis.transaction(_purge_tasks)

        ret = await redis.evalsha(transaction['purge_tasks'], 0)
        [redis_flag.update({key.decode(): False}) for key in ret]
        logger.debug(f"purge_tasks {ret}") if ret else None
    await redis.close()
