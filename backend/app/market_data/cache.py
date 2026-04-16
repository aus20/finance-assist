from app.market_data.types import PriceRecord


class MarketDataCache:
    def __init__(self) -> None:
        self._records: dict[str, PriceRecord] = {}

    def set_many(self, records: list[PriceRecord]) -> None:
        for record in records:
            self._records[record["ticker"]] = dict(record)

    def snapshot(self) -> dict[str, PriceRecord]:
        return {
            ticker: dict(record)
            for ticker, record in self._records.items()
        }
