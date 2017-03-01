import math

import statsmodels.api as sm
import pandas as pd
import numpy as np

from scipy.optimize import brute


# Method for getting the rmse value for an arbitrarily parameterized
# SARIMAX model for the provided data
# This is used by auto_arima's brute force process to identify
# the "best" model
# @param List the orders for the SARIMAX parameters, first three to
# are the non seasonal terms, last three the seasonal terms
# @param Series data to be fit
# @returns Float rmse value of the fitted model
def test_arima(orders, x):
    # slice up the orders
    order = orders[:3]
    seasonal_order = orders[3:]
    # hardcode insert seven period seasonality
    # this will need to become more dynamic later when we deal with
    # multi day long periods
    seasonal_order = np.insert(seasonal_order, 3, 7)
    try:
        fit = sm.tsa.statespace.SARIMAX(x.astype(float), trend='n', order=order, seasonal_order=seasonal_order).fit()
        error = rmse(fit.resid)
        if math.isnan(error):
            return float('inf')
        return error
    except Exception as err:
        return float('inf')

# Root mean squared error function
# calculates the rmse of a list of residuals, used to measure
# the error of different models in model selection
# @param List list of residual values from a model
# @returns Float value of the rmse
def rmse(resid):
    rmse = 0
    for r in resid:
        rmse += math.sqrt(r**2)

    return rmse


# Uses scipy's optimize.brute method to iterate through every possible
# combination of SARIMAX models and fit them, then return the parameter
# values that yield the best fit.
# https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.optimize.brute.html
# @param Series values to be fit
# @returns SARIMAXResults result of best fit
def auto_arima(x):
    grid = (slice(0, 3, 1), slice(0, 3, 1), slice(0, 3, 1), slice(0, 3, 1), slice(0, 3, 1), slice(0, 3, 1))
    res = brute(test_arima, grid, args=(x,), finish=None)
    print res
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    if any(i != 0 for i in res):
        # slice up orders
        order = res[:3].astype(int)
        seasonal_order = res[3:].astype(int)
        # hardcode insert seven period seasonality
        # this will need to become more dynamic later when we deal with
        # multi day long periods
        seasonal_order = np.insert(seasonal_order, 3, 7)
        return sm.tsa.statespace.SARIMAX(x.astype(float), trend='n', order=order, seasonal_order=seasonal_order).fit()
