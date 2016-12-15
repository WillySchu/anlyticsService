#
#
# class Insights:
#     def __init__(self, data):
#         self.data = data
#
#     def process(self):
#         print('Harvesting...')
#         results = [];
#
#         if len(data) < 1:
#             # throw an error
#         elif len(data) == 1:
#             # split by date
#             # check contiguous
#         elif len(data) == 2:
#             # compare
#             # return
#         else:
#             # check contiguous
#
#
#         return self.data
import subprocess

class Insights:
    def __init__(self, data):
        self.data = data

    def process(self):
        print('Harvesting...')
        subprocess.call(['./launch.sh', self.data])
        print 'end'
