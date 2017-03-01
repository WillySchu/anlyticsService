import arrow
import math

import statsmodels.api as sm
import pandas as pd
import numpy as np

from scipy.optimize import brute

class Benchmark(object):
    def __init__(self, file, sep='\t', date_col=1):
        self.data = pd.read_csv(file, sep=sep, parse_dates=[date_col])
        cols = list(self.data.columns.values)
        self.dim = cols[0]
        self.met = cols[-1]
        self.data = self.data.groupby([self.dim, 'ga:date']).sum()

    def test(self):
        dims = list(set(self.data[self.dim]))
        sess = self.data[self.met]

        sum_rmse = 0
        t0 = arrow.get()

        for dim in dims:
            l = len(sess[dim])
            if l < 82:
                continue
            vl = l // 5

            start = sess[dim][-vl:].index[0].strftime('%Y-%m-%d')

            model = auto_arima(sess[dim][:l-vl+1])
            pred = model.get_prediction(start=start, end=l-1)
            resid = pred.predicted_mean - sess[dim][-vl:]

            sum_rmse += rmse(resid)

        tf = arrow.get()
        duration = tf - t0

        return (duration, sum_rmse)

def test_arima(orders, x):
    order = orders[:3]
    seasonal_order = orders[3:]
    seasonal_order = np.insert(seasonal_order, 3, 7)
    try:
        fit = sm.tsa.statespace.SARIMAX(x, trend='n', order=order, seasonal_order=seasonal_order).fit()
        if math.isnan(rmse(fit.resid)):
            return float('inf')
        return rmse(fit.resid)
    except Exception as err:
        print err
        return float('inf')

def rmse(resid):
    rmse = 0
    for r in resid:
        rmse += math.sqrt(r**2)

    return rmse

def auto_arima(x):
        grid = (slice(0, 3, 1), slice(0, 3, 1), slice(0, 3, 1), slice(0, 3, 1), slice(0, 3, 1), slice(0, 3, 1))
        res = brute(test_arima, grid, args=(x,), finish=None)
        if any(i != 0 for i in res):
            # slice up orders
            order = res[:3].astype(int)
            seasonal_order = res[3:].astype(int)
            # hardcode insert seven period seasonality
            # this will need to become more dynamic later when we deal with
            # multi day long periods
            seasonal_order = np.insert(seasonal_order, 3, 7)
            return sm.tsa.statespace.SARIMAX(x.astype(float), trend='n', order=order, seasonal_order=seasonal_order).fit()

def clean_file(file, char='\x00'):
    h = open(file, 'r')
    f = h.read()
    f = ''.join(f.split(char))
    w = open(file, 'w')
    w.write(f)
    w.close()
