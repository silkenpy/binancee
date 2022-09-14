from typing import Dict, Optional, List, Union

from fastapi import FastAPI, Response, status
from loguru import logger

from live_data.exchange.exchange import OrderBookData, ExchangeEnum


class Live:
    """This class initialize fastapi application."""

    def __init__(self, exchange: Dict, symbols: List[str]):
        self.app = FastAPI(debug=True, title="Live data")
        self.symbols = symbols
        self.exchange = exchange
        #self.app.get("/orderBooks")(self.get_order_books_by)
        #self.app.get("/price")(self.get_order_books_by)
        self.app.get("/")(self.get_order_books_by)
        # fixme: shutdown event not called when running in container.
        self.app.on_event("shutdown")(self.close)

    def get_order_books_by(
        self,
        response: Response,
        exchange_name: Optional[ExchangeEnum] = None,
        symbol: Optional[str] = None,
    ) -> Union[
        OrderBookData, Dict[str, Union[str, OrderBookData, Dict[str, OrderBookData]]]
    ]:
        """OrderBooks endpoint.

        This endpoint receives two optional query params, symbol and exchange_name.

        if neither is provided order book of all symbols for all exchanges
        will be return.

        if exchange_name is provided, order book of all symbols for that exchange
        will be return.

        if symbol is provided, order book of specified symbol for all exchanges
         will be return.

        if both are provided, order book of specified symbol for specified exchange
         will  be return.

        if exchange_name or symbol is not valid, error message with status code 406
         will be return.
        """
        if exchange_name and exchange_name not in self.exchange:
            response.status_code = status.HTTP_406_NOT_ACCEPTABLE
            return {
                "msg": f"{exchange_name} is not in monitored exchanges. "
                f"exchanges: {self.exchange.keys()}."
            }
        if symbol and symbol not in self.symbols:
            response.status_code = status.HTTP_406_NOT_ACCEPTABLE
            return {
                "msg": f"{symbol} is not in monitored symbols. "
                f"symbols: {self.symbols}."
            }
        if symbol and exchange_name:
            return self.get_order_books_by_exchange_symbol(exchange_name, symbol)
        if exchange_name:
            return self.get_order_books_by_exchange(exchange_name)
        if symbol:
            return self.get_order_books_by_symbol(symbol)
        return self.get_all_order_books()

    def get_order_books_by_exchange(
        self, exchange_name: ExchangeEnum
    ) -> Dict[str, OrderBookData]:
        return self.exchange[exchange_name].get_order_books()

    def get_order_books_by_exchange_symbol(
        self, exchange_name: ExchangeEnum, symbol: str
    ) -> OrderBookData:
        return self.get_order_books_by_exchange(exchange_name)[symbol]

    def get_order_books_by_symbol(self, symbol: str) -> Dict[str, OrderBookData]:
        return {
            exchange_name: self.get_order_books_by_exchange_symbol(
                exchange_name, symbol
            )
            for exchange_name in self.exchange
        }

    def get_all_order_books(self) -> Dict[str, Dict[str, OrderBookData]]:
        return {
            exchange_name: self.get_order_books_by_exchange(exchange_name)
            for exchange_name in self.exchange
        }

    def close(self):
        logger.warning("Shutting down.")
        for exchange in self.exchange.values():
            exchange.close()
