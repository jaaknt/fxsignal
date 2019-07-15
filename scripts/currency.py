from datetime import datetime
import pandas as pd
import fxsignal
import fxcmpy
import yaml
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    handlers=[logging.FileHandler("./logs/currency.log"), logging.StreamHandler()])

def optimizebuy_hma(config, currency):
    feed = fxsignal.FxcmFeed(currency, datetime(2015, 1, 1), datetime(2019, 5, 1), 'D1', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.OptimizeRunner(feed, data, 'trend_hma','buy')
    runner.run()

def optimizesell_hma(config, currency):
    feed = fxsignal.FxcmFeed(currency, datetime(2015, 1, 1), datetime(2019, 5, 1), 'D1', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.OptimizeRunner(feed, data, 'trend_hma','sell')
    runner.run()

def run():
    with open('./scripts/config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    for currency in ['AUD/USD', 'EUR/USD', 'GBP/USD', 'NZD/USD', 'USD/CAD', 'USD/CHF', 'USD/JPY'] :
        optimizebuy_hma(config, currency)
        optimizesell_hma(config, currency)

if __name__ == '__main__':
    run()