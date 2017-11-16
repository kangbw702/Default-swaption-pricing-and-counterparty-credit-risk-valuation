__author__ = 'marcopereira'
import numpy as np
import pandas as pd
import quandl
import pickle, os
from Scheduler.Scheduler import Scheduler
from parameters import WORKING_DIR, x0Vas, t_step, simNumber, trim_start, trim_end, freq, referenceDate
QUANDL_API_KEY = "J_3ufFECZVffPxNDZuWf"
FRED_API_KEY = "90746840bcdc4851bf3ad921ded8a212"

class CorporateRates(object):
    def __init__(self):
        self.OIS = []
        self.filename = WORKING_DIR + '/CorpData.dat'
        self.corporates = []
        self.ratings = ['AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC']
        self.corpSpreads = {}
        self.corporates = pd.DataFrame()
        self.tenors = []
        self.unPickleMe(file = self.filename)
        self.myScheduler=Scheduler(start=trim_start, end=trim_end, freq=freq, reference=referenceDate)

    def getCorporates(self, trim_start, trim_end):
        curr_trim_end = trim_start
        if(self.corporates.size != 0):
            self.trim_start = self.corporates['OIS'].index.min().date()
            curr_trim_end = self.corporates['OIS'].index.max().date()
        if trim_end <= curr_trim_end:
            self.trim_end = curr_trim_end
            return self.corporates
        self.trim_start = trim_start
        self.trim_end = trim_end
        self.OIS = OIS(trim_start=trim_start, trim_end=trim_end)
        self.datesAll = self.OIS.datesAll
        self.datesAll.columns= [x.upper() for x in self.datesAll.columns]
        self.OISData = self.OIS.getOIS()
        for i in np.arange(len(self.OISData.columns)):
            freq = self.OISData.columns[i]
            self.tenors.append(self.myScheduler.extractDelay(freq=freq))
        for rating in self.ratings:
            index = 'ML/' + rating + 'TRI'
            try:
                corpSpreads = 1e-4 * (quandl.get(index, authtoken=QUANDL_API_KEY, trim_start=trim_start, trim_end=trim_end))
                corpSpreads.reset_index(level=0, inplace=True)
                corpSpreads = pd.merge(left=self.datesAll, right=corpSpreads, how='left')
                corpSpreads = corpSpreads.fillna(method='ffill').fillna(method='bfill')
                self.corpSpreads[rating] = corpSpreads.T.fillna(method='ffill').fillna(method='bfill').T
            except:
                print(index, " not found")
        self.corpSpreads = pd.Panel.from_dict(self.corpSpreads)
        self.corporates = {}
        self.OISData.drop('DATE', axis=1, inplace=True)
        ntenors = np.shape(self.OISData)[1]
        for rating in self.ratings:
            try:
                tiledCorps = np.tile(self.corpSpreads[rating]['VALUE'], ntenors).reshape(np.shape(self.OISData))
                self.corporates[rating] = pd.DataFrame(data=(tiledCorps + self.OISData.values), index=self.OISData.index, columns=self.OISData.columns)
            except:
                print("Error in addition of Corp Spreads")
        self.corporates['OIS'] = self.OISData
        self.corporates = pd.Panel(self.corporates)
        return self.corporates

    def getOISData(self, datelist=[]):
        if (len(datelist) != 0):
            return self.corporates["OIS"].loc[datelist]
        else:
            return self.self.corporates["OIS"]


    def getCorporateData(self, rating, datelist=[]):
        if (len(datelist) != 0):
            return self.corporates[rating].loc[datelist]
        else:
            return self.corporates[rating]

    def pickleMe(self):
        data = [self.corporates, self.corpSpreads]
        with open(self.filename, "wb") as f:
            pickle.dump(len(data), f)
            for value in data:
                pickle.dump(value, f)

    def unPickleMe(self, file):
        data = []
        if (os.path.exists(file)):
            with open(file, "rb") as f:
                for _ in range(pickle.load(f)):
                    data.append(pickle.load(f))
            self.corporates = data[0]
            self.corpSpreads = data[1]

    def saveMeExcel(self, whichdata, fileName):
        try:
            df = pd.DataFrame(whichdata)
        except:
            df = whichdata
        df.to_excel(fileName)

# Class OIS
class OIS(object):
    def __init__(self, trim_start="2005-01-10", trim_end="2010-01-10"):
        self.OIS = 0.01 * quandl.get("USTREASURY/YIELD", authtoken=QUANDL_API_KEY, trim_start=trim_start, trim_end=trim_end)
        self.OIS.reset_index(level=0, inplace=True)
        self.datesAll = pd.DataFrame(pd.date_range(trim_start, trim_end), columns=['DATE'])
        self.OIS.columns = [x.upper() for x in self.OIS.columns]
        self.OIS = pd.merge(left=self.datesAll, right=self.OIS, how='left')
        self.OIS = self.OIS.fillna(method='ffill').fillna(method='bfill')
        self.OIS = self.OIS.T.fillna(method='ffill').fillna(method='bfill').T
        self.OIS.index = self.datesAll.DATE

    def getOIS(self, datelist=[]):
        if (len(datelist) != 0):
            return self.OIS.loc[datelist]
        else:
            return self.OIS


if(__name__ == "__main__"):
    import quandl
    from parameters import WORKING_DIR, x0Vas, t_step, simNumber, trim_start, trim_end, freq, referenceDate
    #a = quandl.get("USTREASURY/YIELD", authtoken="J_3ufFECZVffPxNDZuWf", trim_start="2016-01-10", trim_end="2017-01-10")
    from Scheduler.Scheduler2 import Scheduler
    import pandas as pd
    import numpy as np

    mydatelist = Scheduler(start=trim_start, end=trim_end, freq=freq, reference=referenceDate).datelist1
    mycr = CorporateRates()
    bb = mycr.getCorporates(trim_start, trim_end)

    myois = OIS()
    aa = myois.getOIS(mydatelist)

    print(bb)



