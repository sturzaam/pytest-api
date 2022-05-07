import json

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .schemas import (
    BEHAVIORS,
    handle_request_body,
    handle_responses,
    pascal,
    to_json_schema,
)


class SpecificationResponder:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self.func = None
        self.status_code = None
        self.should_update_example = False
        self.should_update_description = False
        self.receive: Receive = unattached_receive
        self.send: Send = unattached_send
        self.initial_message: Message = {}
        self.started = False

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        headers = MutableHeaders(scope=scope)
        self.path = scope["path"]
        self.method = scope["method"].lower()
        self.receive = receive
        self.send = send

        self.handle_spec(headers)

        await self.app(scope, self.receive_example, self.send_with_spec)

    def handle_spec(self, headers):
        behaviors = BEHAVIORS[self.path]
        self.should_update_example = headers.get("spec-example", "") in behaviors
        self.should_update_description = (
            headers.get("spec-description", "") in behaviors
        )

        if self.should_update_example:
            self.func = behaviors[headers.get("spec-example")]
        elif self.should_update_description:
            self.func = behaviors[headers.get("spec-description")]

    async def receive_example(self) -> Message:
        message = await self.receive()

        if not self.should_update_example:
            return message

        body = message["body"]
        more_body = message.get("more_body", False)
        if more_body:
            message = await self.receive()
            if message["body"] != b"":  # pragma: no cover
                raise NotImplementedError(
                    "Streaming the request body isn't supported yet"
                )

        receive_body = json.loads(body)
        handle_request_body(receive_body, self.path, self.method, self.func)
        to_json_schema(receive_body, pascal(self.func))

        message["body"] = body
        return message

    async def send_with_spec(self, message: Message) -> None:
        if not self.should_update_description:
            await self.send(message)
            return

        if message["type"] == "http.response.start":
            self.status_code = message["status"]
            headers = Headers(raw=message["headers"])
            if headers["content-type"] != "application/json":
                self.should_update_description = False
                await self.send(message)
                return
            self.initial_message = message

        elif message["type"] == "http.response.body":
            body = message.get("body", b"")
            more_body = message.get("more_body", False)
            if more_body:  # pragma: no cover
                raise NotImplementedError(
                    "Streaming the response body isn't supported yet"
                )

            headers = MutableHeaders(raw=self.initial_message["headers"])
            headers["Content-Type"] = "application/json"
            headers["Content-Length"] = str(len(body))
            message["body"] = body

            handle_responses(self.path, self.method, self.status_code, self.func)

            await self.send(self.initial_message)
            await self.send(message)


async def unattached_receive() -> Message:
    raise RuntimeError("receive awaitable not set")  # pragma: no cover


async def unattached_send(message: Message) -> None:
    raise RuntimeError("send awaitable not set")  # pragma: no cover
