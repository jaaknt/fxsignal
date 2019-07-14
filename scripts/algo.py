from datetime import datetime
import pandas as pd
import fxsignal
import fxcmpy
import yaml
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    handlers=[logging.FileHandler("./logs/algo.log"), logging.StreamHandler()])

def simplebuy_hma(config):
    feed = fxsignal.FxcmFeed('EUR/USD', datetime(2018, 4, 1), datetime(2019, 5, 1), 'D1', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.AlgoRunner(feed, data, 'trend_hma','buy')
    runner.run()
    logging.info("simplebuy symbol: {} {}".format(feed.symbol, runner.feed.symbol))

def simplesell_hma(config):
    feed = fxsignal.FxcmFeed('EUR/USD', datetime(2018, 4, 1), datetime(2019, 5, 1), 'D1', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.AlgoRunner(feed, data, 'trend_hma','sell', plot=False, verbose=True)
    runner.run()
    logging.info("simplebuy symbol: {} {}".format(feed.symbol, runner.feed.symbol))


def simplebuy_keltner(config):
    feed = fxsignal.FxcmFeed('EUR/USD', datetime(2015, 1, 1), datetime(2019, 5, 1), 'D1', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.AlgoRunner(feed, data, 'trend_keltner','buy')
    runner.run()
    logging.info("simplebuy symbol: {} {}".format(feed.symbol, runner.feed.symbol))

def simplebuy_keltner2(config):
    feed = fxsignal.FxcmFeed('EUR/USD', datetime(2015, 1, 1), datetime(2019, 5, 1), 'D1', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.AlgoRunner(feed, data, 'trend_keltner2','buy')
    runner.run()

def optimizebuy_hma(config):
    feed = fxsignal.FxcmFeed('EUR/USD', datetime(2015, 1, 1), datetime(2019, 5, 1), 'D1', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.OptimizeRunner(feed, data, 'trend_hma','buy')
    runner.run()

def optimizesell_hma(config):
    feed = fxsignal.FxcmFeed('EUR/USD', datetime(2015, 1, 1), datetime(2019, 5, 1), 'D1', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.OptimizeRunner(feed, data, 'trend_hma','sell')
    runner.run()

def optimizesell_keltner(config):
    feed = fxsignal.FxcmFeed('EUR/USD', datetime(2018, 10, 1), datetime(2019, 5, 1), 'D1', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.OptimizeRunner(feed, data, 'trend_keltner', 'sell')
    runner.run()

def optimizesell_keltner2(config):
    feed = fxsignal.FxcmFeed('EUR/USD', datetime(2018, 10, 1), datetime(2019, 5, 1), 'D1', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.OptimizeRunner(feed, data, 'trend_keltner2', 'sell')
    runner.run()


def run():
    with open('./scripts/config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    simplebuy_hma(config)
    simplesell_hma(config)
    simplebuy_keltner(config)
    simplebuy_keltner2(config)
    optimizebuy_hma(config)
    optimizesell_hma(config)
    optimizesell_keltner(config)
    optimizesell_keltner2(config)

if __name__ == '__main__':
    run()
