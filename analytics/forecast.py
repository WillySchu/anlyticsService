import math
import arrow
import pandas as pd
import numpy as np
import statsmodels.api as sm

from arima import auto_arima
from scipy.optimize import brute

class Forecast:
    # Constructor function takes a GA style data response and reformats it
    # into a pandas dataframe to use for forecasting
    # @param List GA style data with ga:date as a dimension
    # @returns None
    def __init__(self, data):
        self.data = data
        self.fcasts = []

        if len(self.data) < 1:
            raise Exception('No Data')
        try:
            self.start_date = arrow.get(data[0]['meta']['minDate'])
            self.end_date = arrow.get(data[0]['meta']['maxDate'])
        except KeyError:
            self.start_date = arrow.get(data[0]['query']['start-date'])
            self.end_date = arrow.get(data[0]['query']['end-date'])

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
    # @returns List forecast objects
    def process(self):
        if self.fcastLength < 1:
            raise Exception('Insufficient data for forecasting')
        self.forecast()
        return self.fcasts

    # Creates forecasts
    # Loops through each seperate segment, tests it for length and continuity
    # and attempts to fit an SARIMAX model to it by brute force.
    # @returns DataFrame original data plus forecasted values
    def forecast(self):
        mets = self.data[0]['query']['metrics']

        self.idxlength = len(self.data[0]['query']['dimensions']) - 1

        # I feel like there should be a better way to iterate over the first
        # two indices without having to iterate over the third, but I'm
        # dumb so this will have to do for now
        # MET-984
        for met in mets:
            n = 0;
            dedup = {}
            if self.idxlength > 0:
                for index, val in self.df[met].iteritems():
                    idx = index[:self.idxlength]

                    if dedup.get(idx, False):
                        continue

                    dedup[idx] = True
                    n += 1
                    self.get_forecast(self.df[met][idx], idx, met)

                    # hack for now,
                    # only generate one forecasted segment per metric
                    if n > 3:
                        break
            else:
                self.get_forecast(self.df[met], [], met)

    # Calls auto_arima and appends results to fcasts list given data parameters
    # @param pandas Series segment of data to forecast
    # @param List list of dimensions
    # @param String metric
    def get_forecast(self, data, idx, met):
        if len(data) < self.length or (data.astype(float) == 0).any():
            return None
        model = auto_arima(data)
        if model == None:
            return None
        pred = model.get_prediction(start=self.length, end=self.length + self.fcastLength, dynamic=True)

        self.fcasts.append(self.format_forecast(met, data.values, pred, idx))

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
            if self.idxlength > 0:
                for i, v in sub.iteritems():
                    idx = i[:self.idxlength]

                    if dedup.get(idx, False):
                        continue

                    dedup[idx] = True
                    vals = sub[idx].values

                    if np.isnan(sub[idx].values).any():
                        continue

                    res.append(self.format_forecast(met, vals, idx))
            else:
                res.append(self.format_forecast(met, sub.values, []))

        return res

    # Builds a forecast results object given appropriate values
    # This should probably be replaced by a Class soon
    # @param String metric
    # @param pandas Series historical data used to forecast
    # @param pandas Series forecast
    # @param idx List dimensions
    # @returns Object forecast object
    def format_forecast(self, met, vals, pred, idx):
        fcast = {}

        fcast['startDate'] = self.start_date.format('YYYY-MM-DD')
        fcast['endDate'] = self.end_date.format('YYYY-MM-DD')
        fcast['length'] = self.fcastLength
        fcast['metric'] = met
        fcast['dimensions'] = ','.join(i for i in idx)
        fcast['values'] = vals.tolist()
        fcast['forecast'] = pred.predicted_mean.values.tolist()[1:]
        fcast['lower_ci'] = pred.conf_int().iloc[1:, 0].values.tolist()
        fcast['upper_ci'] = pred.conf_int().iloc[1:, 1].values.tolist()

        return fcast
