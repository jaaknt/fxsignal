import argparse
import logging
import os

from datetime import datetime
import backtrader as bt
import pandas as pd

# from cross_ema import BasicStrategy, BuyStrategy, SellStrategy
# from .algo.trend_keltner import BasicStrategy, BuyStrategy, SellStrategy
from .algo import import_algo_class, import_algo_module

#currency_list = ["EURUSD", "GBPUSD", "AUDUSD", "NZDUSD", "USDCHF", "USDCAD"]
# currency_list = ["EURUSD", "GBPUSD"]
#output_dir = './output/'

log = logging.getLogger(__name__)

class BaseRunner():
    def __init__(self, feed, data, algo, strategy, cash=10000.0, leverage=30, output_dir='./output/', plot=False, verbose=False):
        self.feed = feed
        self.data = data
        self.algo = algo
        self.strategy = strategy
        self.output_dir = output_dir
        self.plot = plot
        self.verbose = verbose
        self.cerebro = bt.Cerebro()
        self.set_start_position(cash, leverage)
        self.cerebro.adddata(data)
        self.add_analyzer()
        # self.module = import_algo_module(algo)
        self.StrategyClass = import_algo_class(algo, strategy)
        # log.info("module: {}".format(self.module.__name__))
        log.info("class: {}.{}".format(self.StrategyClass.__module__, self.StrategyClass.__name__))
        # self.import_algorithm(algo)
        # self.add_log(args)

    def set_start_position(self, cash, leverage):
        self.cerebro.broker.setcash(cash)
        self.cerebro.broker.setcommission(leverage=leverage)

    def add_analyzer(self, analyzer=bt.analyzers.TradeAnalyzer):
        self.cerebro.addanalyzer(analyzer)

    def get_strategy_class_name(self):
        words = self.StrategyClass.__module__.split('.')
        return words[2]

    def run(self):
        raise NotImplementedError

    def statistics(self):
        raise NotImplementedError


class AlgoRunner(BaseRunner):
    def __init__(self, feed, data, algo, strategy, cash=100000.0, leverage=30, output_dir='./output/', plot=False, verbose=False):
        super().__init__(feed, data, algo, strategy, cash=cash, leverage=leverage, output_dir=output_dir, plot=plot, verbose=verbose)
        self.add_analyzer()

    def statistics(self, strats):
        analyzer = strats[0].analyzers.tradeanalyzer.get_analysis()
        # logging.info(analyzer)
        if (analyzer.total.total == 0) or (analyzer.total.total == 1 and analyzer.total.open == 1):
            log.info('Warning: No trades in period')
        else:
            log.info(
                'Won trades (count/total/max/average)  {:3d} |  {:.2f} |  {:.2f} |  {:.2f}'.format(
                    analyzer.won.total, analyzer.won.pnl.total, analyzer.won.pnl.max, analyzer.won.pnl.average))
            log.info(
                'Lost trades (count/total/max/average) {:3d} | {:.2f} | {:.2f} | {:.2f}'.format(
                    analyzer.lost.total, analyzer.lost.pnl.total, analyzer.lost.pnl.max, analyzer.lost.pnl.average))
            log.info(
                'Total trades / net                    {:3d} |  {:.2f}'.format(
                    analyzer.total.closed, analyzer.pnl.net.total))
            log.info('Final Portfolio Value: {:.2f}'.format(self.cerebro.broker.getvalue()))

    def run(self):
        self.cerebro.addstrategy(
            self.StrategyClass,
            symbol=self.feed.symbol,
            verbose=self.verbose)
        self.cerebro.addwriter(bt.WriterFile, csv=True, out=('{}results.csv'.format(self.output_dir)))
        self.strats = self.cerebro.run()
        self.statistics(self.strats)
        if self.plot:
            self.cerebro.plot(style='candlestick', barup='green', bardown='red')


class OptimizeRunner(BaseRunner):
    def __init__(self, feed, data, algo, strategy, cash=100000.0, leverage=30, output_dir='./output/', plot=False, verbose=False, file_id=''):
        super().__init__(feed, data, algo, strategy, cash=cash, leverage=leverage, output_dir=output_dir, plot=plot, verbose=verbose)
        self.flie_id = file_id

    def statistics(self, strats):
        stat = []
        for i in range(0, len(strats)):
            params = strats[i][0].params
            analyzer = strats[i][0].analyzers.tradeanalyzer.get_analysis()
            # log.info('Type: {}'.format(dict(params)))
            if (analyzer.total.total == 0) or (analyzer.total.total == 1 and analyzer.total.open == 1):
                log.info('Warning: No trades in period {} {}'.format(self.strategy, self.feed.symbol))
            else:
                row = (self.strategy, self.feed.symbol, self.StrategyClass.get_parameter_values(params, 0),
                       self.StrategyClass.get_parameter_values(params, 1), self.StrategyClass.get_parameter_values(params, 2),
                       self.StrategyClass.get_parameter_values(params, 3), self.StrategyClass.get_parameter_values(params, 4),
                       self.StrategyClass.get_parameter_values(params, 5), self.StrategyClass.get_parameter_values(params, 6),
                       analyzer.total.closed, round(analyzer.pnl.net.total, 2),
                       analyzer.won.total, round(analyzer.won.pnl.total, 2), round(analyzer.won.pnl.max, 2),
                       round(analyzer.won.pnl.average, 2),
                       analyzer.lost.total, round(analyzer.lost.pnl.total, 2), round(analyzer.lost.pnl.max, 2),
                       round(analyzer.lost.pnl.average, 2))
                stat.append(row)

        df = pd.DataFrame(stat,
                          columns=['strategy', 'symbol',self.StrategyClass.get_parameter_keys(params, 0), self.StrategyClass.get_parameter_keys(params, 1),
                                   self.StrategyClass.get_parameter_keys(params, 2), self.StrategyClass.get_parameter_keys(params, 3), self.StrategyClass.get_parameter_keys(params, 4),
                                   self.StrategyClass.get_parameter_keys(params, 5), self.StrategyClass.get_parameter_keys(params, 6),
                                   'total_closed', 'net_total',
                                   'won_total', 'won_net', 'won_max', 'won_avg',
                                   'lost_total', 'lost_net', 'lost_max', 'lost_avg'])
        df.to_csv('{}{}_{}{}{}.csv'.format(self.output_dir, self.get_strategy_class_name(), self.strategy, self.feed.symbol.replace('/',''), self.flie_id), sep=';')
        log.info(df.sort_values(['net_total'], ascending=False).head(5)[
                         ['strategy', 'symbol', self.StrategyClass.get_parameter_keys(params, 0), self.StrategyClass.get_parameter_keys(params, 1), self.StrategyClass.get_parameter_keys(params, 2),
                          self.StrategyClass.get_parameter_keys(params, 3), self.StrategyClass.get_parameter_keys(params, 4), self.StrategyClass.get_parameter_keys(params, 5),
                          self.StrategyClass.get_parameter_keys(params, 6), 'total_closed', 'net_total']])

    def run(self):
        kwargs = self.StrategyClass.get_parameter_list()
        self.cerebro.optstrategy(
            self.StrategyClass,
            **kwargs
        )
        self.strats = self.cerebro.run(stdstats=False)
        self.statistics(self.strats)
