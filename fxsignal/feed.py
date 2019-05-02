# import numpy as np
import pandas as pd
import fxcmpy
import logging

log = logging.getLogger(__name__)

class Feed(object):
    """Abstract forex feed processor"""

    def __init__(self, symbol, start_date, end_date, period, data_dir='./data'):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.period = period
        self.data_dir = data_dir
        self.data = pd.DataFrame()


class FxcmFeed(Feed):
    """
    FXCM feed processor, requires fxcmpy
    """

    # period_list = ['m1', 'm5', 'm15', 'm30', 'H1', 'H2', 'H3', 'H4', 'H6', 'H8', 'D1', 'W1', 'M1']
    symbol_list = ['EUR/USD', 'GBP/USD', 'AUD/USD', 'NZD/USD', 'USD/CAD', 'USD/CHF', 'GBP/AUD', 'EUR/JPY', 'EUR/CHF',
                   'AUD/CAD', 'AUD/JPY', 'GBP/NZD', 'GBP/JPY', 'GBP/CHF', 'EUR/NZD', 'AUD/NZD', 'CAD/CHF', 'CAD/JPY',
                   'GBP/CHF', 'NZD/CHF']

    def __init__(self, symbol, start_date, end_date, period, fxcm_config):
        super().__init__(symbol, start_date, end_date, period)
        assert symbol in self.symbol_list, "Invalid symbol value: {}".format(symbol)
        assert period in fxcmpy.fxcmpy.PERIODS, "Invalid period value: {}".format(period)
        self.fxcm_config = fxcm_config
        self.connection = None

    def get_connection(self):
        """
        access_token: string (default: ''),
            an access token for your FXCM account.
        log_file: string (default: None),
            path of an optional log file. If not given (and not found in the
            optional configuration file), log messages are printed to stdout.
        log_level: string (default: 'warn'),
            the log level. Must be one of 'error', 'warn', 'info' or 'debug'.
            If not given (and not found in the optional configuration file),
            'warn' is used.
        server: one of 'demo' or 'real' (default: 'demo'),
            wheter to use the fxcm demo or real trading server.
        """
        return fxcmpy.fxcmpy(access_token=self.fxcm_config['access_token'], log_file=self.fxcm_config['log_file'], log_level=self.fxcm_config['log_level'], server=self.fxcm_config['server'])

    def get_feed(self):
        log.info("FXCM get_feed - symbol: {} period: {} start_date: {} end_date: {}".format(self.symbol, self.period, self.start_date, self.end_date))
        if self.connection is None:
            self.connection = self.get_connection()
        self.data = self.connection.get_candles(self.symbol, period=self.period, columns=['askopen', 'askclose', 'askhigh', 'asklow', 'tickqty'], start=self.start_date, end=self.end_date)
        #self.data['symbol'] = self.symbol
        #self.data['period'] = self.period
        self.data.reset_index(inplace=True)
        #print(self.data.info())
        #print(self.data.head(5))
        return self.data

    def read_csv(self):
        self.data = pd.read_csv(self.get_csv_filename(), sep=';', index_col=0, parse_dates=[1])
        return self.data

    def clean_data(self):
        self.history = pd.DataFrame()
        self.history = self.history.append(self.data, ignore_index = True)
        self.history.drop(self.history[self.history.tickqty < 2000].index, inplace=True)
        #print(self.history.info())
        #print(self.history.head(5))
        return self.history

    def get_csv_filename(self):
        return "{}/{}{}.csv".format(self.data_dir, self.symbol.replace('/',''),self.period)

    def save_csv(self, data):
        data.to_csv(path_or_buf=self.get_csv_filename(), sep=';', index_label='id')

    #def connect(self):
    #    self.connection.connect()

    def close(self):
        self.connection.close()
