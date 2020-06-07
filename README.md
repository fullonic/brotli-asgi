# brotli-middleware

`BrotliMiddleware` adds [Brotli](https://github.com/google/brotli) response compression to ASGI applications (Starlette, FastAPI, Quart, etc.). It provides faster and more dense compression than GZip, and can be used as a drop in replacement for the `GZipMiddleware` shipped with Starlette.

**Installation**

```bash
pip install brotli-middleware
```

## Examples

### Starlette

```python
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.middleware import Middleware

from brotli_asgi import BrotliMiddleware

async def homepage(request):
    return JSONResponse({"data": "a" * 4000})

app = Starlette(
  routes=[Route("/", homepage)],
  middleware=[Middleware(BrotliMiddleware)],
)
```

### FastAPI

```python
from fastapi import FastAPI
from brotli_asgi import BrotliMiddleware

app = FastAPI()
app.add_middleware(BrotliMiddleware)

@app.get("/")
def home() -> dict:
    return {"data": "a" * 4000}
```

## API Reference

**Overview**

```python
app.add_middleware(
  BrotliMiddleware, quality=4, mode="text", lgwin=22, lgblock=0, minimum_size=400,
)
```

**Parameters**:

- _(Optional)_ `quality`: Controls the compression speed vs compression density tradeoff. The higher the quality, the slower the compression. Range is 0 to 11.
- _(Optional)_ `mode`: The compression mode can be: `"generic"` (default), `"text"` (for UTF-8 format text input) or `"font"` (for WOFF 2.0).
- _(Optional)_ `lgwin`: Base 2 logarithm of the sliding window size. Range is 10 to 24.
- _(Optional)_ `lgblock`: Base 2 logarithm of the maximum input block size. Range is 16 to 24. If set to 0, the value will be set based on the quality.
- _(Optional)_ `minimum_size`: Only compress responses that are bigger than this value in bytes.

## Performance

To better understand the benefits of Brotli over GZip, please read the great article written by Akamai team, [Understanding Brotli's Potential](https://blogs.akamai.com/2016/02/understanding-brotlis-potential.html), where detailed information and benchmarks are provided.

A simple comparative example using Python `sys.getsizof()` and `timeit`:

```python
# ipython console
import sys
import gzip
import brotli

text = b"*" * 100_000_000
%timeit brotli.compress(text, quality=4)
# 606 ms ± 254 µs per loop (mean ± std. dev. of 7 runs, 1 loop each)
sys.getsizeof(brotli.compress(text, quality=4))
# 4761
%timeit gzip.compress(text, compresslevel=6)
# 733 ms ± 6.59 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
sys.getsizeof(gzip.compress(text, compresslevel=6))
# 97255
```

## Compatibility

According to [caniuse.com](https://caniuse.com/#feat=brotli), Brotli is supported by all major browsers with a global use of _94%_.
