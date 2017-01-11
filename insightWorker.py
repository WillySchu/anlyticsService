import redis
import json
import threading
import Queue

from log import Log
from insights import Insights
# from forecast import Forecast

log = Log()

r = redis.StrictRedis(host='localhost', port=6379, db=0)
p = redis.StrictRedis(host='localhost', port=6379, db=0)

class InsightWorker(object):
    def __init__(self, queue):
        self.queue = queue
        self.q = Queue.Queue()

    def listen(self):
        while True:
            o = r.brpop(self.queue, timeout=60)
            if o is not None:
                t = iThread(self.go, o)
                t.start()
                self.pub()

    def go(self, data):
        logging.info('starting')
        envelope = json.loads(data[1])
        ins = Insights(envelope['payload'])
        # fcast = Forecast(envelope['payload'])
        try:
            envelope['payload'] = ins.process()
        except Exception as err:
            logging.error(err)
            envelope['payload'] = err.args
            envelope['error'] = err.args

        self.q.put(envelope)

    def pub(self):
        s = self.q.get()
        p.publish(s['returnKey'], json.dumps(s))
        logging.info('published')
        logging.info(s['returnKey'])

class iThread(threading.Thread):
    def __init__(self, callback, data):
        threading.Thread.__init__(self)
        self.callback = callback
        self.data = data

    def run(self):
        self.callback(self.data)
