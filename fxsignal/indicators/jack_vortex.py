import backtrader as bt
import backtrader.indicators as btind

class JackVortex(bt.Indicator):
    '''
    My deveped indicator that is similar to VORTEX indicator

    '''
    lines = ('jack_vortex',)

    params = (
        ('squeeze_period', 20),
    )

    plotlines = dict(jack_vortex=dict(_method='bar', alpha=0.50, width=1.0))

    def __init__(self):
        highest = btind.Highest(self.data.high, period=self.p.squeeze_period)
        lowest = btind.Lowest(self.data.low, period=self.p.squeeze_period)
        sma = btind.MovAv.SMA(self.data.close, period=self.p.squeeze_period)
        mean = (highest + lowest + sma) / 3.0
        self.l.jack_vortex = btind.MovAv.SMA((self.data.close - mean) / self.data.close, period=self.p.squeeze_period)

        super(JackVortex, self).__init__()
