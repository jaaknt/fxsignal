# Algorithms description
Description of algorithms in plain English implemented in fxsignal/algo directory.

## Trend Keltner
This is trend following algorithm based on ideas
- [Squeeze Momentum](https://www.tradingview.com/script/nqQ1DT5a-Squeeze-Momentum-Indicator-LazyBear/)
- [Elder Impulse System](https://stockcharts.com/school/doku.php?id=chart_school:chart_analysis:elder_impulse_system)
There are few tweaks compared to original algoritm and Squeeze Momentum signals are
different from original idea. Squeeze Momentum signal is valid if 2 last bars are higher then previous one
Squeeze histogram measure how far is current close from 20 day mean value.
Mean  = ((HIGHEST(20)-LOWEST(20))/2 + SMA(20))/2
Squeeze = SMA((close - Mean) / close, 20)

### Algorithm description
1. Filter STDDEV(20)*2.0 > ATR(14)*1.7 #Squeeze off
2. Filter EMA(10)[0] > EMA(10)[-1] and MACD.HISTO[0] > MACD.HISTO[-1] #Elder momentum
   The MACD-Histogram is based on MACD(12,26,9)
3. Filter squeeze[0] < squeeze[-1] and squeeze[-1] < squeeze[-2] #Two last squeeze bars are higher then previous one  

#### Stop condition
1. close - 1.0*ATR(14)

#### Exit condition1
1. Close 1/2 position if close + 1.2*ATR(14) target has been reached
2. Move stop condition = close + 10pips
3. Move exit condition = close + 0.4*ATR(14)

#### Exit condition2
1. Close another 1/2 position if close + 0.4*ATR(14) target has been reached
