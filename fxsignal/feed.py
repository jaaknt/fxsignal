import numpy as np
import pandas as pd
import fxcmpy

class Feed(object):
    """Abstract forex feed processor"""

    def __init__(self, symbol, start_date, end_date, period):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.period = period

    def get_connection():
        raise NotImplementedError

    def get_data():
        raise NotImplementedError

    def save_csv():
        raise NotImplementedError

class FxcmFeed(Feed):
    """
    FXCM feed processor, requires fxcmpy
    """

    period_list = ['m1', 'm5', 'm15', 'm30', 'H1', 'H2', 'H3', 'H4', 'H6', 'H8', 'D1', 'W1', 'M1']
    symbol_list = ['EUR/USD', 'GBP/USD', 'AUD/USD', 'NZD/USD', 'USD/CAD', 'USD/CHF', 'GBP/AUD', 'EUR/JPY', 'EUR/CHF',
                   'AUD/CAD', 'AUD/JPY', 'GBP/NZD', 'GBP/JPY', 'GBP/CHF', 'EUR/NZD', 'AUD/NZD', 'CAD/CHF', 'CAD/JPY',
                   'GBP/CHF', 'NZD/CHF']

    def __init__(self, symbol, start_date, end_date, period, config):
        super().__init__(symbol, start_date, end_date, period)
        assert symbol in self.symbol_list, "Invalid symbol value: {}".format(symbol)
        assert period in self.period_list, "Invalid period value: {}".format(period)
        self.config = config

    def get_connection():
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
        self.connection = fxcmpy.fxcmpy(access_token=self.config['access_token'], log_file=self.config['log_file'], log_level=self.config['log_level'], server=self['config.server'])
