"""Main tests for brotli middleware.

Some of these tests are the same as the ones from starlette.tests.middleware.test_gzip
but using brotli instead.
"""
import gzip
import io

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse, StreamingResponse, JSONResponse, Response
from starlette.testclient import TestClient

from brotli_asgi import BrotliMiddleware


def test_brotli_responses():
    app = Starlette()

    app.add_middleware(BrotliMiddleware)

    @app.route("/")
    def homepage(request):
        return PlainTextResponse("x" * 4000, status_code=200)

    client = TestClient(app)
    response = client.get("/", headers={"accept-encoding": "br"})
    assert response.status_code == 200
    assert response.text == "x" * 4000
    assert response.headers["Content-Encoding"] == "br"
    assert int(response.headers["Content-Length"]) < 4000


def test_brotli_not_in_accept_encoding():
    app = Starlette()

    app.add_middleware(BrotliMiddleware)

    @app.route("/")
    def homepage(request):
        return PlainTextResponse("x" * 4000, status_code=200)

    client = TestClient(app)
    response = client.get("/", headers={"accept-encoding": "identity"})
    assert response.status_code == 200
    assert response.text == "x" * 4000
    assert "Content-Encoding" not in response.headers
    assert int(response.headers["Content-Length"]) == 4000


def test_brotli_ignored_for_small_responses():
    app = Starlette()

    app.add_middleware(BrotliMiddleware)

    @app.route("/")
    def homepage(request):
        return PlainTextResponse("OK", status_code=200)

    client = TestClient(app)
    response = client.get("/", headers={"accept-encoding": "br"})
    assert response.status_code == 200
    assert response.text == "OK"
    assert "Content-Encoding" not in response.headers
    assert int(response.headers["Content-Length"]) == 2


def test_brotli_streaming_response():
    app = Starlette()

    app.add_middleware(BrotliMiddleware)

    @app.route("/")
    def homepage(request):
        async def generator(bytes, count):
            for _ in range(count):
                yield bytes

        streaming = generator(bytes=b"x" * 400, count=10)
        return StreamingResponse(streaming, status_code=200)

    client = TestClient(app)
    response = client.get("/", headers={"accept-encoding": "br"})
    assert response.status_code == 200
    assert response.text == "x" * 4000
    assert response.headers["Content-Encoding"] == "br"
    assert "Content-Length" not in response.headers


def test_brotli_api_options():
    """Tests default values overriding."""
    app = Starlette()

    app.add_middleware(
        BrotliMiddleware,
        quality=11,
        mode="text",
        lgwin=20,
        lgblock=16,
    )

    @app.route("/")
    def homepage(request):
        return JSONResponse({"data": "a" * 4000}, status_code=200)

    client = TestClient(app)
    response = client.get("/", headers={"accept-encoding": "br"})
    assert response.status_code == 200


def test_gzip_fallback():
    app = Starlette()

    app.add_middleware(BrotliMiddleware, gzip_fallback=True)

    @app.route("/")
    def homepage(request):
        return PlainTextResponse("x" * 4000, status_code=200)

    client = TestClient(app)
    response = client.get("/", headers={"accept-encoding": "gzip"})
    assert response.status_code == 200
    assert response.text == "x" * 4000
    assert response.headers["Content-Encoding"] == "gzip"
    assert int(response.headers["Content-Length"]) < 4000


def test_gzip_fallback_false():
    app = Starlette()

    app.add_middleware(BrotliMiddleware, gzip_fallback=False)

    @app.route("/")
    def homepage(request):
        return PlainTextResponse("x" * 4000, status_code=200)

    client = TestClient(app)
    response = client.get("/", headers={"accept-encoding": "gzip"})
    assert response.status_code == 200
    assert response.text == "x" * 4000
    assert "Content-Encoding" not in response.headers
    assert int(response.headers["Content-Length"]) == 4000


def test_excluded_handlers():
    app = Starlette()

    app.add_middleware(
        BrotliMiddleware,
        excluded_handlers=["/excluded"],
    )

    @app.route("/excluded")
    def homepage(request):
        return PlainTextResponse("x" * 4000, status_code=200)

    client = TestClient(app)
    response = client.get("/excluded", headers={"accept-encoding": "br"})

    assert response.status_code == 200
    assert response.text == "x" * 4000
    assert "Content-Encoding" not in response.headers
    assert int(response.headers["Content-Length"]) == 4000


def test_brotli_avoids_double_encoding():
    # See https://github.com/encode/starlette/pull/1901

    app = Starlette()

    app.add_middleware(BrotliMiddleware, minimum_size=1)

    @app.route("/")
    def homepage(request):
        gzip_buffer = io.BytesIO()
        gzip_file = gzip.GzipFile(mode="wb", fileobj=gzip_buffer)
        gzip_file.write(b"hello world" * 200)
        gzip_file.close()
        body = gzip_buffer.getvalue()
        return Response(
            body,
            headers={
                "content-encoding": "gzip",
                "x-gzipped-content-length": str(len(body))
            }
        )

    client = TestClient(app)
    response = client.get("/", headers={"accept-encoding": "br"})
    assert response.status_code == 200
    assert response.text == "hello world" * 200
    assert response.headers["Content-Encoding"] == "gzip"
    assert response.headers["Content-Length"] == response.headers["x-gzipped-content-length"]
