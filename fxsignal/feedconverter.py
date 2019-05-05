import pandas as pd
import backtrader as bt

class FeedConverter(object):

   @staticmethod
   def fxcm2bt(fxcm_data):
       return bt.feeds.PandasData(
           dataname=fxcm_data,
           # dtformat=('%Y-%m-%d '),
           # timeframe=bt.TimeFrame.Minutes,
           datetime=0,
           open=1,
           close=2,
           high=3,
           low=4,
           volume=5,
           openinterest=-1
       )
