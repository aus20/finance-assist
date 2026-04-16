from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.market_data.service import MarketDataService
from app.market_data.types import PriceRecord

router = APIRouter(prefix="/api/stream", tags=["stream"])


def _serialize_event(record: PriceRecord) -> str:
    return f"data: {json.dumps(record)}\n\n"


@router.get("/prices")
async def stream_prices(request: Request) -> StreamingResponse:
    market_data = getattr(request.app.state, "market_data", None)
    if not isinstance(market_data, MarketDataService):
        raise HTTPException(status_code=503, detail="market data service is unavailable")

    async def event_stream() -> AsyncIterator[str]:
        initial_snapshot, queue = market_data.subscribe_with_snapshot()
        try:
            for record in initial_snapshot.values():
                yield _serialize_event(record)

            while True:
                if await request.is_disconnected():
                    break

                try:
                    records = await asyncio.wait_for(queue.get(), timeout=0.25)
                except TimeoutError:
                    continue

                for record in records:
                    yield _serialize_event(record)
        except asyncio.CancelledError:
            raise
        finally:
            market_data.unsubscribe(queue)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
