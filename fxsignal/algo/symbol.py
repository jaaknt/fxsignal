from datetime import datetime
import backtrader as bt
import backtrader.indicators as btind

import logging

log = logging.getLogger(__name__)

symbol_setup =   {"EUR/USD": {"pip": 0.0001, "pip_round": 4, "pip_value": 0.1},
                  "GBP/USD": {"pip": 0.0001, "pip_round": 4, "pip_value": 0.1},
                  "AUD/USD": {"pip": 0.0001, "pip_round": 4, "pip_value": 0.1},
                  "NZD/USD": {"pip": 0.0001, "pip_round": 4, "pip_value": 0.1},
                  "USD/CHF": {"pip": 0.0001, "pip_round": 4, "pip_value": 0.1 / 1.00},
                  "USD/CAD": {"pip": 0.0001, "pip_round": 4, "pip_value": 0.1 / 1.31},
                  "USD/JPY": {"pip": 0.01,   "pip_round": 2, "pip_value": 10.0 / 110.0}
                  }


class SymbolParameter(object):
    """Symbol parameters and sizer calculator"""

    def __init__(self, symbol, cash, max_loss_percent):
        self.symbol = symbol
        self.cash = cash
        self.max_loss_percent = max_loss_percent

    def set_cash(self, cash):
        self.cash = cash

    def get_size(self, forex_amount):
        pips = round(forex_amount / symbol_setup[self.symbol]['pip'],5)
        return max(round((self.cash * self.max_loss_percent) / (pips * symbol_setup[self.symbol]['pip_value']), 2), 1.0) * 1000

    def get_pip_size(self):
        return symbol_setup[self.symbol]['pip']
