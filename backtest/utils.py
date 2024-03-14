import importlib
import yaml
from dateutil.parser import parse as date_parse


def parse_date(dt: str | None = None):
    if dt is None:
        return None
    else:
      return date_parse(dt)

def import_class(module: str, name: str):
    """import class from a python module"""
    m = importlib.import_module(module)
    return getattr(m, name)


def load_yaml_config(fp: str) -> dict:
    """load yaml configurations
    
    the yaml config file:
        - api: {
            key: key,
            secret: secret
          }
        
        - position_manager: {
            name:
            module:
          }

        - strategies:
          - strategy: {
            name: SMA,
            module: miracle.strategy,
            params: {},
            pairs: []
          }
          - strategy: {
            name: RSI,
            module: miracle.strategy,
            params: {},
            pairs: []
          }

    """
    cfg = dict()
    with open(fp, 'r') as f:
        options = yaml.safe_load(f)
        for option in options:
            for k, v in option.items():
                cfg[k] = v
    return cfg


def read_file(fn: str):
    lines = list()
    with open(fn, 'r') as f:
        for line in map(str.strip, f):
            if len(line) > 0:
                lines.append(line)
    return lines