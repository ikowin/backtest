"""The base backtest strategy runner"""

import os
from abc import ABC, abstractmethod


class Runner(ABC):

    def __init__(self, work_dir: str, cfg: dict):
        self.work_dir = work_dir
        self.cfg = cfg
    
    def get_plots(self):
        """Get plots for creation"""
        return self.cfg.get("plots", [])
    
    def get(self, key, default=None):
        return self.cfg.get(key, default)
    
    def set(self, key, value):
        self.cfg[key] = value
        return self
    
    @abstractmethod
    def create_label(self, **params) -> str:
        """Create label for this set of parameters"""
        pass
    
    @abstractmethod
    def iter_parameters(self) -> list:
        """Iterate all possible backtesting parameters"""
        pass

    def get_output_file(self, **params):
        """Build the path of output file"""
        label = self.create_label(**params)
        # basename = self.cfg.get("output", {}).format(**params)
        basename = self.cfg.get("output", {}).format(label=label)
        return os.path.join(self.work_dir, basename)
    
    def get_work_dir(self):
        return self.work_dir
    
    @abstractmethod
    def run(self, symbol: str, **params):
        """Run backtest for a given symbol on a set of parameters"""
        pass
