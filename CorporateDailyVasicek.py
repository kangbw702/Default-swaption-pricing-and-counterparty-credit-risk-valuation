__author__ = 'marcopereira'
import numpy as np
import pandas as pd
import quandl
import pickle, os
from Scheduler.Scheduler import Scheduler
from parameters import WORKING_DIR
from MonteCarloSimulators.Vasicek.vasicekMCSim import MC_Vasicek_Sim
from fredapi import Fred

QUANDL_API_KEY = "J_3ufFECZVffPxNDZuWf"
FRED_API_KEY = "90746840bcdc4851bf3ad921ded8a212"

class CorporateRates(object):
    def __init__(self):
        self.OIS = []
        self.filename = WORKING_DIR + '/CorpData.dat'
        self.corporates = []
        self.ratings = {'AAA': "BAMLC0A1CAAA",
                        'AA':  "BAMLC0A2CAA",
                        'A':   "BAMLC0A3CA",
                        'BBB': "BAMLC0A4CBBB",
                        'BB':  "BAMLH0A1HYBB",
                        'B':   "BAMLH0A2HYB",
                        'CCC': "BAMLH0A3HYC"
                        }
        self.corpSpreads = {}
        self.corporates = pd.DataFrame()
        self.Qcorporates = pd.DataFrame() # survival function for corporates
        self.tenors = []
        self.unPickleMe(file=self.filename)
        self.myScheduler=Scheduler()
        self.myVasicek = MC_Vasicek_Sim()
        self.R = 0.4

    def getCorporatesFred(self, trim_start, trim_end):
        fred = Fred(api_key=FRED_API_KEY)
        curr_trim_end=trim_start
        if(self.corporates.size!=0):
            self.trim_start = self.corporates['OIS'].index.min().date()
            curr_trim_end = self.corporates['OIS'].index.max().date()
        if trim_end<=curr_trim_end:
            self.trim_end = curr_trim_end
            return self.corporates
        self.trim_start = trim_start
        self.trim_end = trim_end
        self.OIS = OIS(trim_start=trim_start, trim_end=trim_end)
        self.datesAll = self.OIS.datesAll
        self.datesAll.columns= [x.upper() for x in self.datesAll.columns]
        self.datesAll.index = self.datesAll.DATE
        self.OISData = self.OIS.getOIS()
        for i in np.arange(len(self.OISData.columns)):
            freq = self.OISData.columns[i]
            self.tenors.append(self.myScheduler.extractDelay(freq=freq))
        for rating in self.ratings.keys():
            index = self.ratings[rating]
            try:
                corpSpreads = 1e-2*(fred.get_series(index,observation_start=trim_start, observation_end=trim_end).to_frame())
                corpSpreads.index = [x.date() for x in corpSpreads.index[:]]
                corpSpreads = pd.merge(left=self.datesAll, right=corpSpreads, left_index=True, right_index=True, how="left")
                corpSpreads = corpSpreads.fillna(method='ffill').fillna(method='bfill')
                corpSpreads = corpSpreads.drop("DATE", axis=1)
                self.corpSpreads[rating] = corpSpreads.T.fillna(method='ffill').fillna(method='bfill').T
            except Exception as e:
                print(e)
                print(index, " not found")
        self.corpSpreads = pd.Panel.from_dict(self.corpSpreads)
        self.corporates = {}
        self.OISData.drop('DATE', axis=1, inplace=True)
        ntenors = np.shape(self.OISData)[1]
        for rating in self.ratings:
            try:
                tiledCorps = np.tile(self.corpSpreads[rating][0], ntenors).reshape(np.shape(self.OISData))
                self.corporates[rating] = pd.DataFrame(data=(tiledCorps + self.OISData.values),
                                                       index=self.OISData.index, columns=self.OISData.columns)
            except:
                print("Error in addition of Corp Spreads")
        self.corporates['OIS'] = self.OISData
        self.corporates = pd.Panel(self.corporates)
        return self.corporates


    def getCorporateData(self, rating, datelist=None):
    # This method gets a curve for a given date or date list for a given rating (normally this will be just a date).
    # It returns a dict of curves read directly from the corporate rates created by getCorporatesFred.
    # Derive delays from self.corporates[rating].columns
        myDelays = self.myScheduler.extractDelay(freq=list(self.corporates[rating].columns))
        if datelist is None:
            return
        outCurve = {}
        for day in datelist:
        # Create curves
        # ..............
        # ..............
        # add curve to outcurve dict
            outCurve[day]=myCurve
        return outCurve

    def getCorporateQData(self, rating, datelist=None, R=0.4):
        self.R = R
        if datelist is None:
            return
        outCurve = {}
        for day in datelist:
        # Create Q curves using q-tilde equation
        # ..............
        # ..............
            outCurve[day]=myCurve
        return outCurve


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
        self.OIS = 0.01 * quandl.get("USTREASURY/YIELD", authtoken=QUANDL_API_KEY, trim_start=trim_start,
                                     trim_end=trim_end)
        self.OIS.reset_index(level=0, inplace=True)
        self.datesAll = pd.DataFrame(pd.date_range(trim_start, trim_end), columns=['DATE'])
        self.OIS.columns = [x.upper() for x in self.OIS.columns]
        self.OIS = pd.merge(left=self.datesAll, right=self.OIS, how='left')
        self.OIS = self.OIS.fillna(method='ffill').fillna(method='bfill')
        self.OIS = self.OIS.T.fillna(method='ffill').fillna(method='bfill').T
        self.OIS.index = self.datesAll.DATE

    def getOIS(self, datelist=[]):
        if (len(datelist) != 0):
            return self.OIS.iloc[datelist]
        else:
            return self.OIS

if(__name__ == "__main__"):
    import quandl
    from parameters import WORKING_DIR, x0Vas, t_step, simNumber, trim_start, trim_end, freq, referenceDate
    #a = quandl.get("USTREASURY/YIELD", authtoken="J_3ufFECZVffPxNDZuWf", trim_start="2016-01-10", trim_end="2017-01-10")

    mycr = CorporateRates()
    curr_trim_end = trim_start

    FRED_API_KEY = "90746840bcdc4851bf3ad921ded8a212"
    fred = Fred(api_key=FRED_API_KEY)

    print(fred)
    #print(mycr.corporates['OIS'].index.min().date())
