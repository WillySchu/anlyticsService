import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)
p = r.pubsub()

class insightWorker:
    def __init__(self, queue):
        self.queue = queue

    def listen(self):
        while True:
            o = r.brpop(self.queue, timeout=60)
            print(o)

    def 
