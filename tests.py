import pytest
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse, StreamingResponse
from starlette.testclient import TestClient
from starlette.middleware.gzip import GZipMiddleware
from brotli_middleware import BrotliMiddleware
import brotli


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
    print(len(response.headers["Content-Length"]))
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


# @pytest.mark.skip
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
