import redis
import json
import threading
import Queue

from insights import Insights

r = redis.StrictRedis(host='localhost', port=6379, db=0)
p = redis.StrictRedis(host='localhost', port=6379, db=0)

class InsightWorker:
    def __init__(self, queue):
        self.queue = queue
        self.q = Queue.Queue()

    def listen(self):
        while True:
            o = r.brpop(self.queue, timeout=60)
            print(o)

            # t = threading.Thread(target=self.go, args=o, kwargs=None)
            # t.start()
            t = iThread(self.go, o)
            t.start()
            self.pub()

    def go(self, data):
        data = json.loads(data[1])
        ins = Insights(data)
        self.q.put(ins.process())

    def pub(self):
        s = self.q.get()
        print(s['returnKey'])
        print('>>>>>>>>>>>>>>>>>>>>>>')
        print(s['returnKey'])
        p.publish(s['returnKey'], json.dumps(s))

class iThread(threading.Thread):
    def __init__(self, callback, data):
        threading.Thread.__init__(self)
        self.callback = callback
        self.data = data

    def run(self):
        self.callback(self.data)
