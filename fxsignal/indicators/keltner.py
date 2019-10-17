import backtrader as bt
import backtrader.indicators as btind

class KeltnerChannels(bt.Indicator):
    '''
    Keltner indicator
    https://www.investopedia.com/terms/k/keltnerchannel.asp
    '''
    lines = ('ma','upper','lower',)

    plotinfo = dict(subplot=False)  # plot along with data
    plotlines = dict(
        ma=dict(ls='--'),  # dashed line
        upper=dict(_samecolor=True),  # use same color as prev line (dcm)
        lower=dict(_samecolor=True),  # use same color as prev line (dch)
    )

    params = (
        ('period', 20),
        ('multiplier', 2.0),
        ('movav', btind.MovAv.Exponential),
        ('atr_period', 10)
    )


    def __init__(self):
        super(KeltnerChannels, self).__init__()

        self.l.ma = self.p.movav(self.data.close, period=self.p.period)
        atr = btind.ATR(self.data, period=self.p.atr_period)
        self.l.upper = self.l.ma + self.p.multiplier * atr
        self.l.lower = self.l.ma - self.p.multiplier * atr
