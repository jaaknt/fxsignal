from datetime import datetime
import backtrader as bt
import backtrader.indicators as btind
import logging

from .symbol import SymbolParameter
from .base import BaseStrategy
from fxsignal.indicators.keltner import KeltnerChannels

log = logging.getLogger(__name__)

time_list = ['06:30','07:00','07:30','08:00','08:30','09:00','09:30','10:00','10:30','11:00','11:30',
             '12:00','12:30','13:00','13:30','14:00','14:30','15:00','15:30','16:00','16:30','17:00',
             '17:30','18:00']

class BasicStrategy(BaseStrategy):
    params = dict(
        symbol='GBP/USD',
        verbose=False,
        max_loss_percent = 0.01, # max risk percent from protfolio value per trade
        atr_period=14,
        vortex_period=14,
        baseline_period=20,
        macd_fast_period=3,
        macd_slow_period=10,
        macd_signal_period=16,
        keltner_atr_multiplier=2.3,
        stop1_atr_multiplier=0.8,
        target1_atr_multiplier=1.5,
        target2_atr_multiplier=0.5
    )

    def __init__(self):
        super().__init__(verbose=self.p.verbose)
        # indicators
        self.atr = btind.ATR(self.data, period=self.p.atr_period)
        self.keltner = KeltnerChannels(self.data, period=self.p.baseline_period, multiplier=self.p.keltner_atr_multiplier, atr_period=self.p.atr_period)
        self.vortex = btind.Vortex(self.data, period=self.p.vortex_period)
        self.macd = btind.MACD(self.data.close,  period_me1=self.p.macd_fast_period, period_me2=self.p.macd_slow_period, period_signal=self.p.macd_signal_period)

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
        return {#"baseline_period": [8, 15, 20, 30],
                "baseline_period": [20],
                #"atr_period": [5, 10, 14, 20],
                "atr_period": [14],
                #"vortex_period": [5, 8, 10, 14],
                "vortex_period": [14],
                "keltner_atr_multiplier": [1.5, 2.0, 2.3, 2.5],
                #"keltner_atr_multiplier": [1.3],
                "stop1_atr_multiplier": [0.6, 0.8, 1.1, 1.5],
                #"stop1_atr_multiplier": [1.0],
                "target1_atr_multiplier": [1.0, 1.3, 1.5, 1.7],
                #"target1_atr_multiplier": [1.5],
                "target2_atr_multiplier": [0.4, 0.6, 0.9],
                #"target2_atr_multiplier": [0.5]
                }

    @staticmethod
    def get_parameter_values(params, i):
        if i == 0:
            return params.baseline_period
        elif i == 1:
            return params.atr_period
        elif i == 2:
            return params.vortex_period
        elif i == 3:
            return params.keltner_atr_multiplier
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
            return 'vortex_period'
        elif i == 3:
            return 'keltner_atr_multiplier'
        elif i == 4:
            return 'stop1_atr_multiplier'
        elif i == 5:
            return 'target1_atr_multiplier'
        elif i == 6:
            return 'target2_atr_multiplier'
        else:
            return ''

    def buy_signal(self):
        if (self.data.close[0] > self.keltner.upper[0]) and (self.vortex.vi_plus[0] > self.vortex.vi_minus[0] and (self.atr[0] > 10 * self.symbol_parameter.get_pip_size())):
            if (self.macd.macd[0] > self.macd.signal[0]) and (self.data.datetime.datetime(0).strftime('%H:%M') in time_list): # and (self.data.high[0] - self.data.low[0] > self.atr[0]*1.2):
                log.debug('{} | Time {} | Macd {:.5f} | Signal {:.5f} | ATR {:.5f}'.format(
                    self.data.datetime.datetime(0), self.data.datetime.datetime(0).strftime('%H:%M'), self.macd.macd[0], self.macd.signal[0], self.atr[0]))
                return True
        return False

    def sell_signal(self):
        if (self.data.close[0] < self.keltner.lower[0]) and (self.vortex.vi_minus[0] > self.vortex.vi_plus[0] and (self.atr[0] > 10 * self.symbol_parameter.get_pip_size())):
            if (self.macd.macd[0] < self.macd.signal[0]) and (self.data.datetime.datetime(0).strftime('%H:%M') in time_list): # and (self.data.high[0] - self.data.low[0] > self.atr[0]*1.2):
                return True
        return False

    def exit_buy_signal(self):
        return False

    def exit_sell_signal(self):
        return False

    def get_stop1_price(self):
        return max(self.p.stop1_atr_multiplier * self.atr, 10 * self.symbol_parameter.get_pip_size())

    def get_target1_price(self):
        return self.p.target1_atr_multiplier * self.atr

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
