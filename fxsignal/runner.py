import argparse
import logging
import os

from datetime import datetime
import backtrader as bt
import pandas as pd

# from cross_ema import BasicStrategy, BuyStrategy, SellStrategy
from .trend_keltner import BasicStrategy, BuyStrategy, SellStrategy

currency_list = ["EURUSD", "GBPUSD", "AUDUSD", "NZDUSD", "USDCHF", "USDCAD"]
# currency_list = ["EURUSD", "GBPUSD"]
output_dir = './output/'


class BaseRunner():
    def __init__(self, args):
        self.args = args
        self.cerebro = bt.Cerebro()
        self.set_start_position()
        self.add_logging(args)

    def set_start_position(self, cash=100000.0, leverage=30):
        self.cerebro.broker.setcash(cash)
        self.cerebro.broker.setcommission(leverage=leverage)

    def add_logging(self, args):
        filename = os.path.basename(__file__)
        logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                            format='%(asctime)s %(levelname)-8s %(message)s',
                            handlers=[logging.FileHandler("logs/{}.log".format(os.path.splitext(filename)[0])),
                                      logging.StreamHandler()])

        logging.info("====================================")
        logging.info("Application {} started".format(filename))
        logging.info(
            "Environment mode : {}, strategy : {}, currency: {}, timeframe: {}".format(args.mode, args.strategy,
                                                                                       args.currency, args.timeframe))

    def set_data_feed(self, currency):
        if currency is not None:
            self.args.currency = currency
        dataCsv = bt.feeds.GenericCSVData(
            dataname='../data/{}{}1.csv'.format(currency, self.args.timeframe[0]),
            separator=';',
            fromdate=datetime.strptime(self.args.start, '%Y-%m-%d'),
            todate=datetime.strptime(self.args.end, '%Y-%m-%d'),
            nullvalue=0.0,
            # dtformat=('%Y-%m-%d '),
            timeframe=bt.TimeFrame.Minutes,
            datetime=1,
            open=2,
            close=3,
            high=4,
            low=5,
            volume=6,
            openinterest=-1
        )
        if self.args.timeframe[0] == 'H' and self.args.timeframe[1:] != '1':
            self.cerebro.resampledata(dataCsv, timeframe=bt.TimeFrame.Minutes,
                                      compression=60 * int(self.args.timeframe[1:]))
        else:
            self.cerebro.adddata(dataCsv)

    def add_analyzer(self, analyzer=bt.analyzers.TradeAnalyzer):
        self.cerebro.addanalyzer(analyzer)

    def run(self):
        raise NotImplementedError

    def statistics(self):
        raise NotImplementedError


class AlgoRunner(BaseRunner):
    def __init__(self, args):
        super().__init__(args)
        self.add_analyzer()
        self.set_data_feed(self.args.currency)

    def statistics(self, strats):
        analyzer = strats[0].analyzers.tradeanalyzer.get_analysis()
        # logging.debug(analyzer)
        if analyzer.total.total == 0:
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
            SellStrategy if self.args.strategy == "sell" else BuyStrategy,
            currency=self.args.currency,
            verbose=self.args.verbose)
        self.cerebro.addwriter(bt.WriterFile, csv=True, out=('{}results.csv'.format(output_dir)))
        self.strats = self.cerebro.run()
        self.statistics(self.strats)
        self.cerebro.plot(style='candlestick', barup='green', bardown='red')


class OptimizeRunner(BaseRunner):
    def __init__(self, args):
        super().__init__(args)
        self.add_analyzer()
        self.set_data_feed(self.args.currency)

    def statistics(self, strats):
        for i in range(0, len(strats)):
            params = strats[i][0].params
            analyzer = strats[i][0].analyzers.tradeanalyzer.get_analysis()
            if analyzer.total.total == 0:
                logging.info('Warning: No trades in period')
            logging.info('{}'.format(BasicStrategy.get_parameter_values(params)))
            logging.info(
                'Won trades (count/total/max/average)  {:3d} |  {:.2f} |  {:.2f} |  {:.2f}'.format(
                    analyzer.won.total, analyzer.won.pnl.total, analyzer.won.pnl.max, analyzer.won.pnl.average))
            logging.info(
                'Lost trades (count/total/max/average) {:3d} | {:.2f} | {:.2f} | {:.2f}'.format(
                    analyzer.lost.total, analyzer.lost.pnl.total, analyzer.lost.pnl.max,
                    analyzer.lost.pnl.average))
            logging.info(
                'Total trades / net                    {:3d} |  {:.2f}'.format(
                    analyzer.total.closed, analyzer.pnl.net.total))

    def run(self):
        kwargs = BuyStrategy.get_parameter_list()
        self.cerebro.optstrategy(
            SellStrategy if self.args.strategy == "sell" else BuyStrategy,
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


class StatisticsRunner(OptimizeRunner):

    def statistics(self, strats):
        stat = []
        for i in range(0, len(strats)):
            params = strats[i][0].params
            analyzer = strats[i][0].analyzers.tradeanalyzer.get_analysis()
            # logging.info('Type: {}'.format(dict(params)))
            if analyzer.total.total == 0:
                logging.info('Warning: No trades in period {} {} {}',
                             format(self.args.strategy, self.args.currency, params))
            else:
                row = (self.args.strategy, self.args.currency, BasicStrategy.get_parameter_values(params, 0),
                       BasicStrategy.get_parameter_values(params, 1), BasicStrategy.get_parameter_values(params, 2),
                       BasicStrategy.get_parameter_values(params, 3), BasicStrategy.get_parameter_values(params, 4),
                       analyzer.total.closed, round(analyzer.pnl.net.total, 2),
                       analyzer.won.total, round(analyzer.won.pnl.total, 2), round(analyzer.won.pnl.max, 2),
                       round(analyzer.won.pnl.average, 2),
                       analyzer.lost.total, round(analyzer.lost.pnl.total, 2), round(analyzer.lost.pnl.max, 2),
                       round(analyzer.lost.pnl.average, 2))
                stat.append(row)

        df = pd.DataFrame(stat,
                          columns=['strategy', 'currency',BasicStrategy.get_parameter_keys(params, 0), BasicStrategy.get_parameter_keys(params, 1),
                                   BasicStrategy.get_parameter_keys(params, 2), BasicStrategy.get_parameter_keys(params, 3), BasicStrategy.get_parameter_keys(params, 4),
                                   'total_closed', 'net_total',
                                   'won_total', 'won_net', 'won_max', 'won_avg',
                                   'lost_total', 'lost_net', 'lost_max', 'lost_avg'])
        df.to_csv('{}{}_{}{}.csv'.format(output_dir, BasicStrategy.get_algorithm_name(), self.args.strategy, self.args.currency), sep=';')
        logging.info(df.sort_values(['net_total'], ascending=False).head(5)[
                         ['strategy', 'currency', BasicStrategy.get_parameter_keys(params, 0), BasicStrategy.get_parameter_keys(params, 1), BasicStrategy.get_parameter_keys(params, 2),
                          BasicStrategy.get_parameter_keys(params, 3), BasicStrategy.get_parameter_keys(params, 4), 'total_closed', 'net_total']])


def parse_args():
    parser = argparse.ArgumentParser(
        description='Backtrader run script',
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("-m", "--mode",
                        required=True,
                        choices=["algo", "optimize", "statistics", "live"],
                        help="algo - for one algorithm testing, optimize - to find best algo parameters, statistics - collect optimize statistics to file, live - run in live")
    parser.add_argument("-s", "--strategy",
                        required=True,
                        choices=["buy", "sell"],
                        help="buy - buy algorithm, sell - sell algorithm")
    parser.add_argument("-c", "--currency",
                        required=True,
                        choices=currency_list,
                        help="currency pair to trade")
    parser.add_argument("--timeframe",
                        choices=['H1', 'H4', 'H6', 'H8', 'H12', 'D1'],
                        default='D1',
                        help="supported values [H1, H4, H6, H8, H12, D1]")
    parser.add_argument("--start",
                        default="2010-01-01",
                        help="start date for backtesting (default 2010-01-01)")
    parser.add_argument("--end",
                        default="2019-12-31",
                        help="end date for backtesting (default 2018-12-31)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="increase output verbosity")
    return parser.parse_args()


def btester():
    args = parse_args()
    if args.mode == "algo":
        runner = AlgoRunner(args)
    elif args.mode == "optimize":
        runner = OptimizeRunner(args)
    elif args.mode == "statistics":
        runner = StatisticsRunner(args)

    runner.run()


if __name__ == '__main__':
    btester()
