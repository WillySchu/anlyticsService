from redisworker import Worker
import traceback

from analytics.insights import Insights
from analytics.forecast import Forecast

class InsightWorker(Worker):
    def run(self, data):
        print 'starting...'
        res = {}
        res['request'] = data
        res['request']['return_key'] = data['returnKey']

        envelope = data

        try:
            ins = Insights(envelope['payload'])
            fcast = Forecast(envelope['payload'])
            res['payload']['insights'] = ins.process()
            res['payload']['forecasts'] = fcast.process()
        except:
            err = traceback.format_exc()
            res['payload'] = {}
            # log.error(err)
            res['payload'] = err
            res['error'] = err

        self.q.put(res)
