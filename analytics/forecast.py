import math
import arrow
import pandas as pd
import numpy as np
import statsmodels.api as sm

from scipy.optimize import brute

class Forecast:
    # Constructor function takes a GA style data response and reformats it
    # into a pandas dataframe to use for forecasting
    # @param List GA style data with ga:date as a dimension
    # @returns None
    def __init__(self, data):
        self.data = data

        if len(self.data) < 1:
            raise Exception('No Data')

        self.start_date = arrow.get(data[0]['meta']['minDate'])
        self.end_date = arrow.get(data[0]['meta']['maxDate'])
        self.length = (self.end_date - self.start_date).days + 1
        # number of days to forecast
        self.fcastLength = self.length // 5
        columns = [x['name'] for x in data[0]['columnHeaders']]
        rows = [x for x in data[0]['rows']]
        df = pd.DataFrame(rows, columns = columns)
        # set ga:date column to datetime type
        df['ga:date'] = pd.to_datetime(df['ga:date'], format = '%Y-%m-%d')
        df['ga:date'] = pd.DatetimeIndex(df['ga:date']).normalize()
        # skip and then append date to ensure proper order
        self.indices = [x for x in data[0]['query']['dimensions'] if x != 'ga:date']
        self.indices.append('ga:date')
        # set indices to ga dimensions
        self.df = df.groupby(self.indices).sum()
        for met in self.data[0]['query']['metrics']:
            self.df[met] = self.df[met].astype(float)

    # Make forecasts and then reformat responses
    # @returns None
    def process(self):
        res = self.forecast()
        return self.format_response(res)

    # Creates forecasts
    # Loops through each seperate segment, tests it for length and continuity
    # and attempts to fit an SARIMAX model to it by brute force.
    # @returns DataFrame original data plus forecasted values
    def forecast(self):
        mets = self.data[0]['query']['metrics']

        preds = {}
        self.idxlength = len(self.data[0]['query']['dimensions']) - 1

        # I feel like there should be a better way to iterate over the first
        # two indices without having to iterate over the third, but I'm
        # dumb so this will have to do for now
        for met in mets:
            n = 0;
            dedup = {}
            preds[met] = pd.DataFrame(columns=self.indices+[met])
            for index, val in self.df[met].iteritems():
                idx = index[:self.idxlength]
                try:
                    if dedup[idx] is True:
                        continue
                except:
                    dedup[idx] = True
                    n += 1
                    if len(self.df[met][idx]) < self.length or (self.df[met][idx].astype(float) == 0).any():
                        continue
                    model = self.auto_arima(self.df[met][idx])
                    if model == None:
                        continue
                    pred = model.predict(start=self.length, end=self.length + self.fcastLength, dynamic=True)
                    values = pd.concat([self.df[met][idx], pred])

                    # reconstruct series with dimensions from original and
                    # forecasted values and append it to results DataFrame
                    for i, v in values.iteritems():
                        row = list(idx) + [i,v]
                        row = pd.Series(row, index=self.indices+[met])
                        preds[met] = preds[met].append(row, ignore_index=True)

                # hack for now,
                # only generate one forecasted segment per metric
                if n > 3:
                    break

        # merge separate metrics back into one dataframe
        for met in mets:
            try:
                res = res.merge(preds[met], on=self.indices, how='outer')
            except Exception as err:
                res = preds[met]
                print err
                print '============'

        return res.groupby(self.indices).sum()

    # Root mean squared error function
    # calculates the rmse of a list of residuals, used to measure
    # the error of different models in model selection
    # @param List list of residual values from a model
    # @returns Float value of the rmse
    def rmse(self, resid):
        rmse = 0
        for r in resid:
            rmse += math.sqrt(r**2)

        return rmse

    # Method for getting the rmse value for an arbitrarily parameterized
    # SARIMAX model for the provided data
    # This is used by auto_arima's brute force process to identify
    # the "best" model
    # @param List the orders for the SARIMAX parameters, first three to
    # are the non seasonal terms, last three the seasonal terms
    # @param Series data to be fit
    # @returns Float rmse value of the fitted model
    def test_arima(self, orders, x):
        # slice up the orders
        order = orders[:3]
        seasonal_order = orders[3:]
        # hardcode insert seven period seasonality
        # this will need to become more dynamic later when we deal with
        # multi day long periods
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

    # Uses scipy's optimize.brute method to iterate through every possible
    # combination of SARIMAX models and fit them, then return the parameter
    # values that yield the best fit.
    # https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.optimize.brute.html
    # @param Series values to be fit
    # @returns SARIMAXResults result of best fit
    def auto_arima(self, x):
        grid = (slice(0, 3, 1), slice(0, 3, 1), slice(0, 3, 1), slice(0, 3, 1), slice(0, 3, 1), slice(0, 3, 1))
        res = brute(self.test_arima, grid, args=(x,), finish=None)
        if any(i != 0 for i in res):
            # slice up orders
            order = res[:3].astype(int)
            seasonal_order = res[3:].astype(int)
            # hardcode insert seven period seasonality
            # this will need to become more dynamic later when we deal with
            # multi day long periods
            seasonal_order = np.insert(seasonal_order, 3, 7)
            return sm.tsa.statespace.SARIMAX(x.astype(float), trend='n', order=order, seasonal_order=seasonal_order).fit()

    # Formats response dictionary constructed from results DataFrame,
    # this puts the data in a more node friendly format to be returned
    # to the client
    # @param DataFrame results of forecasting
    # @returns List contains a dictionary for each forecasted segment
    def format_response(self, df):
        if df.empty:
            return 'No forecasts possible'

        res = []

        # I feel like there should be a better way to iterate over the first
        # two indices without having to iterate over the third, but I'm
        # dumb so this will have to do for now
        for met, sub in df.iteritems():
            dedup = {}
            for i, v in sub.iteritems():
                idx = i[:self.idxlength]
                try:
                    if dedup[idx]:
                        continue
                except:
                    dedup[idx] = True
                    vals = sub[idx].values

                    if np.isnan(sub[idx].values).any():
                        continue

                    fcast = {}

                    fcast['startDate'] = self.start_date.format('YYYY-MM-DD')
                    fcast['endDate'] = self.end_date.format('YYYY-MM-DD')
                    fcast['length'] = self.fcastLength
                    fcast['metric'] = met
                    fcast['dimensions'] = ','.join(i for i in idx)
                    fcast['values'] = vals[:-self.fcastLength].tolist()
                    fcast['forecast'] = vals[-self.fcastLength:].tolist()

                    res.append(fcast)

        return res
