# https://docs.sqlalchemy.org/en/20/core/metadata.html
import os
from datetime import datetime

from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, Float, String
from sqlalchemy import insert, update, select, and_
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy import create_engine

# from basana.config import BINANCE_FUTURES_KLINE_DB

BINANCE_FUTURES_KLINE_DB = "D:\\data\\binance\\db\\futures\\um_klines"

# Following are only Sqlite3!

# the kline db
def add_kline_table(metadata_obj, period='1d'):
    return Table(
        f"k{period}",
        metadata_obj,
        # the kline open time in unix time format
        Column('s', Integer, primary_key=True),
        # the open price
        Column('o', Float(precision=32, decimal_return_scale=None)),
        # the high price
        Column('h', Float(precision=32, decimal_return_scale=None)),
        # the low price
        Column('l', Float(precision=32, decimal_return_scale=None)),
        # the close price
        Column('c', Float(precision=32, decimal_return_scale=None)),
        # the base asset volume
        Column('bv', Float(precision=32, decimal_return_scale=None)),
        # the close time
        Column('e', Integer),
        # the quote asset volume
        Column('qv', Float(precision=32, decimal_return_scale=None)),
        # the number of trades
        Column('n', Integer),
        # the taker buy base asset volume (V)
        Column('tbbv', Float(precision=32, decimal_return_scale=None)),
        # the taker buy quote asset volume
        Column('tbqv', Float(precision=32, decimal_return_scale=None)),
        # the unused field
        Column('i', Integer)
    )


class KlineDb:
    """"The Db for storing Kline Data
    
    >>> db = KlineDb('BTCUSDT')
    >>> db.create_tables()
    
    """
    def __init__(self, symbol: str, path: str = '.'):
        self.symbol = symbol
        self.path = path
        self.dbname = symbol.strip().upper()
        self.db_url = f'sqlite:///{path}/{self.dbname}.db'
        # print(self.db_url)
        # breakpoint()
        # print(self.db_url)
        # db metadata
        self.metadata = MetaData()

        # db engine
        self.engine = None

        # Add tables here
        self.k1d = add_kline_table(self.metadata, period='1d')
        self.k4h = add_kline_table(self.metadata, period='4h')
        self.k30m = add_kline_table(self.metadata, period='30m')
        self.k5m = add_kline_table(self.metadata, period='5m')
        self.k1m = add_kline_table(self.metadata, period='1m')

        # provide the dict interface
        # >>> table = db.tables.get('1d')
        self.tables = {
            '1d': self.k1d,
            '4h': self.k4h,
            '30m': self.k30m,
            '5m': self.k5m,
            '1m': self.k1m
        }

    def create_engine(self, echo: bool = True):
        """Create or get the db engine"""
        if self.engine is None:
            self.engine = create_engine(self.db_url, echo=echo)
        return self.engine
    
    def create_tables(self):
        engine = self.create_engine()
        self.metadata.create_all(engine)

    def _to_timestamp(self, dt: datetime | None = None):
        if dt is not None:
            return int(dt.timestamp() * 1000)
        else:
            return 0
        
    def select(self, symbol: str, interval: str, 
                          start: datetime | None = None, end: datetime | None = None, 
                          skip_if_exists: bool = True):
        pass

    def export_ohlcv_file(self, symbol: str, interval: str, 
                          start: datetime | None = None, end: datetime | None = None, 
                          skip_if_exists: bool = True):
        fn = f'data/binance-{symbol}-{interval}.csv'
        if os.path.exists(fn) and skip_if_exists:
            return fn
        
        table = self.tables.get(interval)
        if table is None:
            raise Exception(f"Not table for interval {interval}")
        
        engine = self.create_engine()
        # https://docs.sqlalchemy.org/en/20/tutorial/data_select.html
        start_ts = self._to_timestamp(start)
        end_ts = self._to_timestamp(end)
        
        if start_ts > 0 and end_ts > 0:
            stmt = select(table.c.s, table.c.o, table.c.h, 
                      table.c.l, table.c.c, table.c.qv).where(
                          and_(table.c.s >= start_ts, table.c.s < end_ts)
                      ).order_by(table.c.s)
        elif start_ts > 0:
            stmt = select(table.c.s, table.c.o, table.c.h, 
                      table.c.l, table.c.c, table.c.qv).where(
                          table.c.s >= start_ts
                      ).order_by(table.c.s)
        elif end_ts > 0:
            stmt = select(table.c.s, table.c.o, table.c.h, 
                      table.c.l, table.c.c, table.c.qv).where(
                          table.c.s < end_ts
                      ).order_by(table.c.s)
        else:
            stmt = select(table.c.s, table.c.o, table.c.h, 
                      table.c.l, table.c.c, table.c.qv).order_by(table.c.s)
        
        lines = list()
        with engine.connect() as conn:
            for row in conn.execute(stmt):
                # datetime,open,high,low,close,volume
                dt = datetime.fromtimestamp(row[0] / 1000)
                line = f'{dt},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]}\n'
                lines.append(line)
        
        with open(fn, 'w') as f:
            f.write('datetime,open,high,low,close,volume\n')
            f.writelines(lines)

        return fn


def get_default_klinedb(symbol: str):
    return KlineDb(symbol, path=BINANCE_FUTURES_KLINE_DB)


def export_ohlcv_feed(
        symbol: str, 
        interval: str, 
        start: datetime | None = None, 
        end: datetime | None = None, 
        skip_if_exists: bool = True
    ):
    db = get_default_klinedb(symbol)
    return db.export_ohlcv_file(symbol, interval, 
                                start=start, end=end, skip_if_exists=skip_if_exists)


