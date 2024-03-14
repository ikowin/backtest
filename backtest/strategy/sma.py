from datetime import datetime
import vectorbt as vbt

from backtest.base import Runner
from backtest.data import BinanceData


__all__ = [
    'DualSMAStrategy'
]


class DualSMAStrategy(Runner):
    """The RSI Strategy"""

    def create_label(self, interval: str = '5m', fast_n: int = 5, slow_n: int = 10):
        """Create label for this set of parameters"""
        return f'{interval}_{fast_n}x{slow_n}'

    def iter_parameters(self) -> list:
        args = list()
        for interval in self.get('intervals', []):
            for (fast_n, slow_n) in self.get('params', []):
                args.append(dict(
                    interval=interval,
                    fast_n=fast_n,
                    slow_n=slow_n
                ))
        return args

    def run(self, symbol: str, interval: str = '4h', fast_n: int = 5, slow_n: int = 10):
        start = self.get("start", datetime(2023, 10, 1))
        df = BinanceData.load([symbol], interval=interval, start=start)
        price = df.get('Close')
        
        fast_ma = vbt.MA.run(price, fast_n)
        slow_ma = vbt.MA.run(price, slow_n)
        entries = fast_ma.ma_crossed_above(slow_ma)
        exits = fast_ma.ma_crossed_below(slow_ma)
        
        init_cash = self.get("init_cash", 10000)
        return vbt.Portfolio.from_signals(price, entries, exits, init_cash=init_cash)
    
    def show(self):
        pass

