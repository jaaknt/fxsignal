from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import backtrader as bt
import fxsignal
import fxcmpy
import yaml
import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    handlers=[logging.FileHandler("./logs/collect.log"), logging.StreamHandler()])

#symbol_list = ['EUR/USD', 'GBP/USD', 'AUD/USD', 'NZD/USD', 'USD/CAD', 'USD/CHF', 'GBP/AUD', 'EUR/JPY', 'EUR/CHF',
#               'AUD/CAD', 'AUD/JPY', 'GBP/NZD', 'GBP/JPY', 'GBP/CHF', 'EUR/NZD', 'AUD/NZD', 'CAD/CHF', 'CAD/JPY',
#               'GBP/CHF', 'NZD/CHF', 'USD/JPY']

# 'AUD/CHF','CHF/JPY','EUR/AUD','EUR/CAD','EUR/GBP','GBP/CAD','NZD/JPY',
symbol_list = ['GBP/USD']

#symbol_list = ['AUD/CAD','AUD/JPY','AUD/NZD','AUD/USD','CAD/CHF',
#               'CAD/JPY','EUR/CHF','EUR/JPY','EUR/NZD','EUR/USD',
#               'GBP/AUD','GBP/CHF','GBP/JPY','GBP/NZD','GBP/USD',
#               'NZD/CHF','NZD/USD','USD/CAD','USD/CHF','USD/JPY']

#    minutes: m1, m5, m15 and m30,
#    hours: H1, H2, H3, H4, H6 and H8,
#    one day: D1,
#    one week: W1,
#    one month: M1.


def collect(config):
    ''' Collects data for whole period '''
    start_date = datetime(2019, 1, 1)
    end_date = datetime(2019, 9, 1)
    for symbol in symbol_list:

        feed = fxsignal.FxcmFeed(symbol, start_date, end_date, 'm30', config['fxcm'])
        feed.get_feed()
        feed.close()
        data = feed.clean()
        feed.save_csv(data)
        logging.info("{} count: {}".format(symbol, len(data.index)))

def collect_chunk(config):
    ''' Collects data by months (there is 10000 records limitation in fxcmpy API) '''
    start_date = datetime(2018, 1, 1)
    end_date = datetime(2019, 12, 31)
    for symbol in symbol_list:
        chunk_start_date = start_date
        chunk_end_date = start_date + relativedelta(months=+1)
        history = pd.DataFrame()

        while (chunk_start_date < end_date):
            feed = fxsignal.FxcmFeed(symbol, chunk_start_date, chunk_end_date, 'm30', config['fxcm'])
            feed.get_feed()
            feed.close()
            data = feed.clean()
            history = history.append(data, ignore_index = True)
            chunk_start_date = chunk_end_date+relativedelta(seconds=+1)
            chunk_end_date   = chunk_end_date+relativedelta(months=+1)

        feed.save_csv(history)
        logging.info("{} count: {}".format(symbol, len(history.index)))


def run():
    with open('./scripts/config.yaml') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    collect_chunk(config)

if __name__ == '__main__':
    run()
