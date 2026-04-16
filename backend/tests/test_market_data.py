import asyncio

from app.market_data.service import MarketDataService
from app.main import app

REQUIRED_PRICE_FIELDS = {
    "ticker",
    "price",
    "previous_price",
    "timestamp",
    "direction",
}


def _market_data_service():
    market_data = getattr(app.state, "market_data", None)
    assert market_data is not None, "expected app.state.market_data to be seeded at startup"
    return market_data


def test_seeded_default_ticker_records_have_required_fields(client):
    market_data = _market_data_service()

    snapshot = market_data.cache.snapshot()

    assert snapshot, "expected seeded ticker records before the first stream read"
    first_record = next(iter(snapshot.values()))
    assert REQUIRED_PRICE_FIELDS <= set(first_record)


def test_one_tick_updates_price_data_while_preserving_shape(client):
    market_data = _market_data_service()

    before_snapshot = market_data.cache.snapshot()
    ticker, before_record = next(iter(before_snapshot.items()))

    market_data.tick()

    after_record = market_data.cache.snapshot()[ticker]

    assert REQUIRED_PRICE_FIELDS <= set(after_record)
    assert after_record["ticker"] == ticker
    assert after_record["price"] != before_record["price"]
    assert after_record["previous_price"] == before_record["price"]


def test_cache_stores_previous_and_current_values_correctly(client):
    market_data = _market_data_service()

    before_snapshot = market_data.cache.snapshot()
    ticker, before_record = next(iter(before_snapshot.items()))

    market_data.tick()

    after_record = market_data.cache.snapshot()[ticker]

    assert after_record["ticker"] == ticker
    assert after_record["previous_price"] == before_record["price"]
    assert after_record["price"] != before_record["price"]


def test_service_can_restart_after_stop():
    async def scenario() -> None:
        service = MarketDataService(tick_interval=0.01)

        await service.start()
        await asyncio.sleep(0.03)
        first_run_snapshot = service.cache.snapshot()
        await service.stop()

        stopped_snapshot = service.cache.snapshot()
        await asyncio.sleep(0.03)
        assert service.cache.snapshot() == stopped_snapshot

        await service.start()
        restarted_before = service.cache.snapshot()
        await asyncio.sleep(0.03)
        restarted_after = service.cache.snapshot()
        await service.stop()

        assert first_run_snapshot
        assert restarted_before
        assert restarted_after != restarted_before

    asyncio.run(scenario())


def test_subscribe_with_snapshot_returns_coherent_initial_state_then_later_updates():
    async def scenario() -> None:
        service = MarketDataService(tick_interval=1)
        await service.start()

        initial_snapshot, queue = service.subscribe_with_snapshot()
        ticker, initial_record = next(iter(initial_snapshot.items()))

        service.tick()
        update_batch = await asyncio.wait_for(queue.get(), timeout=1)
        update_by_ticker = {record["ticker"]: record for record in update_batch}
        updated_record = update_by_ticker[ticker]

        service.unsubscribe(queue)
        await service.stop()

        assert initial_record["ticker"] == ticker
        assert updated_record["ticker"] == ticker
        assert updated_record["previous_price"] == initial_record["price"]
        assert updated_record["price"] != initial_record["price"]

    asyncio.run(scenario())
