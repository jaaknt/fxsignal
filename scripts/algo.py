from datetime import datetime
import pandas as pd
import fxsignal
import fxcmpy
import yaml
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    handlers=[logging.FileHandler("./logs/algo.log"), logging.StreamHandler()])

def simplebuy(config):
    feed = fxsignal.FxcmFeed('EUR/USD', datetime(2015, 1, 1), datetime(2019, 5, 1), 'D1', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.AlgoRunner(feed, data, 'trend_keltner2','buy')
    runner.run()
    logging.info("simplebuy symbol: {} {}".format(feed.symbol, runner.feed.symbol))

def simplesell(config):
    feed = fxsignal.FxcmFeed('EUR/USD', datetime(2015, 1, 1), datetime(2019, 5, 1), 'D1', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.AlgoRunner(feed, data, 'trend_keltner2','sell')
    runner.run()

def optimizebuy(config):
    feed = fxsignal.FxcmFeed('EUR/USD', datetime(2015, 1, 1), datetime(2019, 5, 1), 'D1', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.OptimizeRunner(feed, data, 'trend_keltner','buy')
    runner.run()

def optimizesell(config):
    feed = fxsignal.FxcmFeed('EUR/USD', datetime(2015, 1, 1), datetime(2019, 5, 1), 'D1', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.OptimizeRunner(feed, data, 'trend_keltner', 'sell')
    runner.run()



def run():
    with open('./scripts/config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    simplebuy(config)
    simplesell(config)
    optimizebuy(config)
    optimizesell(config)

if __name__ == '__main__':
    run()
