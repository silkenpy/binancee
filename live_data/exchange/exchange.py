from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict


@dataclass
class OrderBookLine:
    """This data class represents a line of order book."""

    amount: float
    price: float


@dataclass
class OrderBookData:
    """This data class represents order book data for a symbol."""

    asks: List[OrderBookLine]
    bids: List[OrderBookLine]
    time: float

class ExchangeEnum(str, Enum):
    """All supported exchanges should be defined here."""

    Binance = "binance"


class Exchange(ABC):
    """All exchanges should be inherited from this class
    to ensure required functionality."""

    @abstractmethod
    def get_order_books(self) -> Dict[str, OrderBookData]:
        """Returns a dict which keys are symbols and values are order book data."""

    def close(self):
        """Util function use by Live class
        to close all exchanges gracefully (threads, web sockets, etc)"""
