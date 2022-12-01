from re import split
from sanic import Request
from sanic.log import logger
from functools import wraps
from aioredis.lock import Lock
from aioredis.client import Pipeline
from .bulk import key_func_g, Sanic, once, pop, purge_tasks, RateLimitExceeded, Redis, client_list




class CounterSildeWindowLimiter:
    def __init__(self, app: Sanic=None, key_func=key_func_g, windowSize: int=1000, splitNum: int=5, limit: int=5) -> None:
        self._app = app
        self._key_func = key_func
        self._windowSize = windowSize
        self._splitNum = splitNum
        self._limit = limit
        self._recovery_frequency = windowSize // splitNum / 1000
        self._redis: Redis
        self._lock: Lock
        
        if app:
            self.init_app(app)

    def init_app(self, app: Sanic):
        self._app = app
        self._app_name = app.name
        setattr(app.ctx, 'limiter', self)

        @app.after_server_start
        async def aio_limiter_configure(_app: Sanic):
            logger.debug("[sanic-limiter] connecting")
            self._redis: Redis = _app.ctx.redis
            self._lock = self._redis.lock(f"lock_{self._app_name}")
            setattr(_app.ctx, 'redis_flag', dict({'purge_tasks': True}))
            app.add_task(purge_tasks(_app, self._redis.client(), self._windowSize), name='purge_tasks')
            app.add_task(client_list(self._redis, _app.ctx.redis_flag, _app), name='client_list')

        @app.before_server_stop
        async def close_limiter(_app: Sanic):
            logger.debug("[sanic-limiter] closing")
            _app.ctx.redis_flag['purge_tasks'] = False
            _app.ctx.redis_flag['client_list'] = False
            # await _app.cancel_task('purge_tasks')

    
    def limit(self):
        def _outer(func):
            @wraps(func)
            async def _inner(request: Request, *args, **kwargs):
                key = self._key_func(func, request)
                # lock = await self._lock.acquire(blocking_timeout=5)
                # if not lock:
                #     await self._lock.release()
                #     raise RateLimitExceeded("The lock is busy")
                # status = await once(key, self._redis, self._limit, self._splitNum)
                # if status:
                #     await self._lock.release()
                #     raise status
                # if not self._app.get_task(key, raise_exception=False):
                #     self._app.add_task(pop(key, self._redis, self._recovery_frequency), name=key)
                # await self._redis.sadd('purge_tasks', key)
                # await self._lock.release()
                async def _once(pipe: Pipeline):
                    if not self._app.get_task(key, raise_exception=False):
                        self._app.ctx.redis_flag[key] = True
                        self._app.add_task(pop(self._app, key, self._redis.client(), self._recovery_frequency), name=key)
                    await once(key, self._redis, self._limit, self._splitNum)
                    await pipe.sadd('purge_tasks', key)
                # logger.debug(f"once {await self._redis.transaction(_once, key)}")
                logger.debug(f"once {await self._redis.transaction(_once)}")
                return await func(request, *args, **kwargs)
            return _inner
        return _outer
                


            


    