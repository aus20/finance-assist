from __future__ import annotations

import asyncio
import threading
from collections.abc import Iterable

from app.market_data.cache import MarketDataCache
from app.market_data.simulator import MarketDataSimulator
from app.market_data.types import PriceRecord


class MarketDataService:
    def __init__(
        self,
        *,
        cache: MarketDataCache | None = None,
        simulator: MarketDataSimulator | None = None,
        tick_interval: float = 1.0,
    ) -> None:
        self.cache = cache or MarketDataCache()
        self.simulator = simulator or MarketDataSimulator()
        self.tick_interval = tick_interval
        self._task: asyncio.Task[None] | None = None
        self._state_lock = threading.Lock()
        self._subscribers: set[tuple[asyncio.AbstractEventLoop, asyncio.Queue[list[PriceRecord]]]] = set()

    async def start(self) -> None:
        if self._task is not None and not self._task.done():
            return

        with self._state_lock:
            if not self.cache.snapshot():
                self.cache.set_many(self.simulator.seed())
        self._task = asyncio.create_task(self._run(), name="market-data-loop")

    async def stop(self) -> None:
        if self._task is None:
            return

        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        finally:
            self._task = None

    def tick(self) -> None:
        with self._state_lock:
            snapshot = self.cache.snapshot()
            if not snapshot:
                records = self.simulator.seed()
            else:
                records = self.simulator.tick(snapshot)

            self.cache.set_many(records)
            subscribers = list(self._subscribers)

        self._broadcast(records, subscribers)

    def subscribe(self) -> asyncio.Queue[list[PriceRecord]]:
        queue: asyncio.Queue[list[PriceRecord]] = asyncio.Queue()
        loop = asyncio.get_running_loop()
        with self._state_lock:
            self._subscribers.add((loop, queue))
        return queue

    def subscribe_with_snapshot(self) -> tuple[dict[str, PriceRecord], asyncio.Queue[list[PriceRecord]]]:
        queue: asyncio.Queue[list[PriceRecord]] = asyncio.Queue()
        loop = asyncio.get_running_loop()
        with self._state_lock:
            self._subscribers.add((loop, queue))
            snapshot = self.cache.snapshot()
        return snapshot, queue

    def unsubscribe(self, queue: asyncio.Queue[list[PriceRecord]]) -> None:
        with self._state_lock:
            self._subscribers = {
                subscriber
                for subscriber in self._subscribers
                if subscriber[1] is not queue
            }

    async def _run(self) -> None:
        try:
            while True:
                await asyncio.sleep(self.tick_interval)
                self.tick()
        except asyncio.CancelledError:
            raise

    def _broadcast(
        self,
        records: Iterable[PriceRecord],
        subscribers: Iterable[tuple[asyncio.AbstractEventLoop, asyncio.Queue[list[PriceRecord]]]],
    ) -> None:
        payload = [dict(record) for record in records]
        stale_subscribers: list[tuple[asyncio.AbstractEventLoop, asyncio.Queue[list[PriceRecord]]]] = []

        for loop, queue in subscribers:
            if loop.is_closed():
                stale_subscribers.append((loop, queue))
                continue
            loop.call_soon_threadsafe(queue.put_nowait, payload)

        if stale_subscribers:
            with self._state_lock:
                for subscriber in stale_subscribers:
                    self._subscribers.discard(subscriber)
