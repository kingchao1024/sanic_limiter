# sanic_limiter

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
from sanic.response import text
from limiter_for_sanic import CounterSildeWindowLimiter

app = Sanic(__name__)
limiter = CounterSildeWindowLimiter()

@app.get('/')
@limiter.limit()
async def index(request: Request):
    return text('HELLO')

app.run(host="0.0.0.0", port=5000, dev=True)
```

Points Used
===========
```
Redis transactions
Redis list
Sanic background tasks
```