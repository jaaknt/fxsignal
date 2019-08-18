from datetime import datetime
import pandas as pd
import fxsignal
import fxcmpy
import yaml
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    handlers=[logging.FileHandler("./logs/algo.log"), logging.StreamHandler()])

def simplebuy_trend30(config):
    feed = fxsignal.FxcmFeed('GBP/USD', datetime(2019, 1, 1), datetime(2019, 9, 1), 'm30', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.AlgoRunner(feed, data, 'trend30', 'buy', plot=True, verbose=False)
    runner.run()
    logging.info("simplebuy symbol: {} {}".format(feed.symbol, runner.feed.symbol))

def simplesell_trend30(config):
    feed = fxsignal.FxcmFeed('GBP/USD', datetime(2019, 1, 1), datetime(2019, 9, 1), 'm30', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.AlgoRunner(feed, data, 'trend30','sell', plot=True, verbose=True)
    runner.run()
    logging.info("simplesell symbol: {} {}".format(feed.symbol, runner.feed.symbol))

def optimizebuy_trend30(config):
    feed = fxsignal.FxcmFeed('GBP/USD', datetime(2019, 1, 1), datetime(2019, 9, 1), 'm30', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.OptimizeRunner(feed, data, 'trend30', 'buy')
    runner.run()

def optimizesell_trend30(config):
    feed = fxsignal.FxcmFeed('GBP/USD', datetime(2019, 1, 1), datetime(2019, 9, 1), 'm30', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.OptimizeRunner(feed, data, 'trend30', 'sell')
    runner.run()


def run():
    with open('./scripts/config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    #simplebuy_trend30(config)
    #simplesell_trend30(config)
    optimizebuy_trend30(config)
    #optimizesell_trend30(config)

if __name__ == '__main__':
    run()
