from typing import Literal, TypedDict

PriceDirection = Literal["up", "down", "flat"]


class PriceRecord(TypedDict):
    ticker: str
    price: float
    previous_price: float
    timestamp: str
    direction: PriceDirection
