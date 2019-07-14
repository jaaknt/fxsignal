from datetime import datetime
import backtrader as bt
#import backtrader.indicators as btind

import logging

log = logging.getLogger(__name__)

class BaseStrategy(bt.Strategy):

    (Start, Order1Added, Order1Completed, PreTarget2, Target2, ExitOrderAdded) = range(6)

    def __init__(self, verbose=False):
        super().__init__()
        if verbose:
            log.setLevel(logging.DEBUG)

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
        if order.price is not None and order.price != 0.0:
            price = order.price
        elif order.executed.price is not None and order.executed.price != 0.0:
            price = order.executed.price
        else:
            price = self.data.open[0]

        log.debug(
            '{} | Order ref: {} | Type {} | Status {} | Price {:.5f}'.format(self.data.datetime.datetime(0), order.ref,
                                                                             order.ordtypename(), order.getstatusname(), price))
        if order.status == order.Margin:
            log.info('{} | MARGIN CALL Order ref: {} | Type {} | Status {} | Price {:.5f}'.format(
                self.data.datetime.datetime(0), order.ref, order.ordtypename(),
                order.getstatusname(), price))

        old_stage = self.stage
        if order.status == order.Completed:
            if self.stage == self.Order1Added:
                # if order.ref != self.main_order.ref:
                #    log.error("Stage: {}, Order ref: {}, Main order ref: {}".format(self.stage, order.ref, self.main_order.ref)
                self.main_order_price = order.executed.price # self.data.open[0]
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
            elif order.ref == self.exit_order.ref and self.stage == self.ExitOrderAdded:
                self.stage = self.Start
            else:
                log.info(
                    '{} | Unknown stage Order ref: {} | Old stage {} | New stage {} | Price {:.5f} | Size: {:.0f}'.format(
                        self.data.datetime.datetime(0), order.ref,
                        old_stage,
                        self.stage,
                        price,
                        order.executed.size))

            log.debug(
                '{} | Order ref: {} | Old stage {} | New stage {} | Price {:.5f} | Size: {:.0f}'.format(
                    self.data.datetime.datetime(0), order.ref,
                    old_stage,
                    self.stage,
                    price,
                    order.executed.size))
            # order.executed.value

    def next(self):
        pass

    def stop(self):
        pass
        # if self.broker.getvalue() > 11000:
        #log.info('datetime: {} Ending Value {:.2f}'.format(
        #    self.data.datetime.datetime(0),
        #    self.broker.getvalue()))


    def buy_signal(self):
        return False

    def sell_signal(self):
        return False

    def exit_buy_signal(self):
        return False

    def exit_sell_signal(self):
        return False

    def get_stop1_price(self):
        pass

    def get_target1_price(self):
        pass

    def get_stop2_price(self):
        pass

    def get_target2_price(self):
        pass

    def next_buy_v1(self):

        if self.position and self.stage == self.Start:
            log.error("{} Stage is not correct: {} Main: {} Stop: {} Limit: {} Exit: {}".format(self.data.datetime.datetime(0), self.stage,
                self.main_order.getstatusname(), self.stop_order.getstatusname(), self.limit_order.getstatusname(),
                'None' if self.exit_order is None else self.exit_order.getstatusname()))

        old_stage = self.stage
        if not self.position and self.stage == self.Start:
            if self.buy_signal():
                stop1_price = self.data.close - self.get_stop1_price()
                self.target1_price = self.data.close + self.get_target1_price()

                self.size = self.symbol_parameter.get_size(self.get_stop1_price())
                #log.debug('{} size: {:.0f} atr: {:.5f} multiplier: {:.2f}'.format(
                #    self.data.datetime.datetime(0), self.size, self.atr[0], self.p.stop1_atr_multiplier))

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
                #log.debug('{} Close: {:.5f} Open: {:.5f}'.format(self.data.datetime.datetime(0), self.data.close[0],
                #                                                     self.data.open[0]))
                log.debug('{} | next | Old stage {} | New stage {}'.format(self.data.datetime.datetime(0), old_stage, self.stage))
        elif self.stage == self.PreTarget2:
            self.stop_order = self.sell(exectype=bt.Order.Stop,
                                        price=self.main_order_price + self.get_stop2_price(),
                                        size=self.size / 2,
                                        transmit=True)
            self.limit_order = self.sell(exectype=bt.Order.Limit,
                                         price=self.target1_price + self.get_target2_price(),
                                         size=self.size / 2,
                                         transmit=True,
                                         oco=self.stop_order)
            self.stage = self.Target2
            log.debug('{} | next | Old stage {} | New stage {}'.format(self.data.datetime.datetime(0), old_stage, self.stage))
        elif self.stage in [self.Target2, self.Order1Completed] and self.exit_buy_signal():
            self.cancel(self.stop_order)
            self.exit_order = self.sell(exectype=bt.Order.Market, price=None, size=self.size if self.stage == self.Order1Completed else self.size / 2, transmit=True)
            self.stage = self.ExitOrderAdded
        else:
            log.debug('{} | next | Old stage {} | New stage {}'.format(self.data.datetime.datetime(0), old_stage, self.stage))
            pass


    def next_sell_v1(self):

        if self.position and self.stage == self.Start:
            log.error("{} Stage is not correct: {} Main: {} Stop: {} Limit: {} Exit: {}".format(self.data.datetime.datetime(0), self.stage,
                self.main_order.getstatusname(), self.stop_order.getstatusname(), self.limit_order.getstatusname(),
                'None' if self.exit_order is None else self.exit_order.getstatusname()))

        old_stage = self.stage
        if not self.position and self.stage == self.Start:
            if self.sell_signal():
                stop1_price = self.data.close + self.get_stop1_price()
                self.target1_price = self.data.close - self.get_target1_price()

                self.size = self.symbol_parameter.get_size(self.get_stop1_price())
                # log.debug('{} size: {:.0f} atr: {:.5f} multiplier: {:.2f}'.format(
                #    self.data.datetime.datetime(0), self.size, self.atr[0], self.p.stop1_atr_multiplier))

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
                #log.debug('{} Close: {:.5f} Open: {:.5f}'.format(self.data.datetime.datetime(0), self.data.close[0],
                #                                                 self.data.open[0]))
                log.debug('{} | next | Old stage {} | New stage {}'.format(self.data.datetime.datetime(0), old_stage, self.stage))
        elif self.stage == self.PreTarget2:
            self.stop_order = self.buy(exectype=bt.Order.Stop,
                                       price=self.main_order_price - self.get_stop2_price(),
                                       size=self.size / 2,
                                       transmit=True)
            self.limit_order = self.buy(exectype=bt.Order.Limit,
                                        price=self.target1_price - self.get_target2_price(),
                                        size=self.size / 2,
                                        transmit=True,
                                        oco=self.stop_order)
            self.stage = self.Target2
            log.debug('{} | next | Old stage {} | New stage {}'.format(self.data.datetime.datetime(0), old_stage, self.stage))
        elif self.stage in [self.Target2, self.Order1Completed] and self.exit_sell_signal():
            self.cancel(self.stop_order)
            self.exit_order = self.buy(exectype=bt.Order.Market, price=None, size = self.size if self.stage == self.Order1Completed else self.size / 2, transmit=True)
            self.stage = self.ExitOrderAdded
            log.debug('{} | next | Old stage {} | New stage {}'.format(self.data.datetime.datetime(0), old_stage, self.stage))
        else:
            pass
