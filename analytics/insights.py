import re
import arrow
import logging

log = logging.getLogger(__name__)

class Insights(object):
    def __init__(self, data):
        self.data = data
        self.dateRegex = r".+?(?=T)"

    # Main function for insight generation
    # generates as many possible insights if data is contiguous
    # else if two sets of data, compares those two
    # @returns Dict of generated insights
    def process(self):
        print 'hellloooooo'
        log.info('Harvesting...')
        results = [];


        if len(self.data) < 1:
            raise Exception('No Data')
        elif len(self.data) == 1:
            days = self.splitByDate(self.data[0])
            self.checkContiguousDates(days)
        elif len(self.data) == 2:
            return [compareArbitrary(self.data[1], self.data[0], 'adHoc')]
        else:
            days = self.data
            self.checkContiguousDates(days)

        dateStr = days[-1]["query"]["start-date"]
        # remove time component of date if applicable
        if len(dateStr) > 10:
            date = arrow.get(re.match(self.dateRegex, dateStr).group())
        else:
            date = arrow.get(dateStr)

        results.append(self.dayvsYesterday(days))

        if date.weekday() + 7 < len(days):
            results.append(self.weekToDate(days))

        if date.day + date.ceil('month').day < len(days):
            results.append(self.monthToDate(days))

        if (date - date.floor('quarter')).days + 92 < len(days):
            results.append(self.qtrToDate(days))

        # yearToDate
        # dayvsLastYear

        # Harvest some shit
        return results

    # Takes a group of time seriesed data and splits it out into groups for individual days
    # @param Dict of unsorted time seriesed data
    # @returns Array of data, sorted by date
    def splitByDate(self, data):
        result = []
        dates = {x[0] for x in data['rows']}

        for date in dates:
            # remove time component of date if applicable
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

    # Checks data to see if it contains all contiguous dates
    # if data is not contiguous, throws an error
    # @param Array of date sorted data
    # @returns Nothing
    def checkContiguousDates(self, data):
        numDays = (arrow.get(data[-1]['query']['start-date']) - arrow.get(data[0]['query']['start-date'])).days + 1
        if numDays != len(data):
            raise Exception('data set not contiguous')

    # Takes two arrays, aggregates them by date, compares them, and returns insights
    # @param Array first array
    # @param Array second array
    # @param String type of insight
    # @param Int number of insights to generate
    # @returns Array of insight dicts
    def compareArbitrary(self, current, last, t='type', n=5):
        current = self.aggregate(current)
        last = self.aggregate(last)
        dif = self.compare(current, last)
        return self.generateInsights(dif, n, t)

    # Splits an array of data up given the arbitrary params
    # @param Array of ga style time seriesed data
    # @param String start date of first period
    # @param String end date of first period
    # @param String start date of second period
    # @param String end date of second period
    # @param String the type name of the insights to be generated
    # @returns Tuple of data arrays
    def arbitraryPeriod(self, data, firstStart, firstEnd, secondStart, secondEnd):
        fp = [x for x in data if arrow.get(x['query']['start-date']) >= firstStart and arrow.get(x['query']['start-date']) <= firstEnd]
        sp = [x for x in data if arrow.get(x['query']['start-date']) >= secondStart and arrow.get(x['query']['start-date']) <= secondEnd]
        return (sp, fp)

    def weekToDate(self, data):
        t = 'weekToDate'
        log.debug(t)
        currentEnd = arrow.get(data[-1]['query']['start-date'])
        currentStart = currentEnd.floor('week')
        lastEnd = currentEnd.replace(weeks=-1)
        lastStart = lastEnd.floor('week')
        current, last = self.arbitraryPeriod(data, currentStart, currentEnd, lastStart, lastEnd)
        return self.compareArbitrary(current, last, t)

    def monthToDate(self, data):
        t = 'monthToDate'
        log.debug(t)
        currentEnd = arrow.get(data[-1]['query']['start-date'])
        currentStart = currentEnd.floor('month')
        lastEnd = currentEnd.replace(months=-1)
        lastStart = lastEnd.floor('month')
        current, last = self.arbitraryPeriod(data, currentStart, currentEnd, lastStart, lastEnd)
        return self.compareArbitrary(current, last, t)

    def qtrToDate(self, data):
        t = 'qtrToDate'
        log.debug(t)
        currentEnd = arrow.get(data[-1]['query']['start-date'])
        currentStart = currentEnd.floor('quarter')
        lastEnd = currentEnd.replace(quarters=-1)
        lastStart = lastEnd.floor('quarter')
        current, last = self.arbitraryPeriod(data, currentStart, currentEnd, lastStart, lastEnd)
        return self.compareArbitrary(current, last, t)

    def yearToDate(self, data):
        t = 'yearToDate'
        log.debug(t)
        currentEnd = arrow.get(data[-1]['query']['start-date'])
        currentStart = currentEnd.floor('year')
        lastEnd = currentEnd.replace(years=-1)
        lastStart = lastEnd.floor('year')
        current, last = self.arbitraryPeriod(data, currentStart, currentEnd, lastStart, lastEnd)
        return self.compareArbitrary(current, last, t)

    def dayvsYesterday(self, data):
        t = 'dayvsYesterday'
        log.debug(t)
        currentEnd = arrow.get(data[-1]['query']['start-date'])
        currentStart = currentEnd
        lastEnd = currentEnd.replace(days=-1)
        lastStart = lastEnd
        current, last = self.arbitraryPeriod(data, currentStart, currentEnd, lastStart, lastEnd)
        return self.compareArbitrary(current, last, t)

    def dayvsLastYear(self, data):
        t = 'dayvsLastYear'
        log.debug(t)
        currentEnd = arrow.get(data[-1]['query']['start-date'])
        currentStart = currentEnd
        lastEnd = currentEnd.replace(years=-1)
        lastStart = lastEnd
        current, last = self.arbitraryPeriod(data, currentStart, currentEnd, lastStart, lastEnd)
        return self.compareArbitrary(current, last, t)

    def weekvsLastYear(self, data):
        t = 'weekvsLastYear'
        log.debug(t)
        currentEnd = arrow.get(data[-1]['query']['start-date'])
        currentStart = currentEnd.floor('week')
        lastEnd = currentEnd.replace(years=-1)
        lastStart = lastEnd.floor('week')
        current, last = self.arbitraryPeriod(data, currentStart, currentEnd, lastStart, lastEnd)
        return self.compareArbitrary(current, last, t)

    # Generates insight dicts from compared and scored ga data
    # @param Dict compared and scored data
    # @param Int64 number of insights to generate
    # @param String type of insights to be generated
    # @returns Array of insight dicts
    def generateInsights(self, dif, n, t='type'):
        insights = []
        meta = dif['meta']
        del dif['meta']

        for met in dif.keys():
            for dim in dif[met].keys():
                insight = {}
                insight['startDate'] = meta['startDate']
                insight['endDate'] = meta['endDate']
                insight['metric'] = met
                insight['dimensions'] = dim
                insight['type'] = t
                insight['percentChange'] = dif[met][dim]['score']
                insight['significance'] = self.scoreSignificance(insight, dif[met][dim], meta['largest'][met])
                insights.append(insight)

        n = n if n < len(insights) else len(insights)
        insights = sorted(insights, key=lambda d: d['significance'])
        return insights[-n:]

    # Generates a significance score for a provided insight
    # @param Dict insight to generate score for
    # @param Dict comparison data that contains necessary metadata
    # @param Dict store of largest values used for normalization
    # @returns Float64 significance score of insight
    def scoreSignificance(self, insight, dif, largest):
        mag = dif['magnitude']
        insight['magnitude'] = mag
        insight['mag1'] = dif['mag1']
        insight['mag2'] = dif['mag2']
        normMag = mag / largest['mag']
        normPerc = abs(insight['percentChange']) / largest['perc']
        return normMag + normPerc

    # Compares two aggregated sets of ga style data to find % changes for each row
    # @param Dict first set of data, most recent
    # @param Dict second set of data, historical
    # @returns Dict a dictionary containing the % change for each row as well as metadata about the sets as a whole
    def compare(self, first, second):
        dif = {}
        largest = {}
        for met in first.keys():
            if met == 'meta':
                continue

            largest[met] = {}
            largest[met]['mag'] = 0
            largest[met]['perc'] = 0

            if met not in dif:
                dif[met] = {}

            for dim in first[met].keys():
                if dim in second[met]:
                    if second[met][dim] == 0:
                        continue
                    dif[met][dim] = {}
                    mag = abs(first[met][dim]) + abs(second[met][dim])
                    largest[met]['mag'] = mag if largest[met]['mag'] < mag else largest[met]['mag']

                    dif[met][dim]['score'] = (first[met][dim] - second[met][dim]) / second[met][dim]

                    perc = abs(dif[met][dim]['score'])
                    largest[met]['perc'] = perc if largest[met]['perc'] < perc else largest[met]['perc']

                    dif[met][dim]['magnitude'] = first[met][dim] + second[met][dim]
                    dif[met][dim]['mag1'] = first[met][dim]
                    dif[met][dim]['mag2'] = second[met][dim]

        meta = {}
        meta['startDate'] = second['meta']['startDate']
        meta['endDate'] = first['meta']['endDate']
        meta['largest'] = largest
        dif['meta'] = meta
        return dif

    # Aggregates and array of ga style time seriesed dictionaries into one, date agnostic, dictionary
    # @param Array of seperate ga style dicts
    # @returns Dict of aggregated data
    def aggregate(self, data):
        agg = {}
        meta = {}
        agg['meta'] = meta
        dimensions = data[0]['query']['dimensions']
        metrics = data[0]['query']['metrics']
        for met in metrics:
            agg[met] = {}

        for day in data:
            startDate = arrow.get(day['query']['start-date'])
            endDate = arrow.get(day['query']['end-date'])

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

            meta['endDate'] = meta['endDate'].format('YYYY-MM-DD')
            meta['startDate'] = meta['startDate'].format('YYYY-MM-DD')
            return agg
