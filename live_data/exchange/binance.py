import json
from threading import Thread
from typing import List, Dict
import websocket
from loguru import logger
from websocket import WebSocketApp

from live_data.exchange.exchange import Exchange, OrderBookData, OrderBookLine


class Binance(Exchange):
    """Binance exchange class collects data from binance.

    Currently, collects order book data via web socket.
    """

    BINANCE_WEB_SOCKET_URL = "wss://stream.binance.com:9443"

    def __init__(self, symbols: List[str]):
        self.symbols = symbols

        self.order_books = {
            self.get_symbol_by_stream(symbol.upper()): {} for symbol in self.symbols
        }

        self.stop_threads = False
        logger.info("Starting order book thread.")
        self.order_books_ws = self.init_order_books_ws()
        self.order_book_thread = Thread(target=self.order_book_ws_worker)
        self.order_book_thread.daemon = True
        self.order_book_thread.start()
        logger.info("Binance threads started successfully.")

    def init_order_books_ws(self) -> WebSocketApp:
        """Configure and returns binance web socket for order books."""
        # websocket.enableTrace(True)
        order_book_streams = "/".join(
            [self.get_stream_by_symbol(symbol) for symbol in self.symbols]
        )
        ws = websocket.WebSocketApp(
            f"{Binance.BINANCE_WEB_SOCKET_URL}/stream?streams={order_book_streams}",
            on_open=self.ws_on_open,
            on_message=self.update_order_books,
            on_error=self.ws_on_error,
            on_close=self.ws_on_close,
        )
        return ws

    @staticmethod
    def ws_on_error(_ws: WebSocketApp, msg: str):
        logger.error(msg)

    # @staticmethod
    def ws_on_open(self, _ws: WebSocketApp):
        ws_payload = {
            "method": "SUBSCRIBE",
            "params": self.symbols,
            # "params": ["!ticker@arr"],
            "id": 1
        }
        _ws.send(json.dumps(ws_payload))

        logger.info("Connected to web socket.")

    @staticmethod
    def ws_on_close(_ws: WebSocketApp):
        logger.warning("Web socket closed.")

    def order_book_ws_worker(self):
        """binance order book web socket worker which try to
        establish a connection to binance as long as stop_threads is false."""
        while not self.stop_threads:
            logger.info("Connecting to web socket.")
            self.order_books_ws.run_forever()
            # self.order_books_ws.run_forever(proxy_type="socks5h", http_proxy_host="127.0.0.1", http_proxy_port=2900)

    def update_order_books(self, _ws: WebSocketApp, received_data: str):
        """Parse a message received  by web socket to order book data."""
        parsed_data = json.loads(received_data)

        if "data" not in parsed_data:
            return

        self.order_books[parsed_data["data"]["s"]] = {"time": parsed_data["data"]["E"],
                                                      "price": parsed_data["data"]["c"]}

    @staticmethod
    def parse_order_book_lines(data: List[List[str]]) -> List[OrderBookLine]:
        """Parse one side of order book (bids or asks)."""
        order_book_lines = []
        for line in data:
            order_book_lines.append(
                OrderBookLine(amount=float(line[1]), price=float(line[0]))
            )
        return order_book_lines

    def get_order_books(self) -> Dict[str, OrderBookData]:
        return self.order_books

    @staticmethod
    def get_symbol_by_stream(stream: str) -> str:
        """Structure of order book stream in binance is
        <symbol>@<depth>@<granularity> like `btcusdt@depth20@100ms`."""
        return stream.split("@")[0]

    @staticmethod
    def get_stream_by_symbol(symbol: str) -> str:
        """Structure of order book stream in binance is
        <symbol>@<depth>@<granularity> like `btcusdt@depth20@100ms`."""
        return f"{symbol}@depth20@1000ms"

    def close(self):
        """Close binance threads, currently order book web socket thread."""
        logger.warning("Closing binance threads.")
        self.stop_threads = True
        self.order_books_ws.close()
        self.order_book_thread.join()

        self.order_books_ws = self.init_order_books_ws()
        self.order_book_thread = Thread(target=self.order_book_ws_worker)
        self.order_book_thread.daemon = True
        self.order_book_thread.start()

        logger.info("Binance threads closed successfully.")
