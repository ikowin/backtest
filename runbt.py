import argparse
import warnings

from backtest.engine import BacktestEngine
from backtest.log import create_log

def run():
    warnings.filterwarnings("ignore")
    create_log("backtest")
    parser = argparse.ArgumentParser(description='The Backtest Engine')
    parser.add_argument('-f', '--config-file', type=str, default="config.yaml")

    args = parser.parse_args()
    
    executor = BacktestEngine(args.config_file)
    executor.exec()



if __name__ == '__main__':
    run()


