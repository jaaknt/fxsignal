from datetime import datetime
import backtrader as bt
import backtrader.indicators as btind

import logging

log = logging.getLogger(__name__)

# micro lot =      1000
# mini lot =      10000
# standard lot = 100000
# https://www.investing.com/tools/forex-pip-calculator
symbol_setup =   {'AUD/CAD': {'pip': 0.0001, 'pip_round': 4, 'pip_value': 0.08},
                  'AUD/CHF': {'pip': 0.0001, 'pip_round': 4, 'pip_value': 0.10},
                  'AUD/JPY': {'pip': 0.01,   'pip_round': 2, 'pip_value': 0.09},
                  'AUD/NZD': {'pip': 0.0001, 'pip_round': 4, 'pip_value': 0.07},
                  'AUD/USD': {'pip': 0.0001, 'pip_round': 4, 'pip_value': 0.10},
                  'CAD/CHF': {'pip': 0.0001, 'pip_round': 4, 'pip_value': 0.10},
                  'CAD/JPY': {'pip': 0.01,   'pip_round': 2, 'pip_value': 0.09},
                  'CHF/JPY': {'pip': 0.01,   'pip_round': 2, 'pip_value': 0.09},
                  'EUR/AUD': {'pip': 0.0001, 'pip_round': 4, 'pip_value': 0.07},
                  'EUR/CAD': {'pip': 0.0001, 'pip_round': 4, 'pip_value': 0.08},
                  'EUR/CHF': {'pip': 0.0001, 'pip_round': 4, 'pip_value': 0.10},
                  'EUR/GBP': {'pip': 0.0001, 'pip_round': 4, 'pip_value': 0.13},
                  'EUR/JPY': {'pip': 0.01,   'pip_round': 2, 'pip_value': 0.09},
                  'EUR/NZD': {'pip': 0.0001, 'pip_round': 4, 'pip_value': 0.07},
                  'EUR/USD': {'pip': 0.0001, 'pip_round': 4, 'pip_value': 0.10},
                  'GBP/AUD': {'pip': 0.0001, 'pip_round': 4, 'pip_value': 0.07},
                  'GBP/CAD': {'pip': 0.0001, 'pip_round': 4, 'pip_value': 0.08},
                  'GBP/CHF': {'pip': 0.0001, 'pip_round': 4, 'pip_value': 0.10},
                  'GBP/JPY': {'pip': 0.01,   'pip_round': 2, 'pip_value': 0.09},
                  'GBP/NZD': {'pip': 0.0001, 'pip_round': 4, 'pip_value': 0.07},
                  'GBP/USD': {'pip': 0.0001, 'pip_round': 4, 'pip_value': 0.10},
                  'NZD/CHF': {'pip': 0.0001, 'pip_round': 4, 'pip_value': 0.10},
                  'NZD/JPY': {'pip': 0.01,   'pip_round': 2, 'pip_value': 0.09},
                  'NZD/USD': {'pip': 0.0001, 'pip_round': 4, 'pip_value': 0.10},
                  'USD/CAD': {'pip': 0.0001, 'pip_round': 4, 'pip_value': 0.08}, #0.1 / 1.30
                  'USD/CHF': {'pip': 0.0001, 'pip_round': 4, 'pip_value': 0.10}, # 0.1 / 1.00
                  'USD/JPY': {'pip': 0.01,   'pip_round': 2, 'pip_value': 0.09} # 10.0 / 110.0
                  }

class SymbolParameter(object):
    """Symbol parameters and size calculator"""

    def __init__(self, symbol, cash, max_loss_percent):
        self.symbol = symbol
        self.cash = cash
        self.max_loss_percent = max_loss_percent

    def set_cash(self, cash):
        self.cash = cash

    def get_size(self, forex_amount):
        """ Calculate trade size by stoploss pips and max loss percent from trade account balance"""
        pips = round(forex_amount / symbol_setup[self.symbol]['pip'],0)
        # log.info('pips: {:.5f} | max loss: {:.5f} | pip value: {:.5f}'.format(pips, self.cash * self.max_loss_percent, pips * symbol_setup[self.symbol]['pip_value']))
        return round((self.cash * self.max_loss_percent) / (pips * symbol_setup[self.symbol]['pip_value']), 2) * 1000

    def get_pip_size(self):
        return symbol_setup[self.symbol]['pip']
