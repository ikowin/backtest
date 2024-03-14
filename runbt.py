import argparse
import warnings

from backtest.engine import BacktestEngine
from backtest.log import create_log

def run():
    warnings.filterwarnings("ignore")
    create_log("backtest")
    parser = argparse.ArgumentParser(description='The Backtest Engine')
    parser.add_argument('-f', '--config-file', type=str, default="config.yaml", help="the yaml config file")
    parser.add_argument('-s', '--show', dest='show_only', action='store_true', help="show the result")

    args = parser.parse_args()
    
    executor = BacktestEngine(args.config_file)
    executor.exec(show_only=args.show_only)



if __name__ == '__main__':
    run()


