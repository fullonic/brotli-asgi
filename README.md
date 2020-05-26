### An AGSI Middleware built using starlette.

Brotli middleware it's a perfect alternative to GZip for both speed and smaller compression responses.

It can be use as a drop in replacement to the GZipMiddleware shipped with starlette (see compatibility bellow).

**A basic example:**

```python
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.middleware import Middleware
from brotli_middleware import BrotliMiddleware


def homepage(request):
    return JSONResponse({"data": "a" * 4000}, status_code=200)


middleware = [Middleware(BrotliMiddleware, quality=4, minimum_size=250)]
app = Starlette(routes=[Route("/", homepage)], middleware=middleware)


```

**Note**: As [FastAPI](https://fastapi.tiangolo.com/) is built on top of Starlette, the Starlette example works as well with FastAPI.

However, here is another use case example with FastApi.

```python
from fastapi import FastAPI
from brotli_middleware import BrotliMiddleware

app = FastAPI()

app.add_middleware(BrotliMiddleware, quality=4, minimum_size=250)
```

By default, the level of compression (quality) is 4 and can go up to 11, where lower values result in faster compression but bigger files (see benchmarks bellow).

The full list of arguments to control how brotli works are the follow:

- **mode**: The compression mode can be:
  generic (default), text (for UTF-8 format text input)
  or font (for WOFF 2.0).
- **quality**: Controls the compression-speed vs compression-
  density tradeoff. The higher the quality, the slower the compression.
  Range is 0 to 11.
- **lgwin**: Base 2 logarithm of the sliding window size. Range
  is 10 to 24.
- **lgblock**: Base 2 logarithm of the maximum input block size.
  Range is 16 to 24. If set to 0, the value will be set based on the
  quality.
- **minimum_size**: Only compress responses that are bigger than this value in bytes.

```python
# the default values are
app.add_middleware(
        BrotliMiddleware, quality=4, mode="text", lgwin=22, lgblock=0, minimum_size=400
    )
```

#### Performance

To better understand why brotli over GZip please read the great article write by Akamai team, [Understanding Brotli's Potential](https://blogs.akamai.com/2016/02/understanding-brotlis-potential.html), where detailed information and benchmarks are made.

A simple comparative example using python `sys.getsizof()` and `timeit`:

```python
# ipython console
import sys
import gzip
import brotli

text = b"*"*100_000_000
%timeit brotli.compress(text, quality=4)
# 606 ms ± 254 µs per loop (mean ± std. dev. of 7 runs, 1 loop each)
sys.getsizeof(brotli.compress(text, quality=4))
# 4761
%timeit gzip.compress(text, compresslevel=6)
# 733 ms ± 6.59 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
sys.getsizeof(gzip.compress(text, compresslevel=6))
# 97255

```

#### Compatibility

Accordantly with [caniuse.com](https://caniuse.com/#feat=brotli) brotli is supported by all major browsers with a global use of _94%_.
