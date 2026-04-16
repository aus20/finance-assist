import asyncio
import json

from app.main import app
from app.routes.stream import stream_prices

EXPECTED_EVENT_FIELDS = {
    "ticker",
    "price",
    "previous_price",
    "timestamp",
    "direction",
}

class _StubRequest:
    def __init__(self, app):
        self.app = app
        self._disconnected = False

    async def is_disconnected(self) -> bool:
        return self._disconnected

    def disconnect(self) -> None:
        self._disconnected = True


async def _collect_asgi_messages(path: str) -> list[dict[str, object]]:
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "headers": [(b"host", b"testserver")],
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
        "root_path": "",
        "app": app,
    }
    first_body_seen = asyncio.Event()
    request_seen = False
    messages: list[dict[str, object]] = []

    async def receive() -> dict[str, object]:
        nonlocal request_seen
        if not request_seen:
            request_seen = True
            return {"type": "http.request", "body": b"", "more_body": False}
        await first_body_seen.wait()
        return {"type": "http.disconnect"}

    async def send(message: dict[str, object]) -> None:
        messages.append(message)
        if message["type"] == "http.response.body" and message.get("body"):
            first_body_seen.set()

    await asyncio.wait_for(app(scope, receive, send), timeout=5)
    return messages


def _first_response_body(messages: list[dict[str, object]]) -> str:
    for message in messages:
        if message["type"] == "http.response.body" and message.get("body"):
            return message["body"].decode()
    raise AssertionError("expected at least one response body event")


def test_get_stream_prices_returns_event_stream(client):
    messages = asyncio.run(_collect_asgi_messages("/api/stream/prices"))
    response_start = messages[0]

    assert response_start["type"] == "http.response.start"
    assert response_start["status"] == 200
    headers = dict(response_start["headers"])
    assert headers[b"content-type"].split(b";")[0] == b"text/event-stream"


def test_stream_output_contains_expected_fields(client):
    messages = asyncio.run(_collect_asgi_messages("/api/stream/prices"))
    payload = json.loads(_first_response_body(messages).removeprefix("data:").strip())

    assert EXPECTED_EVENT_FIELDS <= set(payload)


def test_startup_seeds_market_data_before_first_stream_read(client):
    market_data = getattr(app.state, "market_data", None)
    assert market_data is not None, "expected app.state.market_data to exist after startup"

    seeded_snapshot = market_data.cache.snapshot()
    assert seeded_snapshot, "expected startup to seed market data before any stream read"

    messages = asyncio.run(_collect_asgi_messages("/api/stream/prices"))
    decoded_payload = json.loads(_first_response_body(messages).removeprefix("data:").strip())

    assert decoded_payload["ticker"] in seeded_snapshot


def test_stream_remains_open_for_successive_updates(client):
    market_data = getattr(app.state, "market_data", None)
    assert market_data is not None
    snapshot_size = len(market_data.cache.snapshot())

    request = _StubRequest(app)
    response = client.portal.call(stream_prices, request)

    try:
        first_payload = json.loads(client.portal.call(anext, response.body_iterator).removeprefix("data:").strip())
        for _ in range(snapshot_size - 1):
            client.portal.call(anext, response.body_iterator)

        market_data.tick()

        second_payload = json.loads(client.portal.call(anext, response.body_iterator).removeprefix("data:").strip())
    finally:
        request.disconnect()
        client.portal.call(response.body_iterator.aclose)

    assert first_payload["ticker"] == second_payload["ticker"]
    assert first_payload["price"] != second_payload["price"]
    assert second_payload["previous_price"] == first_payload["price"]


def test_stream_returns_503_when_market_data_service_is_unavailable(client):
    original_market_data = getattr(app.state, "market_data", None)
    delattr(app.state, "market_data")
    try:
        response = client.get("/api/stream/prices")
    finally:
        if original_market_data is not None:
            app.state.market_data = original_market_data

    assert response.status_code == 503
    assert response.json()["detail"] == "market data service is unavailable"
