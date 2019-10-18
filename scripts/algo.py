from datetime import datetime
import pandas as pd
import fxsignal
import fxcmpy
import yaml
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    handlers=[logging.FileHandler("./logs/algo.log"), logging.StreamHandler()])

#major_currencies = ['EUR/USD', 'GBP/USD', 'AUD/USD', 'USD/CAD', 'NZD/USD', 'USD/CHF','USD/JPY']
major_currencies = ['EUR/USD', 'GBP/USD', 'USD/CAD', 'USD/JPY']

def simplebuy_breakout30_major(config):
    for currency in major_currencies:
        feed = fxsignal.FxcmFeed(currency, datetime(2018, 1, 1), datetime(2019, 12, 1), 'm30', config['fxcm'])
        feed.read_csv()
        data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
        runner = fxsignal.AlgoRunner(feed, data, 'breakout30', 'buy', plot=False, verbose=False)
        runner.run()
        logging.info("simplebuy symbol: {} {}".format(feed.symbol, runner.feed.symbol))

def simplesell_breakout30_major(config):
    for currency in major_currencies:
        feed = fxsignal.FxcmFeed(currency, datetime(2018, 1, 1), datetime(2019, 12, 1), 'm30', config['fxcm'])
        feed.read_csv()
        data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
        runner = fxsignal.AlgoRunner(feed, data, 'breakout30', 'sell', plot=False, verbose=False)
        runner.run()
        logging.info("simplesell symbol: {} {}".format(feed.symbol, runner.feed.symbol))


def simplebuy_breakout30(config):
    feed = fxsignal.FxcmFeed('USD/CAD', datetime(2019, 8, 1), datetime(2019, 12, 1), 'm30', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.AlgoRunner(feed, data, 'breakout30', 'buy', plot=False, verbose=True)
    runner.run()
    logging.info("simplebuy symbol: {} {}".format(feed.symbol, runner.feed.symbol))

def simplesell_breakout30(config):
    feed = fxsignal.FxcmFeed('EUR/USD', datetime(2019, 8, 1), datetime(2019, 12, 1), 'm30', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.AlgoRunner(feed, data, 'breakout30', 'sell', plot=True, verbose=False)
    runner.run()
    logging.info("simplesell symbol: {} {}".format(feed.symbol, runner.feed.symbol))

def simplebuy_trend30(config):
    feed = fxsignal.FxcmFeed('GBP/USD', datetime(2019, 1, 1), datetime(2019, 12, 1), 'm30', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.AlgoRunner(feed, data, 'trend30', 'buy', plot=True, verbose=False)
    runner.run()
    logging.info("simplebuy symbol: {} {}".format(feed.symbol, runner.feed.symbol))

def simplesell_trend30(config):
    feed = fxsignal.FxcmFeed('GBP/USD', datetime(2019, 1, 1), datetime(2019, 12, 1), 'm30', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.AlgoRunner(feed, data, 'trend30','sell', plot=True, verbose=True)
    runner.run()
    logging.info("simplesell symbol: {} {}".format(feed.symbol, runner.feed.symbol))

def optimizebuy_trend30(config):
    feed = fxsignal.FxcmFeed('GBP/USD', datetime(2019, 1, 1), datetime(2019, 12, 1), 'm30', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.OptimizeRunner(feed, data, 'trend30', 'buy', leverage=300)
    runner.run()

def optimizesell_trend30(config):
    feed = fxsignal.FxcmFeed('GBP/USD', datetime(2019, 1, 1), datetime(2019, 12, 1), 'm30', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.OptimizeRunner(feed, data, 'trend30', 'sell')
    runner.run()

def optimizebuy_breakout30(config):
    for currency in major_currencies:
        feed = fxsignal.FxcmFeed(currency, datetime(2019, 9, 1), datetime(2019, 12, 1), 'm30', config['fxcm'])
        feed.read_csv()
        data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
        runner = fxsignal.OptimizeRunner(feed, data, 'breakout30', 'buy')
        runner.run()

def optimizesell_breakout30(config):
    for currency in major_currencies:
        feed = fxsignal.FxcmFeed(currency, datetime(2019, 9, 1), datetime(2019, 12, 1), 'm30', config['fxcm'])
        feed.read_csv()
        data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
        runner = fxsignal.OptimizeRunner(feed, data, 'breakout30', 'sell')
        runner.run()

def run():
    with open('./scripts/config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    #simplebuy_breakout30_major(config)
    #simplesell_breakout30_major(config)
    #simplebuy_breakout30(config)
    #simplesell_breakout30(config)
    #simplebuy_trend30(config)
    #simplesell_trend30(config)
    #optimizebuy_trend30(config)
    #optimizesell_trend30(config)
    #optimizesell_trend30(config)
    optimizebuy_breakout30(config)
    optimizesell_breakout30(config)

if __name__ == '__main__':
    run()
