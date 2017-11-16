import numpy as np
from dateutil.relativedelta import relativedelta
import pandas as pd

class Scheduler(object):

    def __init__(self):
        pass

    def getSchedule(self, start, end, freq, referencedate):
        #return pd.date_range(start=start,end=end,freq=freq).date
        date_tmp = start
        datelist = []
        while (date_tmp <= end):
            if (date_tmp >= referencedate):
                datelist.append(date_tmp)
            date_tmp += self.extractDelay(freq=freq)
        return datelist

    def extractDelay(self, freq):
        if type(freq) == list:
            freq = freq[0]
        if (freq == 'Date'): return relativedelta(days=+ 0)
        x = self.only_numerics(freq)
        if (x == ''):
            freqValue = 100
        else:
            freqValue = np.int(x)
            if (freq.upper().find('D') != -1): delta = relativedelta(days=+ freqValue)
            if (freq.upper().find('W') != -1): delta = relativedelta(weeks=+ freqValue)
            if (freq.find('M') != -1): delta = relativedelta(months=+ freqValue)
            if (freq.find('Y') != -1): delta = relativedelta(years=+ freqValue)
            if (freq.find('ZERO') != -1): delta = relativedelta(years=+ freqValue)
        return delta

    def only_numerics(self, seq):
        seq_type = type(seq)
        return seq_type().join(filter(seq_type.isdigit, seq))

if(__name__ == "__main__"):
    from datetime import date
    myscheduler = Scheduler()
    datelist = myscheduler.extractDelay(freq="3M")
    print(datelist)
    start = date(2016, 10, 1)
    end = date(2017, 7, 1)
    reference = date(2016, 10, 1)
    a = myscheduler.getSchedule(start, end, freq="3M", referencedate=reference)
    print(datelist)
    print(a[-1].__class__)
