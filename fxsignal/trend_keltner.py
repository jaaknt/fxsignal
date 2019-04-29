from datetime import datetime
import backtrader as bt
import backtrader.indicators as btind

import logging

log = logging.getLogger(__name__)

currency_setup = {"EURUSD": {"pip": 0.0001, "pip_round": 4, "pip_value": 0.1},
                  "GBPUSD": {"pip": 0.0001, "pip_round": 4, "pip_value": 0.1},
                  "AUDUSD": {"pip": 0.0001, "pip_round": 4, "pip_value": 0.1},
                  "NZDUSD": {"pip": 0.0001, "pip_round": 4, "pip_value": 0.1},
                  "USDCHF": {"pip": 0.0001, "pip_round": 4, "pip_value": 0.1 / 1.00},
                  "USDCAD": {"pip": 0.0001, "pip_round": 4, "pip_value": 0.1 / 1.31}
                  }


class BasicStrategy(bt.Strategy):
    params = dict(
        currency='EURUSD',
        verbose=False,
        atr_period=14,
        stddev_period=20,
        squeeze_period=20,
        macd_fast_period=12,
        macd_slow_period=26,
        macd_signal_period=9,
        macd_ema_period=8,
        squeeze_bb_multiplier=2.0,
        squeeze_kc_multiplier=1.5,
        stop1_atr_multiplier=1.2,
        target1_atr_multiplier=1.6,
        target2_atr_multiplier=0.3
    )

    (Start, Order1Added, Order1Completed, PreTarget2, Target2) = range(5)

    def __init__(self):
        super().__init__()
        # self.ema_short = btind.MovAv.EMA(self.data.close, period=self.p.ema_short_period)
        self.atr = btind.ATR(self.data, period=self.p.atr_period)
        self.stddev = btind.StdDev(self.data.close, period=self.p.stddev_period)
        self.highest = btind.Highest(self.data.high, period=self.p.squeeze_period, plot=False)
        self.lowest = btind.Lowest(self.data.low, period=self.p.squeeze_period, plot=False)
        self.sma = btind.MovAv.SMA(self.data.close, period=self.p.squeeze_period, plot=False)
        self.mean = ((self.highest + self.lowest) / 2.0 + self.sma) / 2.0
        self.squeeze = btind.MovAv.SMA((self.data.close - self.mean) / self.data.close, period=self.p.squeeze_period)

        #    self.macd_fast   = btind.MovAv.EMA(self.data.close, period=self.p.macd_fast_period, plot=False)
        #    self.macd_slow   = btind.MovAv.EMA(self.data.close, period=self.p.macd_slow_period, plot=False)
        #    self.macd        = self.macd_fast - self.macd_slow
        #    self.macd_signal = btind.MovAv.EMA(self.macd, period=self.p.macd_signal_period, plot=False)
        #    self.macd_histogram = self.macd - self.macd_signal
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
        self.max_loss = 2000.0  # 2000 USD = 2% from 100000
        self.currency_params = currency_setup[self.p.currency]

    def notify_trade(self, trade):
        log.debug(
            '{} | Trade id: {} | Status {} | Price {:.5f}'.format(self.data.datetime.datetime(0), trade.tradeid,
                                                                  trade.status_names[trade.status], trade.price))

        if not trade.isclosed:
            return
        log.debug('{} | Trade profit, Gross {:.5f}, Net {:.5f} Start {:.5f}'.format(
            self.data.datetime.datetime(0), trade.pnl, trade.pnlcomm, trade.price))

        # self.log('Trade profit, Gross {:.5f}, Net {:.5f} Start {:.5f}'.format(
        #    trade.pnl, trade.pnlcomm, trade.price), force_print=self.p.verbose)
        # print (self.data[0])

    def notify_order(self, order):
        log.debug(
            '{} | Order ref: {} | Type {} | Status {} | Price {:.5f}'.format(self.data.datetime.datetime(0), order.ref,
                                                                             order.ordtypename(),
                                                                             order.getstatusname(),
                                                                             0.0 if order.price is None else order.price))
        if order.status == order.Margin:
            log.info('{} | MARGIN CALL Order ref: {} | Type {} | Status {} | Price {:.5f}'.format(
                self.data.datetime.datetime(0), order.ref, order.ordtypename(),
                order.getstatusname(),
                0.0 if order.price is None else order.price))

        old_stage = self.stage
        if order.status == order.Completed:
            if self.stage == self.Order1Added:
                # if order.ref != self.main_order.ref:
                #    log.error("Stage: {}, Order ref: {}, Main order ref: {}".format(self.stage, order.ref, self.main_order.ref)
                self.main_order_price = self.data.open[0]
                self.stage = self.Order1Completed
            elif order.ref == self.stop_order.ref and self.stage == self.Order1Completed:
                # self.cancel(self.limit_order)
                self.stage = self.Start
            elif order.ref == self.stop_order.ref and self.stage == self.Target2:
                self.stage = self.Start
            elif order.ref == self.limit_order.ref and self.stage == self.Order1Completed:
                # if order.ref != self.limit_order.ref:
                #    log.error("Stage: {}, Order ref: {}, Limit order ref: {}".format(self.stage, order.ref, self.limit_order.ref)
                self.stage = self.PreTarget2
            elif order.ref == self.limit_order.ref and self.stage == self.Target2:
                self.stage = self.Start

            log.debug(
                '{} | Order ref: {} | Old stage {} | New stage {} | Price {:.5f} | Commission: {:.5f} Size: {:.0f}'.format(
                    self.data.datetime.datetime(0), order.ref,
                    old_stage,
                    self.stage,
                    order.executed.price,
                    order.executed.comm,
                    order.executed.size))
            # order.executed.value

    def next(self):
        pass

    def stop(self):
        # if self.broker.getvalue() > 11000:
        log.info('datetime: {} Ending Value {:.2f}'.format(
            self.data.datetime.datetime(0),
            self.broker.getvalue()))

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

    @staticmethod
    def get_algorithm_name():
        return 'trendkeltner'


class BuyStrategy(BasicStrategy):

    def __init__(self):
        super().__init__()

    def next(self):
        if not self.position and self.stage == self.Start:
            if self.stddev * self.p.squeeze_bb_multiplier > self.atr * self.p.squeeze_kc_multiplier:
                #log.debug('{} | stddev: {:.5f} | k*stddev: {:.5f} | atr {:.5f} | m*atr {:.5f}'.format(
                #    self.data.datetime.datetime(0), self.stddev[0], self.stddev[0] * self.p.squeeze_bb_multiplier,
                #    self.atr[0], self.atr[0] * self.p.squeeze_kc_multiplier))
                #log.debug('{} | squeeze[0]: {} | squeeze[1]: {} | squeeze[2] {}'.format(self.data.datetime.datetime(0),
                #                                                                        self.squeeze[0],
                #                                                                        self.squeeze[1],
                #                                                                        self.squeeze[2]))
                #log.debug('{} | histo[0]: {:.5f} | .histo[-1]: {:.5f}'.format(self.data.datetime.datetime(0),
                #                                                              self.macd.histo[0], self.macd.histo[-1]))
                # and self.squeeze[-1] > self.squeeze[-2]
                if (self.macd_ema[0] > self.macd_ema[-1] and self.macd.histo[0] > self.macd.histo[-1]) and (
                        self.squeeze[0] > self.squeeze[-1] and self.squeeze[-1] > self.squeeze[-2]):
                    stop1_price = self.data.close - self.p.stop1_atr_multiplier * self.atr
                    self.target1_price = self.data.close + self.p.target1_atr_multiplier * self.atr

                    loss_pips = round(self.p.stop1_atr_multiplier * self.atr, self.currency_params['pip_round']) / \
                                self.currency_params['pip']
                    self.size = max(round(self.max_loss / (loss_pips * self.currency_params['pip_value']), 0), 1) * 1000
                    log.debug('{} loss_pips: {:.0f} size: {:.0f} atr: {:.5f} multiplier: {:.2f}'.format(
                        self.data.datetime.datetime(0), loss_pips, self.size, self.atr[0], self.p.stop1_atr_multiplier))

                    self.main_order = self.buy(exectype=bt.Order.Market, price=None, size=self.size, transmit=True)
                    self.stop_order = self.sell(exectype=bt.Order.Stop,
                                                price=stop1_price,
                                                size=self.size,
                                                transmit=True)
                    self.limit_order = self.sell(exectype=bt.Order.Limit,
                                                 price=self.target1_price,
                                                 size=self.size / 2,
                                                 transmit=True,
                                                 oco=self.stop_order)
                    self.stage = self.Order1Added
                    log.debug('{} Close: {:.5f} Open: {:.5f}'.format(self.data.datetime.datetime(0), self.data.close[0],
                                                                     self.data.open[0]))
        elif self.stage == self.PreTarget2:
            self.stop_order = self.sell(exectype=bt.Order.Stop,
                                        price=self.main_order_price + 10 * self.currency_params['pip'],
                                        size=self.size / 2,
                                        transmit=True)
            self.limit_order = self.sell(exectype=bt.Order.Limit,
                                         price=self.target1_price + self.p.target2_atr_multiplier * self.atr,
                                         size=self.size / 2,
                                         transmit=True,
                                         oco=self.stop_order)
            self.stage = self.Target2
        #    elif self.stage == self.Target2 and self.data.close < self.ema_short:
        #        self.exit_order = self.sell(exectype=bt.Order.Market, price=None, size=15000, transmit=True)
        #        self.cancel(self.stop_order)
        #        self.stage = self.Start
        else:
            pass


class SellStrategy(BasicStrategy):

    def __init__(self):
        super().__init__()

    def next(self):
        if not self.position and self.stage == self.Start:
            if self.stddev * self.p.squeeze_bb_multiplier > self.atr * self.p.squeeze_kc_multiplier:
                #log.debug('{} | stddev: {:.5f} | k*stddev: {:.5f} | atr {:.5f} | m*atr {:.5f}'.format(
                #    self.data.datetime.datetime(0), self.stddev[0], self.stddev[0] * self.p.squeeze_bb_multiplier,
                #    self.atr[0], self.atr[0] * self.p.squeeze_kc_multiplier))
                #log.debug('{} | squeeze[0]: {} | squeeze[1]: {} | squeeze[2] {}'.format(self.data.datetime.datetime(0),
                #                                                                        self.squeeze[0],
                #                                                                        self.squeeze[1],
                #                                                                        self.squeeze[2]))
                #log.debug('{} | histo[0]: {:.5f} | .histo[-1]: {:.5f}'.format(self.data.datetime.datetime(0),
                #                                                              self.macd.histo[0], self.macd.histo[-1]))
                # and self.squeeze[-1] > self.squeeze[-2]
                if (self.macd_ema[0] < self.macd_ema[-1] and self.macd.histo[0] < self.macd.histo[-1]) and (
                        self.squeeze[0] < self.squeeze[-1] and self.squeeze[-1] < self.squeeze[-2]):
                    stop1_price = self.data.close + self.p.stop1_atr_multiplier * self.atr
                    self.target1_price = self.data.close - self.p.target1_atr_multiplier * self.atr

                    loss_pips = round(self.p.stop1_atr_multiplier * self.atr, self.currency_params['pip_round']) / \
                                self.currency_params['pip']
                    self.size = max(round(self.max_loss / (loss_pips * self.currency_params['pip_value']), 0), 1) * 1000
                    log.debug('{} loss_pips: {:.0f} size: {:.0f} atr: {:.5f} multiplier: {:.2f}'.format(
                        self.data.datetime.datetime(0), loss_pips, self.size, self.atr[0], self.p.stop1_atr_multiplier))

                    self.main_order = self.sell(exectype=bt.Order.Market, price=None, size=self.size, transmit=True)
                    self.stop_order = self.buy(exectype=bt.Order.Stop,
                                               price=stop1_price,
                                               size=self.size,
                                               transmit=True)
                    self.limit_order = self.buy(exectype=bt.Order.Limit,
                                                price=self.target1_price,
                                                size=self.size / 2,
                                                transmit=True,
                                                oco=self.stop_order)
                    self.stage = self.Order1Added
                    log.debug('{} Close: {:.5f} Open: {:.5f}'.format(self.data.datetime.datetime(0), self.data.close[0],
                                                                     self.data.open[0]))
        elif self.stage == self.PreTarget2:
            self.stop_order = self.buy(exectype=bt.Order.Stop,
                                       price=self.main_order_price - 10 * self.currency_params['pip'],
                                       size=self.size / 2,
                                       transmit=True)
            self.limit_order = self.buy(exectype=bt.Order.Limit,
                                        price=self.target1_price - self.p.target2_atr_multiplier * self.atr,
                                        size=self.size / 2,
                                        transmit=True,
                                        oco=self.stop_order)
            self.stage = self.Target2
        #    elif self.stage == self.Target2 and self.data.close < self.ema_short:
        #        self.exit_order = self.sell(exectype=bt.Order.Market, price=None, size=15000, transmit=True)
        #        self.cancel(self.stop_order)
        #        self.stage = self.Start
        else:
            pass
