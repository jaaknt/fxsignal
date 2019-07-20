from datetime import datetime
import pandas as pd
import fxsignal
import fxcmpy
import yaml
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    handlers=[logging.FileHandler("./logs/currency.log"), logging.StreamHandler()])
log = logging.getLogger(__name__)

symbol_list = ['AUD/CAD','AUD/JPY','AUD/NZD','AUD/USD','CAD/CHF',
               'CAD/JPY','EUR/CHF','EUR/JPY','EUR/NZD','EUR/USD',
               'GBP/AUD','GBP/CHF','GBP/JPY','GBP/NZD','GBP/USD',
               'NZD/CHF','NZD/USD','USD/CAD','USD/CHF','USD/JPY']

def optimizebuy_hma(config, currency):
    feed = fxsignal.FxcmFeed(currency, datetime(2010, 1, 1), datetime(2019, 8, 1), 'D1', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.OptimizeRunner(feed, data, 'trend_jackvortex','buy')
    runner.run()

def optimizesell_hma(config, currency):
    feed = fxsignal.FxcmFeed(currency, datetime(2010, 1, 1), datetime(2019, 8, 1), 'D1', config['fxcm'])
    feed.read_csv()
    data = fxsignal.FeedConverter.fxcm2bt(feed.clean())
    runner = fxsignal.OptimizeRunner(feed, data, 'trend_jackvortex','sell')
    runner.run()

def run():
    log.info("Start")
    with open('./scripts/config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    for currency in ['AUD/USD', 'EUR/USD', 'GBP/USD', 'NZD/USD', 'USD/CAD', 'USD/CHF', 'USD/JPY'] :
    #for currency in symbol_list :
        optimizebuy_hma(config, currency)
        optimizesell_hma(config, currency)
    log.info("End")

if __name__ == '__main__':
    run()
