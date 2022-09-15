
import uvicorn

from live_data.live import Live
from live_data.exchange.binance import Binance

binance_instance = Binance(
    [
        # "!bookTicker"
        "!ticker"
        # "btcusdt@ticker", "ethusdt@ticker", "trxusdt@ticker", "shibusdt@ticker", "dogeusdt@ticker",
        # "celrusdt@ticker", "oneusdt@ticker", "etcusdt@ticker", "compusdt@ticker", "xrpusdt@ticker",
        # "bnbusdt@ticker", "maticusdt@ticker", "solusdt@ticker", "ltcusdt@ticker", "icpusdt@ticker",
        # "linkusdt@ticker", "sandusdt@ticker", "manausdt@ticker", "cakeusdt@ticker", "dotusdt@ticker",
        # "adausdt@ticker", "atomusdt@ticker", "ftmusdt@ticker", "cosusdt@ticker", "paxgusdt@ticker",

    ]
)

live_server = Live(exchange={"binance": binance_instance}, symbols=[])
app = live_server.app
if __name__ == "__main__":
    uvicorn.run(live_server.app, host="127.0.0.1", port=8000)
