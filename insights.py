import re
import dateutil.parser
from datetime import date, timedelta

class Insights:
    def __init__(self, data):
        self.data = data
        self.dateRegex = r".+?(?=T)"

    def process(self):
        print('Harvesting...')
        results = [];

        if len(self.data) < 1:
            pass
            # throw an error
        elif len(self.data) == 1:
            pass
            days = self.splitByDate(self.data[0])
            # check contiguous
        elif len(self.data) == 2:
            pass
            # compare
            # return
        else:
            pass
            # check contiguous

        a = self.aggregate(days[0:])

        print a

        # Harvest some shit
        return self.data

    def splitByDate(self, data):
        result = []
        dates = {x[0] for x in data['rows']}

        for date in dates:
            if len(date) > 10:
                dDate = re.match(self.dateRegex, date).group()
            else:
                dDate = date
            res = {}
            res['query'] = {}
            res['query']['start-date'] = dDate
            res['query']['end-date'] = dDate
            res['query']['dimensions'] = data['query']['dimensions']
            res['query']['metrics'] = data['query']['metrics']
            res['columnHeaders'] = data['columnHeaders'][1:]
            res['rows'] = [x[1:] for x in data['rows'] if x[0] == date]
            result.append(res)


        result = sorted(result, key=lambda d: map(int, d['query']['start-date'].split('-')))

        return result

    def checkContiguousDates(self, data):
        lastDate = ''
        oneDay = timedelta(day=1)

    def aggregate(self, data):
        agg = {}
        meta = {}
        agg['meta'] = {}
        dimensions = data[0]['query']['dimensions']
        metrics = data[0]['query']['metrics']
        for met in metrics:
            agg[met] = {}

        for day in data:
            startDate = dateutil.parser.parse(day['query']['start-date'])
            endDate = dateutil.parser.parse(day['query']['end-date'])

            if startDate != endDate:
                raise Exception('Harvestor received non exploded data')

            if 'startDate' not in meta:
                meta['startDate'] = startDate

            if 'endDate' not in meta:
                meta['endDate'] = endDate

            if startDate < meta['startDate']:
                meta['startDate'] = startDate

            if endDate > meta['endDate']:
                meta['endDate'] = endDate

            for i in range(0,len(day['rows'])):
                dimName = ''
                for j in range(0,len(day['rows'][0])):
                    if day['columnHeaders'][j]['columnType'] == 'DIMENSION':
                        if len(dimName) > 0:
                            dimName += ','
                        dimName += day['rows'][i][j]
                    else:
                        met = day['columnHeaders'][j]['name']
                        if dimName in agg[met]:
                            agg[met][dimName] += float(day['rows'][i][j])
                        else:
                            agg[met][dimName] = float(day['rows'][i][j])

            return agg
