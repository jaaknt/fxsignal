from datetime import datetime
import pandas as pd
import backtrader as bt
import fxsignal
import fxcmpy
import yaml
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    handlers=[logging.FileHandler("./logs/fxsignal-test.log"), logging.StreamHandler()])

def getcsv(config):
    feed = fxsignal.FxcmFeed('GBP/USD', datetime(2018, 1, 1), datetime(2019, 5, 1), 'D1', config['fxcm'])
    # data = pd.DataFrame()
    data = feed.read_csv()
    logging.info("getcsv count(): {}".format(len(data.index)))

def savecsv(config):
    feed = fxsignal.FxcmFeed('GBP/USD', datetime(2018, 1, 1), datetime(2019, 5, 1), 'D1', config['fxcm'])
    # data = pd.DataFrame()
    data = feed.get_feed()
    feed.close()
    feed.save_csv(data)
    logging.info("savecsv count(): {}".format(len(data.index)))

def panda2bt(config):
    feed = fxsignal.FxcmFeed('GBP/USD', datetime(2018, 1, 1), datetime(2019, 5, 1), 'D1', config['fxcm'])
    # data = pd.DataFrame()
    feed.read_csv()
    d1 = feed.clean()
    # print(d1.info())
    data = fxsignal.FeedConverter.fxcm2bt(d1)
    logging.info("panda2bt symbol(): {}".format(feed.symbol))

def run():
    with open('./scripts/config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    savecsv(config)
    getcsv(config)
    panda2bt(config)

if __name__ == '__main__':
    run()
