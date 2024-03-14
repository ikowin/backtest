from datetime import datetime
import vectorbt as vbt

from backtest.base import Runner
from backtest.data import BinanceData


class RSIStrategy(Runner):
    """The RSI Strategy"""

    def create_label(self, interval: str = '5m', window: int = 10, min_rsi: int = 5, max_rsi: int = 10):
        """Create label for this set of parameters"""
        return f'{interval}_{window}_{min_rsi}x{max_rsi}'

    def iter_parameters(self) -> list:
        args = list()
        for interval in self.get('intervals', []):
            for window in self.get('windows', []):
                for (min_rsi, max_rsi) in self.get('params', []):
                    args.append(dict(
                        interval=interval,
                        window=window,
                        min_rsi=min_rsi,
                        max_rsi=max_rsi
                    ))
        return args

    def run(self, symbol: str, interval: str = '4h', window: int = 4, min_rsi: int = 20, max_rsi: int = 80):
        start = self.get("start", datetime(2023, 10, 1))
        df = BinanceData.load([symbol], interval=interval, start=start)
        price = df.get('Close')
        # Use MA
        # rsi = vbt.RSI.run(price, window=14, short_name="rsi")
        # https://github.com/polakowo/vectorbt/blob/master/examples/MACDVolume.ipynb

        rsi = vbt.RSI.run(price, window)
        entries = rsi.rsi_below(min_rsi)
        exits = rsi.rsi_above(max_rsi)
        # Note:
        # 1. entries and exits are pandas.core.series.Series with dtype ='bool', and
        #    entries.index.name = 'Open time'
        #    exits.index.name = 'Open time'
        # 2. price is Series and 
        #    price.index.name = 'Open time'
        #    price.name = 'Close'
        # 3. price, entries, exits have the same length
        #    len(price) = len(entries) = len(exits)
        init_cash = self.get("init_cash", 10000)
        return vbt.Portfolio.from_signals(price, entries, exits, init_cash=init_cash)

