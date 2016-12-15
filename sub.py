import subprocess

class Insights:
    def __init__(self, data):
        self.data = data

    def process(self):
        print('Harvesting...')
        subprocess.call(['./launch.sh', self.data])
        print 'end'
