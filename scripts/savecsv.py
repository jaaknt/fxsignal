from datetime import datetime
import pandas as pd
import fxsignal
import fxcmpy
import yaml
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    handlers=[logging.FileHandler("./logs/fxsignal.log"), logging.StreamHandler()])

def getcsv(config):
    feed = fxsignal.FxcmFeed('EUR/USD', datetime(2019, 1, 1), datetime(2019, 5, 1), 'D1', config['fxcm'])
    # data = pd.DataFrame()
    data = feed.read_csv()
    logging.info("getcsv count(): {}".format(len(data.index)))

def savecsv(config):
    feed = fxsignal.FxcmFeed('EUR/USD', datetime(2019, 1, 1), datetime(2019, 5, 1), 'D1', config['fxcm'])
    # data = pd.DataFrame()
    data = feed.get_feed()
    feed.close()
    feed.save_csv(data)
    logging.info("savecsv count(): {}".format(len(data.index)))


def run():
    with open('./scripts/config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    savecsv(config)
    getcsv(config)

if __name__ == '__main__':
    run()
