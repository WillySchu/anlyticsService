import math
import pandas as pd
import numpy as np
import statsmodels.api as sm

from scipy.optimize import brute

class Forecast:
    def __init__(self, data):
        self.data = data
        print len(data)
        columns = [x['name'] for x in data[0]['columnHeaders']]
        rows = [x for x in data[0]['rows']]
        df = pd.DataFrame(rows, columns = columns)
        df['ga:date'] = pd.to_datetime(df['ga:date'], format = '%Y-%m-%d')

        df['ga:date'] = pd.DatetimeIndex(df['ga:date']).normalize()
        indices = [x for x in data[0]['query']['dimensions'] if x != 'ga:date']
        indices.append('ga:date')
        self.df = df.groupby(indices).sum()

        # print df['ga:sessions'].head()
        # print df.ix
        # print df.where(df.)

    def process(self):
        self.find_models()
        return self.data

    def find_models(self):
        # I feel like there should be a better way to iterate over the first
        # two indices without having to iterate over the third, but I'm
        # dumb so this will have to do for now
        dedup = {}
        idxlength = len(self.data[0]['query']['dimensions']) - 1
        # print self.data[0]['query']
        for met in self.data[0]['query']['metrics']:
            for index, val in self.df[met].iteritems():
                idx = index[:idxlength]
                try:
                    if dedup[idx] is True:
                        continue
                except:
                    dedup[idx] = True

                    model = self.auto_arima(self.df[met][idx])
                    # print model.summary()
                    break

    def rmse(self, resid):
        rmse = 0
        for r in resid:
            rmse += math.sqrt(r**2)

        return rmse

    def test_arima(self, orders, x):
        order = orders[:3]
        seasonal_order = orders[3:]
        seasonal_order = np.insert(seasonal_order, 3, 7)
        try:
            fit = sm.tsa.statespace.SARIMAX(x.astype(float), trend='n', order=order, seasonal_order=seasonal_order, freq=7).fit()
            rmse = self.rmse(fit.resid)
            print rmse
            if math.isnan(rmse):
                print fit.resid
                return float('inf')
            print rmse
            return rmse
        except Exception as err:
            print err
            return float('inf')

    def auto_arima(self, x):
        grid = (slice(0, 3, 1), slice(0, 3, 1), slice(0, 3, 1), slice(0, 3, 1), slice(0, 3, 1), slice(0, 3, 1))
        res = brute(self.test_arima, grid, args=(x,), finish=None)
        if any(i != 0 for i in res):
            print res
        return res
        # order = res[0][:3]
        # seasonal_order = res[0][3:]
        # seasonal_order = np.insert(seasonal_order, 3, 12)
        # return sm.tsa.statespace.SARIMAX(x, trend='n', order=order, seasonal_order=seasonal_order)
