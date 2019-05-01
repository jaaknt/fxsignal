import pandas as pd
import backtrader as bt

class FeedConverter(object):

   @staticmethod
   def fxcm2bt(data):
       return bt.feeds.PandasData(
           dataname=data,
           # dtformat=('%Y-%m-%d '),
           timeframe=bt.TimeFrame.Minutes,
           datetime=1,
           open=2,
           close=3,
           high=4,
           low=5,
           volume=6,
           openinterest=-1
       )
