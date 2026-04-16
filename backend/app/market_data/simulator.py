from __future__ import annotations

from datetime import UTC, datetime
from random import Random

from app.market_data.types import PriceDirection, PriceRecord

DEFAULT_PRICES = {
    "AAPL": 191.42,
    "MSFT": 428.15,
    "GOOGL": 173.88,
    "AMZN": 184.27,
    "TSLA": 171.63,
}


class MarketDataSimulator:
    def __init__(self, seed: int = 7) -> None:
        self._random = Random(seed)

    def seed(self) -> list[PriceRecord]:
        timestamp = _timestamp()
        return [
            {
                "ticker": ticker,
                "price": price,
                "previous_price": price,
                "timestamp": timestamp,
                "direction": "flat",
            }
            for ticker, price in DEFAULT_PRICES.items()
        ]

    def tick(self, snapshot: dict[str, PriceRecord]) -> list[PriceRecord]:
        timestamp = _timestamp()
        records: list[PriceRecord] = []

        for ticker, current in snapshot.items():
            previous_price = current["price"]
            movement = round(self._random.uniform(-1.5, 1.5), 2)
            if movement == 0:
                movement = 0.01
            price = round(max(1.0, previous_price + movement), 2)
            records.append(
                {
                    "ticker": ticker,
                    "price": price,
                    "previous_price": previous_price,
                    "timestamp": timestamp,
                    "direction": _direction(price, previous_price),
                }
            )

        return records


def _timestamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _direction(price: float, previous_price: float) -> PriceDirection:
    if price > previous_price:
        return "up"
    if price < previous_price:
        return "down"
    return "flat"
