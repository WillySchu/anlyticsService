import math
import arrow
import pandas as pd
import numpy as np
import statsmodels.api as sm

from scipy.optimize import brute

class Forecast:
    def __init__(self, data):
        self.data = data
        self.length = (arrow.get(data[0]['meta']['maxDate']) - arrow.get(data[0]['meta']['minDate'])).days + 1
        print self.length
        self.fcastLength = self.length // 5
        columns = [x['name'] for x in data[0]['columnHeaders']]
        rows = [x for x in data[0]['rows']]
        df = pd.DataFrame(rows, columns = columns)
        df['ga:date'] = pd.to_datetime(df['ga:date'], format = '%Y-%m-%d')

        df['ga:date'] = pd.DatetimeIndex(df['ga:date']).normalize()
        indices = [x for x in data[0]['query']['dimensions'] if x != 'ga:date']
        indices.append('ga:date')
        self.df = df.groupby(indices).sum()
        for met in self.data[0]['query']['metrics']:
            self.df[met] = self.df[met].astype(float)

    def process(self):
        res = self.forecast()
        return self.format_response(res)

    def forecast(self):
        mets = self.data[0]['query']['metrics']
        dims = [x for x in self.data[0]['query']['dimensions'] if x != 'ga:date']
        columns = dims + ['ga:date']

        preds = {}
        idxlength = len(self.data[0]['query']['dimensions']) - 1
        # print self.data[0]['query']

        # I feel like there should be a better way to iterate over the first
        # two indices without having to iterate over the third, but I'm
        # dumb so this will have to do for now
        for met in mets:
            dedup = {}
            preds[met] = pd.DataFrame(columns=columns+[met])
            z = 0
            for index, val in self.df[met].iteritems():
                idx = index[:idxlength]
                try:
                    if dedup[idx] is True:
                        continue
                except:
                    dedup[idx] = True
                    if len(self.df[met][idx]) < self.length or (self.df[met][idx].astype(float) == 0).any():
                        continue
                    z += 1
                    model = self.auto_arima(self.df[met][idx])
                    pred = model.predict(start=self.length, end=self.length + self.fcastLength, dynamic=True)
                    nf = pd.concat([self.df[met][idx], pred])

                    for i, v in nf.iteritems():
                        row = list(idx) + [i,v]
                        row = pd.Series(row, index=columns+[met])
                        preds[met] = preds[met].append(row, ignore_index=True)

                break

        for met in mets:
            try:
                res = res.merge(preds[met], how='outer')
            except Exception as err:
                res = preds[met]
                print err
                print '============'

        return res

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
            fit = sm.tsa.statespace.SARIMAX(x.astype(float), trend='n', order=order, seasonal_order=seasonal_order).fit()
            rmse = self.rmse(fit.resid)
            if math.isnan(rmse):
                print fit.resid
                return float('inf')
            return rmse
        except Exception as err:
            return float('inf')

    def auto_arima(self, x):
        grid = (slice(0, 3, 1), slice(0, 3, 1), slice(0, 3, 1), slice(0, 3, 1), slice(0, 3, 1), slice(0, 3, 1))
        res = brute(self.test_arima, grid, args=(x,), finish=None)
        if any(i != 0 for i in res):
            print res
            order = res[:3].astype(int)
            seasonal_order = res[3:].astype(int)
            seasonal_order = np.insert(seasonal_order, 3, 7)
            return sm.tsa.statespace.SARIMAX(x.astype(float), trend='n', order=order, seasonal_order=seasonal_order).fit()

    def format_response(self, res):
        if res.empty:
            return 'No forecasts possible'
        print res.to_json()
