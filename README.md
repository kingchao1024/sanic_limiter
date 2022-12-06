# sanic_limiter

## Require
```
Python 3.7+
Redis
```

## Sources
```shell
git clone https://github.com/kingchao1024/sanic_limiter.git
```

## Install (Python 3.7+)
```shell
pip install limiter-for-sanic
```

Introduce
===========
    A Sanic current limiter based on the sliding window idea.

Quickstart
===========
Demo for quickstart:
```python
from sanic import Sanic
from aioredis import from_url
from sanic.response import text
from limiter_for_sanic import CounterSildeWindowLimiter

app = Sanic(__name__)
app.config['REDIS'] = 'redis://locahost'
# or
# setattr(app.ctx, 'redis', await from_url('redis://locahost'))
limiter = CounterSildeWindowLimiter(app)

@app.get('/')
@limiter.limit()
async def index(request: Request):
    return text('HELLO')

app.run(host="0.0.0.0", port=5000, dev=True)
```

Points Used
===========
- Redis lua
- Redis list
- Sanic background tasks
- ~~Redis transactions~~