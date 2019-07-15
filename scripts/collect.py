from datetime import datetime
import pandas as pd
import backtrader as bt
import fxsignal
import fxcmpy
import yaml
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    handlers=[logging.FileHandler("./logs/collect.log"), logging.StreamHandler()])

symbol_list = ['EUR/USD', 'GBP/USD', 'AUD/USD', 'NZD/USD', 'USD/CAD', 'USD/CHF', 'GBP/AUD', 'EUR/JPY', 'EUR/CHF',
               'AUD/CAD', 'AUD/JPY', 'GBP/NZD', 'GBP/JPY', 'GBP/CHF', 'EUR/NZD', 'AUD/NZD', 'CAD/CHF', 'CAD/JPY',
               'GBP/CHF', 'NZD/CHF', 'USD/JPY']

def collect(config):
    start_date = datetime(2010, 1, 1)
    end_date = datetime(2019, 6, 1)
    for symbol in symbol_list:
        feed = fxsignal.FxcmFeed(symbol, start_date, end_date, 'D1', config['fxcm'])
        feed.get_feed()
        feed.close()
        data = feed.clean()
        feed.save_csv(data)
        logging.info("{} count: {}".format(symbol, len(data.index)))

def run():
    with open('./scripts/config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    collect(config)

if __name__ == '__main__':
    run()
