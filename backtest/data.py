# Copyright (c) 2021 Oleg Polakow. All rights reserved.

"""Custom data classes that subclass `vectorbt.data.base.Data`."""
import pandas as pd
from vectorbt import _typing as tp
from vectorbt.data.base import Data
from vectorbt.utils.datetime_ import (
    datetime_to_ms
)
from backtest.db import get_default_klinedb


BinanceDataT = tp.TypeVar("BinanceDataT", bound="BinanceData")


class BinanceData(Data):
    """load binace data from sqlitedb"""
    @classmethod
    def load(cls: tp.Type[BinanceDataT],
                 symbols: tp.Labels,
                 interval: str = '1d',
                 start = None,
                 end = None,
                 **kwargs) -> BinanceDataT:
        """Load data from sqlite3 db"""
        data = dict()
        st = datetime_to_ms(start) if start else 0
        et = datetime_to_ms(end) if end else 0
        if st > 0 and et > 0:
            sql = f'select * from k{interval} where s >= {st} and s < {et} order by s;'
        elif st > 0:
            sql = f'select * from k{interval} where s >= {st} order by s;'
        elif et > 0:
            sql = f'select * from k{interval} where s < {et} order by s;'
        else:
            sql = f'select * from k{interval} order by s;'
        # Create for all
        for s in symbols:
            # Select keyword arguments for this symbol
            kdb = get_default_klinedb(s)
            engine = kdb.create_engine(echo=False)
            df = pd.read_sql(sql, engine)
            # Convert data to a DataFrame
            df = df.rename(columns={
                's': 'Open time',
                'o': 'Open',
                'h': 'High',
                'l': 'Low',
                'c': 'Close',
                'bv': 'Volume',
                'e': 'Close time',
                'qv': 'Quote volume',
                'n': 'Number of trades',
                'tbbv': 'Taker base volume',
                'tbqv': 'Taker quote volume',
                'i': 'Ignore'
            })
            df.index = pd.to_datetime(df['Open time'], unit='ms', utc=True)
            del df['Open time']
            df['Open'] = df['Open'].astype(float)
            df['High'] = df['High'].astype(float)
            df['Low'] = df['Low'].astype(float)
            df['Close'] = df['Close'].astype(float)
            df['Volume'] = df['Volume'].astype(float)
            df['Close time'] = pd.to_datetime(df['Close time'], unit='ms', utc=True)
            df['Quote volume'] = df['Quote volume'].astype(float)
            df['Number of trades'] = df['Number of trades'].astype(int)
            df['Taker base volume'] = df['Taker base volume'].astype(float)
            df['Taker quote volume'] = df['Taker quote volume'].astype(float)
            del df['Ignore']
            
            data[s] = df

        # Create new instance from data
        return cls.from_data(
            data,
            # tz_localize=tz_localize,
            # tz_convert=tz_convert,
            # missing_index=missing_index,
            # missing_columns=missing_columns,
            # wrapper_kwargs=wrapper_kwargs,
            download_kwargs=kwargs
        )