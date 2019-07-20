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
    feed = fxsignal.FxcmFeed('EUR/USD', datetime(2018, 11, 1), datetime(2019, 5, 1), 'D1', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.AlgoRunner(feed, data, 'trend_jackvortex','buy', plot=True, verbose=False)
    runner.run()
    logging.info("simplebuy symbol: {} {}".format(feed.symbol, runner.feed.symbol))

def simplesell_hma(config):
    feed = fxsignal.FxcmFeed('EUR/USD', datetime(2018, 11, 1), datetime(2019, 5, 1), 'D1', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.AlgoRunner(feed, data, 'trend_jackvortex','sell', plot=True, verbose=True)
    runner.run()
    logging.info("simplebuy symbol: {} {}".format(feed.symbol, runner.feed.symbol))

def run():
    with open('./scripts/config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    simplebuy_hma(config)
#    simplesell_hma(config)

if __name__ == '__main__':
    run()
