import math
import pandas as pd
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
        indices = data[0]['query']['dimensions']
        df.set_index('ga:date', inplace=True)


        print df.head()
        # print df.ix
        # print df.where(df.)

    def process(self):
        return self.data

    def test_arima(orders, x):
        order = orders[:3]
        seasonal_order = orders[3:]
        seasonal_order = np.insert(seasonal_order, 3, 12)
        try:
            fit = sm.tsa.statespace.SARIMAX(x, trend='n', order=order, seasonal_order=seasonal_order).fit()
            if math.isnan(fit.aic):
                return float('inf')
            return fit.bic
        except:
            return float('inf')

    def auto_arima(x):
        grid = (slice(0, 3, 1), slice(0, 3, 1), slice(0, 3, 1), slice(0, 3, 1), slice(0, 3, 1), slice(0, 3, 1))
        res = brute(self.test_arima, grid, args=(x,), finish=None)
        order = res[0][:3]
        seasonal_order = res[0][3:]
        seasonal_order = np.insert(seasonal_order, 3, 12)
        return sm.tsa.statespace.SARIMAX(x, trend='n', order=order, seasonal_order=seasonal_order)
