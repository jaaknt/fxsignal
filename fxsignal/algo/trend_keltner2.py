from datetime import datetime
import backtrader as bt
import backtrader.indicators as btind
import logging

from .symbol import SymbolParameter
from .base import BaseStrategy

log = logging.getLogger(__name__)

class BasicStrategy(BaseStrategy):
    params = dict(
        symbol='EUR/USD',
        verbose=False,
        max_loss_percent = 0.02, # max risk percent from protfolio value per trade
        atr_period=14,
        stddev_period=20,
        squeeze_period=20,
        macd_fast_period=12,
        macd_slow_period=26,
        macd_signal_period=9,
        macd_ema_period=8,
        squeeze_bb_multiplier=2.0,
        squeeze_kc_multiplier=1.6,
        stop1_atr_multiplier=1.0,
        target1_atr_multiplier=1.2,
        target2_atr_multiplier=0.4
    )

    def __init__(self):
        super().__init__(verbose=self.p.verbose)
        # self.ema_short = btind.MovAv.EMA(self.data.close, period=self.p.ema_short_period)
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
        return {"macd_ema_period": [8, 10],
                "stop1_atr_multiplier": [0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5],
                "target1_atr_multiplier": [1.2, 1.3, 1.4, 1.5, 1.6],
                "target2_atr_multiplier": [0.2, 0.4, 0.6, 0.8, 1.0],
                "squeeze_kc_multiplier": [1.5, 1.6, 1.7]
                }

    @staticmethod
    def get_parameter_values(params, i):
        if i == 0:
            return params.macd_ema_period
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
            return 'macd_ema_period'
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

    def buy_signal(self):
        if self.stddev * self.p.squeeze_bb_multiplier > self.atr * self.p.squeeze_kc_multiplier:
            if (self.macd_ema[0] > self.macd_ema[-1] and self.macd.histo[0] > self.macd.histo[-1]) and \
               (self.squeeze[0] > self.squeeze[-1]):
                return True
        return False

    def sell_signal(self):
        if self.stddev * self.p.squeeze_bb_multiplier > self.atr * self.p.squeeze_kc_multiplier:
            if (self.macd_ema[0] < self.macd_ema[-1] and self.macd.histo[0] < self.macd.histo[-1]) and (
                    self.squeeze[0] < self.squeeze[-1]):
                return True
        return False

    def exit_buy_signal(self):
        return False

    def exit_sell_signal(self):
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
