from datetime import datetime
import backtrader as bt
import backtrader.indicators as btind

from .symbol import SymbolParameter
from .base import BaseStrategy

import logging

log = logging.getLogger(__name__)


class BasicStrategy(BaseStrategy):
    params = dict(
        symbol='EUR/USD',
        verbose=False,
        decision_analyzer=True,
        max_loss_percent = 0.02, # max risk percent from protfolio value per trade
        wma_period=22,
        hma_period=17,
        atr_period=14,
        stddev_period=20,
        squeeze_period=20,
        macd_fast_period=12,
        macd_slow_period=26,
        macd_signal_period=9,
        macd_ema_period=13,
        squeeze_bb_multiplier=2.0,
        squeeze_kc_multiplier=1.5,
        stop1_atr_multiplier=1.5,
        target1_atr_multiplier=1.0,
        target2_atr_multiplier=2.0
    )

    def __init__(self):
        super().__init__(verbose=self.p.verbose)
        if self.p.verbose:
            log.setLevel(logging.DEBUG)
        self.hlc3 = (self.data.high + self.data.low + self.data.close)/3
        self.baseline = btind.WMA(self.hlc3, period = self.p.wma_period)
        self.exit = btind.HMA(self.hlc3, period = self.p.hma_period)
        self.atr = btind.ATR(self.data, period=self.p.atr_period)
        self.stddev = btind.StdDev(self.data.close, period=self.p.stddev_period)
        self.highest = btind.Highest(self.data.high, period=self.p.squeeze_period, plot=False)
        self.lowest = btind.Lowest(self.data.low, period=self.p.squeeze_period, plot=False)
        self.sma = btind.MovAv.SMA(self.data.close, period=self.p.squeeze_period, plot=False)
        self.mean = ((self.highest + self.lowest) / 2.0 + self.sma) / 2.0
        self.squeeze = btind.MovAv.SMA((self.data.close - self.mean) / self.data.close, period=self.p.squeeze_period)

        self.macd = btind.MACDHisto(self.data.close, period_me1=self.p.macd_fast_period,
                                    period_me2=self.p.macd_slow_period, period_signal=self.p.macd_signal_period)

        self.macd_ema = btind.MovAv.EMA(self.data.close, period=self.p.macd_ema_period)
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
        return {"wma_period": [17, 19, 21, 23],
                "stop1_atr_multiplier": [0.8, 1.0, 1.2, 1.5],
                "target1_atr_multiplier": [1.0, 1.2, 1.4],
                "target2_atr_multiplier": [0.2, 0.6, 1.0],
                "squeeze_kc_multiplier": [1.5]
                }

    @staticmethod
    def get_parameter_values(params, i):
        if i == 0:
            return params.wma_period
        elif i == 1:
            return params.stop1_atr_multiplier
        elif i == 2:
            return params.target1_atr_multiplier
        elif i == 3:
            return params.target2_atr_multiplier
        elif i == 4:
            return params.squeeze_kc_multiplier
        else:
            return ''

    @staticmethod
    def get_parameter_keys(params, i):
        if i == 0:
            return 'wma_period'
        elif i == 1:
            return 'stop1_atr_multiplier'
        elif i == 2:
            return 'target1_atr_multiplier'
        elif i == 3:
            return 'target2_atr_multiplier'
        elif i == 4:
            return 'squeeze_kc_multiplier'
        else:
            return ''

    @staticmethod
    def get_algorithm_name():
        return 'trend_hma'

    def buy_signal(self):
        if self.data.close[0] > self.baseline[0]: #and self.baseline[0] > self.baseline[-1]:
            #if self.stddev[0] * self.p.squeeze_bb_multiplier > self.atr[0] * self.p.squeeze_kc_multiplier:
            if (self.macd_ema[0] > self.macd_ema[-1] and self.macd.histo[0] > self.macd.histo[-1]) and (self.squeeze[0] > self.squeeze[-1]):
                return True
        return False

    def sell_signal(self):
        if self.data.close[0] < self.baseline[0]: # and self.baseline[0] < self.baseline[-1]:
            #if self.stddev * self.p.squeeze_bb_multiplier > self.atr * self.p.squeeze_kc_multiplier:
            if (self.macd_ema[0] < self.macd_ema[-1] and self.macd.histo[0] < self.macd.histo[-1]) and (self.squeeze[0] < self.squeeze[-1]):
                return True
        return False

    def exit_buy_signal(self):
        return False
#        if self.stage == self.Order1Completed:
#            return self.data.high < self.exit or self.data.close < self.baseline
        if self.stage == self.Target2:
            return self.data.high[0] < self.exit[0] or self.data.close[0] < self.baseline[0]
        return False

    def exit_sell_signal(self):
        return False
#        if self.stage == self.Order1Completed:
#            return self.data.low > self.exit or self.data.close > self.baseline
        if self.stage == self.Target2:
            return self.data.low[0] > self.exit[0] or self.data.close[0] > self.baseline[0]
        return False

    def get_stop1_price(self):
        return self.p.stop1_atr_multiplier * self.atr

    def get_target1_price(self):
        return self.p.target1_atr_multiplier * self.atr

    def get_stop2_price(self):
        return 10 * self.symbol_parameter.get_pip_size()

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
