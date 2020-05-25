"""AGSI Brotli middleware build on top of startlette."""

import brotli  # type: ignore
import io

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class BrotliMiddleware:
    def __init__(self, app: ASGIApp, quality: int = 4, minimum_size: int = 500) -> None:
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

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:  # noqa
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
                self.br_file(body, quality=self.quality)
                body = self.br_file(body, quality=self.quality)
                headers = MutableHeaders(raw=self.initial_message["headers"])
                headers["Content-Encoding"] = "br"
                headers["Content-Length"] = str(len(body))
                headers.add_vary_header("Accept-Encoding")
                message["body"] = body

                await self.send(self.initial_message)
                await self.send(message)

async def unattached_send(message: Message) -> None:
    raise RuntimeError("send awaitable not set")  # pragma: no cover
