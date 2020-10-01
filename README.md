# brotli-asgi

[![Packaging status](https://img.shields.io/pypi/v/brotli-asgi?color=%2334D058&label=pypi%20package)](https://pypi.org/project/brotli-asgi)
[![CI](https://github.com/fullonic/brotli-asgi/workflows/Tests/badge.svg)](https://github.com/fullonic/brotli-asgi/actions?query=workflow%3ATests)



`BrotliMiddleware` adds [Brotli](https://github.com/google/brotli) response compression to ASGI applications (Starlette, FastAPI, Quart, etc.). It provides faster and more dense compression than GZip, and can be used as a drop in replacement for the `GZipMiddleware` shipped with Starlette.

**Installation**

```bash
pip install brotli-asgi
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
  BrotliMiddleware,
  quality=4,
  mode="text",
  lgwin=22,
  lgblock=0,
  minimum_size=400,
  gzip_fallback=True
)
```

**Parameters**:

- _(Optional)_ `quality`: Controls the compression speed vs compression density tradeoff. The higher the quality, the slower the compression. Range is 0 to 11.
- _(Optional)_ `mode`: The compression mode can be: `"generic"` (default), `"text"` (for UTF-8 format text input) or `"font"` (for WOFF 2.0).
- _(Optional)_ `lgwin`: Base 2 logarithm of the sliding window size. Range is 10 to 24.
- _(Optional)_ `lgblock`: Base 2 logarithm of the maximum input block size. Range is 16 to 24. If set to 0, the value will be set based on the quality.
- _(Optional)_ `minimum_size`: Only compress responses that are bigger than this value in bytes.
- _(Optional)_ `gzip_fallback`: If `True`, uses gzip encoding if `br` is not in the Accept-Encoding header.

## Performance

To better understand the benefits of Brotli over GZip, please read the great article written by Akamai team, [Understanding Brotli's Potential](https://blogs.akamai.com/2016/02/understanding-brotlis-potential.html), where detailed information and benchmarks are provided.

A simple comparative example using Python `sys.getsizof()` and `timeit`:

```python
# ipython console
import gzip
import sys

import brotli
import requests

page = requests.get("https://github.com/fullonic/brotli-asgi").content
%timeit brotli.compress(page, quality=4)
# 1.83 ms ± 43 µs per loop (mean ± std. dev. of 7 runs, 1000 loops each)
sys.getsizeof(brotli.compress(page, quality=4))
# 20081
%timeit gzip.compress(page, compresslevel=6)
# 2.75 ms ± 29.8 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)
sys.getsizeof(gzip.compress(page, compresslevel=6))
# 20640
```

## Compatibility

According to [caniuse.com](https://caniuse.com/#feat=brotli), Brotli is supported by all major browsers with a global use of _94%_.
