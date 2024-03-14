"""The backtest engine

The engine runs according to the configuration file which will include:
    - the symbols
    - the strategies and their params
    - the output result files
    - the plots
"""


import os
import logging
import pandas as pd

from backtest.base import Runner
from backtest.plot import BoxPlot
from backtest.utils import (
    load_yaml_config, read_file, import_class
)


log = logging.getLogger(__name__)


class ConfigError(Exception):
    pass


class EngineConfig:

    def __init__(self, fp: str):
        self.symbols = list()
        self.strategies = list()
        self.data = dict()
        self.load_config(fp)

    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def set(self, key, value):
        self.data[key] = value

    def load_config(self, fn: str):
        cfgs = load_yaml_config(fn)
        # Add symbols
        options = cfgs.get('symbols', [])
        for option in options:
            if 'names' in option:
                self.symbols += [s.strip() for s in option['names']]
            elif 'feeds' in option:
                for feed in option['feeds']:
                    self.symbols += read_file(feed)
        # Add strategy
        for s in cfgs.get('strategies', []):
            self.strategies.append(s)
        return self



class BacktestEngine:
    """The Backtest Engine"""

    def __init__(self, fp: str):
        self.cfg = EngineConfig(fp)

    def _exec(self, runner, tokens: list, **params):
        """"execute backtest for all tokens via a group of parameters

        Args:
            runner: callable, the strategy instance
            tokens: list, tokens feed into the runner
            params: dict, a set of strategy parameters
        
        We execute backtesting for all symbols for a given set of parameters.
        """
        # The output CSV headers
        headers = ['Start', 'End', 'Period', 'Start Value', 'End Value', 'Total Return [%]', 'Benchmark Return [%]', 
                'Max Gross Exposure [%]', 'Total Fees Paid', 'Max Drawdown [%]', 'Max Drawdown Duration', 'Total Trades', 
                'Total Closed Trades', 'Total Open Trades', 'Open Trade PnL', 'Win Rate [%]', 'Best Trade [%]', 'Worst Trade [%]', 
                'Avg Winning Trade [%]', 'Avg Losing Trade [%]', 'Avg Winning Trade Duration', 'Avg Losing Trade Duration', 
                'Profit Factor', 'Expectancy', 'Sharpe Ratio', 'Calmar Ratio', 'Omega Ratio', 'Sortino Ratio']
        
        df = pd.DataFrame(columns=headers)

        # Run backtest for a given symbol + a set of parameters
        for token in tokens:
            try:
                log.info('backtest %s on %s ...', token, params)
                s = runner.run(token, **params)
                df.loc[token] = s
            except Exception as ex:
                pass
        
        # Write into CSV file
        df.index.name = 'Token'
        df = df.sort_values(by='Total Return [%]', ascending=False)
        fp = runner.get_output_file(**params)
        df.to_csv(fp)

    def exec(self, dry_run: bool = False):
        if dry_run:
            return
        for one in self.cfg.strategies:
            s = one.get('strategy')
            name, module = s['name'], s['module']
            # Load the strategy class
            log.info("Strategy: %s.%s", module, name)
            cls= import_class(module, name)
            # Create working dir
            work_dir = s.get('work_dir', '.')
            if not os.path.exists(work_dir):
                os.mkdir(work_dir)
            # initialize the strategy
            runner: Runner = cls(work_dir, s)
            # Iterate all possible backtesting parameters
            for params in runner.iter_parameters():
                self._exec(runner, self.cfg.symbols, **params)
            # Create plots
            BoxPlot(runner).create_plots()

