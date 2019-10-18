from datetime import datetime
import backtrader as bt
import backtrader.indicators as btind
import logging

from .symbol import SymbolParameter
from .base import BaseStrategy

log = logging.getLogger(__name__)

class BasicStrategy(BaseStrategy):
    params = dict(
        symbol='GBP/USD',
        verbose=False,
        max_loss_percent = 0.01, # max risk percent from protfolio value per trade
        atr_period=9,
        baseline_period=23,
        breakout_period=10,
        volatility_atr_multiplier=1.3,
        stop1_atr_multiplier=1.0,
        target1_atr_multiplier=1.5,
        target2_atr_multiplier=0.5
    )

    def __init__(self):
        super().__init__(verbose=self.p.verbose)
        if self.p.verbose:
            log.setLevel(logging.DEBUG)
        # indicators
        self.atr = btind.ATR(self.data, period=self.p.atr_period)
        self.hlc3 = (self.data.high + self.data.low + self.data.close)/3
        self.baseline = btind.WMA(self.hlc3, period=self.p.baseline_period)
        self.highest_close = btind.Highest(self.data.close, period=self.p.breakout_period)
        self.lowest_close = btind.Lowest(self.data.close, period=self.p.breakout_period)

        self.stage = self.Start
        self.main_order = None
        self.stop_order = None
        self.limit_order = None
        self.exit_order = None
        self.main_order_price = None
        self.target1_price = None
        self.size = None
        self.symbol_parameter = SymbolParameter(self.p.symbol, self.broker.get_cash(), self.p.max_loss_percent)


    @staticmethod
    def get_parameter_list():
        return {"baseline_period": [15, 18, 23, 30],
                #"baseline_period": [23],
                "atr_period": [5, 9, 14],
                #"atr_period": [9],
                "breakout_period": [5, 8, 10, 12, 15],
                #"breakout_period": [10],
                "volatility_atr_multiplier": [1.0, 1.3, 1.5, 1.7, 2.0],
                #"volatility_atr_multiplier": [1.3],
                "stop1_atr_multiplier": [0.6, 0.8, 1.0, 1.2, 1.5],
                #"stop1_atr_multiplier": [1.0],
                "target1_atr_multiplier": [1.0, 1.3, 1.5, 1.7, 2.0],
                #"target1_atr_multiplier": [1.5],
                "target2_atr_multiplier": [0.2, 0.5, 1.0, 1.5, 2.0],
                #"target2_atr_multiplier": [0.5]
                }

    @staticmethod
    def get_parameter_values(params, i):
        if i == 0:
            return params.baseline_period
        elif i == 1:
            return params.atr_period
        elif i == 2:
            return params.breakout_period
        elif i == 3:
            return params.volatility_atr_multiplier
        elif i == 4:
            return params.stop1_atr_multiplier
        elif i == 5:
            return params.target1_atr_multiplier
        elif i == 6:
            return params.target2_atr_multiplier
        else:
            return ''

    @staticmethod
    def get_parameter_keys(params, i):
        if i == 0:
            return 'baseline_period'
        elif i == 1:
            return 'atr_period'
        elif i == 2:
            return 'breakout_period'
        elif i == 3:
            return 'volatility_atr_multiplier'
        elif i == 4:
            return 'stop1_atr_multiplier'
        elif i == 5:
            return 'target1_atr_multiplier'
        elif i == 6:
            return 'target2_atr_multiplier'
        else:
            return ''

    def buy_signal(self):
        if (self.data.close[0] > self.baseline[0]) and (self.data.close[0] > self.highest_close[-1]) and (self.atr[0] > 10 * self.symbol_parameter.get_pip_size()):
            if (self.data.high[0] - self.data.low[0] > self.atr[0] * self.p.volatility_atr_multiplier) and (self.data.datetime.datetime(0).strftime('%H:%M') in ['06:30','07:00','07:30','08:00','08:30']) and (self.data.high[0] - self.data.low[0] > 0.0010):
                log.debug('{} | Time {} | High - Low{:.5f} | ATR {:.5f}'.format(
                    self.data.datetime.datetime(0), self.data.datetime.datetime(0).strftime('%H:%M'), self.data.high[0] - self.data.low[0], self.atr[0]))
                return True
        return False

    def sell_signal(self):
        if (self.data.close[0] < self.baseline[0]) and (self.data.close[0] < self.lowest_close[-1]) and (self.atr[0] > 10 * self.symbol_parameter.get_pip_size()):
            if (self.data.high[0] - self.data.low[0] > self.atr[0] * self.p.volatility_atr_multiplier) and (self.data.datetime.datetime(0).strftime('%H:%M') in ['06:30','07:00','07:30','08:00','08:30']) and (self.data.high[0] - self.data.low[0] > 0.0010):
                return True
        return False

    def exit_buy_signal(self):
        return False

    def exit_sell_signal(self):
        return False

    def get_stop1_price(self):
        return max(self.p.stop1_atr_multiplier * self.atr[0], 10 * self.symbol_parameter.get_pip_size())

    def get_target1_price(self):
        return self.p.target1_atr_multiplier * self.atr[0]

    def get_stop2_price(self):
        return 3 * self.symbol_parameter.get_pip_size()

    def get_target2_price(self):
        return self.p.target2_atr_multiplier * self.atr

class BuyStrategy(BasicStrategy):

    def __init__(self):
        super().__init__()

    def next(self):
        self.next_buy_v1()


class SellStrategy(BasicStrategy):

    def __init__(self):
        super().__init__()

    def next(self):
        self.next_sell_v1()
