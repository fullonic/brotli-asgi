"""AGSI Brotli middleware build on top of startlette."""

import brotli  # type: ignore
from brotli import Compressor, MODE_GENERIC
import io

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class BrotliMiddleware:
    def __init__(self, app: ASGIApp, quality: int = 4, minimum_size: int = 200) -> None:
        self.app = app
        self.quality = quality
        self.minimum_size = minimum_size

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            headers = Headers(scope=scope)
            if "br" in headers.get("Accept-Encoding", ""):
                responder = BrotliResponder(self.app, self.quality, self.minimum_size)
                await responder(scope, receive, send)
                return
        await self.app(scope, receive, send)


class BrotliResponder:
    def __init__(self, app: ASGIApp, quality: int, minimum_size: int) -> None:
        self.app = app
        self.minimum_size = minimum_size
        self.quality = quality
        self.send = unattached_send  # type: Send
        self.initial_message = {}  # type: Message
        self.started = False
        self.br_file = brotli.compress
        # for dealing with streaming brotli files
        self.br_stream = Compressor(mode=MODE_GENERIC, quality=4, lgwin=22, lgblock=0)
        self.br_buffer = io.BytesIO()

    async def __call__(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:  # noqa
        self.send = send
        await self.app(scope, receive, self.send_with_brotli)

    async def send_with_brotli(self, message: Message) -> None:
        """Apply compression using brotli."""
        message_type = message["type"]
        if message_type == "http.response.start":
            # Don't send the initial message until we've determined how to
            # modify the ougoging headers correctly.
            self.initial_message = message
        elif message_type == "http.response.body" and not self.started:
            self.started = True
            body = message.get("body", b"")
            more_body = message.get("more_body", False)
            if len(body) < self.minimum_size and not more_body:
                # Don't apply Brotli to small outgoing responses.
                await self.send(self.initial_message)
                await self.send(message)
            elif not more_body:
                # Standard Brotli response.
                body = self.br_file(body, quality=self.quality)
                headers = MutableHeaders(raw=self.initial_message["headers"])
                headers["Content-Encoding"] = "br"
                headers["Content-Length"] = str(len(body))
                headers.add_vary_header("Accept-Encoding")
                message["body"] = body
                await self.send(self.initial_message)
                await self.send(message)
            else:
                # TODO: Add support for streaming
                # Initial body in streaming Brotli response.
                headers = MutableHeaders(raw=self.initial_message["headers"])
                headers["Content-Encoding"] = "br"
                headers.add_vary_header("Accept-Encoding")
                del headers["Content-Length"]
                self.br_buffer.write(
                    self.br_stream.compress(body) + self.br_stream.flush()
                )

                message["body"] = self.br_buffer.getvalue()
                self.br_buffer.seek(0)
                self.br_buffer.truncate()
                await self.send(self.initial_message)
                await self.send(message)

        elif message_type == "http.response.body":
            # Remaining body in streaming Brotli response.
            body = message.get("body", b"")
            more_body = message.get("more_body", False)
            self.br_buffer.write(self.br_stream.compress(body) + self.br_stream.flush())
            if not more_body:
                self.br_buffer.write(self.br_stream.finish())
            message["body"] = self.br_buffer.getvalue()
            print(len(message["body"]), len(body))
            self.br_buffer.seek(0)
            self.br_buffer.truncate()

            await self.send(message)


async def unattached_send(message: Message) -> None:
    raise RuntimeError("send awaitable not set")  # pragma: no cover
