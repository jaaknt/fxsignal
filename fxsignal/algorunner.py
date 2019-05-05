import argparse
import logging
import os

from datetime import datetime
import backtrader as bt
import pandas as pd

# from cross_ema import BasicStrategy, BuyStrategy, SellStrategy
from .trend_keltner import BasicStrategy, BuyStrategy, SellStrategy

#currency_list = ["EURUSD", "GBPUSD", "AUDUSD", "NZDUSD", "USDCHF", "USDCAD"]
# currency_list = ["EURUSD", "GBPUSD"]
#output_dir = './output/'


class BaseRunner():
    def __init__(self, feed, data, strategy, cash=10000.0, leverage=30, output_dir='./output/', plot=False, verbose=False):
        self.feed = feed
        self.data = data
        self.strategy = strategy
        self.output_dir = output_dir
        self.plot = plot
        self.verbose = verbose
        self.cerebro = bt.Cerebro()
        self.set_start_position(cash, leverage)
        self.cerebro.adddata(data)
        self.add_analyzer()
        # self.add_logging(args)

    def set_start_position(self, cash, leverage):
        self.cerebro.broker.setcash(cash)
        self.cerebro.broker.setcommission(leverage=leverage)

    def add_analyzer(self, analyzer=bt.analyzers.TradeAnalyzer):
        self.cerebro.addanalyzer(analyzer)

    def run(self):
        raise NotImplementedError

    def statistics(self):
        raise NotImplementedError


class AlgoRunner(BaseRunner):
    def __init__(self, feed, data, strategy, cash=100000.0, leverage=30, output_dir='./output/', plot=False, verbose=False):
        super().__init__(feed, data, strategy, cash=cash, leverage=leverage, output_dir=output_dir, plot=plot, verbose=verbose)
        self.add_analyzer()

    def statistics(self, strats):
        analyzer = strats[0].analyzers.tradeanalyzer.get_analysis()
        # logging.info(analyzer)
        if (analyzer.total.total == 0) or (analyzer.total.total == 1 and analyzer.total.open == 1):
            logging.info('Warning: No trades in period')
        else:
            logging.info(
                'Won trades (count/total/max/average)  {:3d} |  {:.2f} |  {:.2f} |  {:.2f}'.format(
                    analyzer.won.total, analyzer.won.pnl.total, analyzer.won.pnl.max, analyzer.won.pnl.average))
            logging.info(
                'Lost trades (count/total/max/average) {:3d} | {:.2f} | {:.2f} | {:.2f}'.format(
                    analyzer.lost.total, analyzer.lost.pnl.total, analyzer.lost.pnl.max, analyzer.lost.pnl.average))
            logging.info(
                'Total trades / net                    {:3d} |  {:.2f}'.format(
                    analyzer.total.closed, analyzer.pnl.net.total))
            logging.info('Final Portfolio Value: {:.2f}'.format(self.cerebro.broker.getvalue()))

    def run(self):
        self.cerebro.addstrategy(
            SellStrategy if self.strategy == "sell" else BuyStrategy,
            symbol=self.feed.symbol,
            verbose=self.verbose)
        self.cerebro.addwriter(bt.WriterFile, csv=True, out=('{}results.csv'.format(self.output_dir)))
        self.strats = self.cerebro.run()
        self.statistics(self.strats)
        if self.plot:
            self.cerebro.plot(style='candlestick', barup='green', bardown='red')


class OptimizeRunner(BaseRunner):
    def __init__(self, feed, data, strategy, cash=100000.0, leverage=30, output_dir='./output/', plot=False, verbose=False):
        super().__init__(feed, data, strategy, cash=cash, leverage=leverage, output_dir=output_dir, plot=plot, verbose=verbose)

    def statistics(self, strats):
        stat = []
        for i in range(0, len(strats)):
            params = strats[i][0].params
            analyzer = strats[i][0].analyzers.tradeanalyzer.get_analysis()
            # logging.info('Type: {}'.format(dict(params)))
            if (analyzer.total.total == 0) or (analyzer.total.total == 1 and analyzer.total.open == 1):
                logging.info('Warning: No trades in period {} {} {}',
                    format(self.strategy, self.feed.symbol, params))
            else:
                row = (self.strategy, self.feed.symbol, BasicStrategy.get_parameter_values(params, 0),
                       BasicStrategy.get_parameter_values(params, 1), BasicStrategy.get_parameter_values(params, 2),
                       BasicStrategy.get_parameter_values(params, 3), BasicStrategy.get_parameter_values(params, 4),
                       analyzer.total.closed, round(analyzer.pnl.net.total, 2),
                       analyzer.won.total, round(analyzer.won.pnl.total, 2), round(analyzer.won.pnl.max, 2),
                       round(analyzer.won.pnl.average, 2),
                       analyzer.lost.total, round(analyzer.lost.pnl.total, 2), round(analyzer.lost.pnl.max, 2),
                       round(analyzer.lost.pnl.average, 2))
                stat.append(row)

        df = pd.DataFrame(stat,
                          columns=['strategy', 'symbol',BasicStrategy.get_parameter_keys(params, 0), BasicStrategy.get_parameter_keys(params, 1),
                                   BasicStrategy.get_parameter_keys(params, 2), BasicStrategy.get_parameter_keys(params, 3), BasicStrategy.get_parameter_keys(params, 4),
                                   'total_closed', 'net_total',
                                   'won_total', 'won_net', 'won_max', 'won_avg',
                                   'lost_total', 'lost_net', 'lost_max', 'lost_avg'])
        df.to_csv('{}{}_{}{}.csv'.format(self.output_dir, BasicStrategy.get_algorithm_name(), self.strategy, self.feed.symbol.replace('/','')), sep=';')
        logging.info(df.sort_values(['net_total'], ascending=False).head(5)[
                         ['strategy', 'symbol', BasicStrategy.get_parameter_keys(params, 0), BasicStrategy.get_parameter_keys(params, 1), BasicStrategy.get_parameter_keys(params, 2),
                          BasicStrategy.get_parameter_keys(params, 3), BasicStrategy.get_parameter_keys(params, 4), 'total_closed', 'net_total']])

    def run(self):
        kwargs = BuyStrategy.get_parameter_list()
        self.cerebro.optstrategy(
            SellStrategy if self.strategy == "sell" else BuyStrategy,
            **kwargs
            # rsi_threshold=range(72, 70, -2) if self.args.strategy == "sell" else range(28, 30, 2),
            # rsi_threshold=range(70, 62, -2) if self.args.strategy == "sell" else range(30, 38, 2),
            # stage1_profit_target=[0.01200, 0.01300],
            # stage1_profit_target=[0.0080, 0.0090, 0.0100, 0.01100, 0.01200, 0.01300, 0.01400, 0.01500, 0.01600],
            # stage1_profit_target=[0.0080, 0.0100, 0.01200, 0.01400, 0.01600],
            # stage1_loss_limit=[0.01400, 0.01600],  # , 0.01800, 0.0200, 0.0220]
            # stage1_loss_limit=[0.01200, 0.01400],
            # stage1_loss_limit=[0.01200, 0.01400, 0.01600, 0.01800, 0.0200, 0.0220],
            # verbose=[self.args.verbose]
        )
        self.strats = self.cerebro.run(stdstats=False)
        self.statistics(self.strats)
