import arrow
import math

import pandas as pd

from analytics.arima import auto_arima
from suppress_print import suppress_stdout_stderr

class Benchmark(object):
    def __init__(self, file, sep='\t', date_col=1):
        self.data = pd.read_csv(file, sep=sep, parse_dates=[date_col])
        cols = list(self.data.columns.values)
        self.dim = cols[0]
        self.met = cols[-1]
        self.dims = list(set(self.data[self.dim]))
        self.data = self.data.groupby([self.dim, 'ga:date']).sum()

    def test(self):
        sess = self.data[self.met]

        sum_rmse = 0
        t0 = arrow.get()

        for dim in self.dims:
            l = len(sess[dim])
            if l < 82:
                continue
            vl = l // 5

            start = sess[dim][-vl:].index[0].strftime('%Y-%m-%d')

            model = auto_arima(sess[dim][:l-vl+1])
            pred = model.get_prediction(start=start, end=l-1)

            resid = pred.predicted_mean - sess[dim][-vl:]

            sum_rmse += rmse(resid)

            break

        tf = arrow.get()
        duration = tf - t0

        return (duration, sum_rmse)

def rmse(resid):
    rmse = 0
    for r in resid:
        rmse += math.sqrt(r**2)

    return rmse

def clean_file(file, char='\x00'):
    h = open(file, 'r')
    f = h.read()
    f = ''.join(f.split(char))
    w = open(file, 'w')
    w.write(f)
    w.close()
