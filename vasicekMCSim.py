
# Modify Vasicek MC Simulator:
# to include the expected curve at column 0 in getLibor()
# include a method to create the expected curve given x, datelist)
# include a method that will find x that will fit a given input Q or Z.
# This requires the use of an optimization package.

from pandas import DataFrame
import numpy as np
import pandas as pd
from parameters import WORKING_DIR
import os

class MC_Vasicek_Sim(object):
    def __init__(self):
        pass

    def setVasicek(self, x, minDay, maxDay, simNumber, t_step):
        # SDE parameters - Vasicek SDE
        # dr(t) = k(θ − r(t))dt + σdW(t)
        self.kappa = x[0]
        self.theta = x[1]
        self.sigma = x[2]
        self.r0 = x[3]
        self.simNumber = simNumber
        self.t_step = t_step
        # internal representation of times series - integer multiples of t_step
        #self.datelist = datelist
        # creation of a fine grid for Monte Carlo integration
        # Create fine date grid for SDE integration
        #minDay = min(datelist)
        #maxDay = max(datelist)
        self.datelistlong = pd.date_range(minDay, maxDay).tolist()
        self.datelistlong = [x.date() for x in self.datelistlong]
        self.ntimes = len(self.datelistlong)
        self.libor = []
        self.smallLibor = []
        return

    def getLibor(self):
        # array of numbers for the number of samples
        # numpy.ndarray. row index - date. Col index - trajectory
        rd = np.random.standard_normal(size = (self.ntimes,self.simNumber))
        r = np.zeros(np.shape(rd))
        nrows = np.shape(rd)[0]
        sigmaDT = self.sigma * np.sqrt(self.t_step)
        # calculate r(t)
        r[1, :] = self.r0 + r[1, :]
        for i in np.arange(2,nrows):
            r[i, :] = r[i-1, :] + self.kappa*(self.theta-r[i-1, :])*self.t_step + sigmaDT*rd[i, :]
        # calculate integral(r(s)ds)
        integralR = r.cumsum(axis=0)*self.t_step
        # calculate Libor
        self.libor = np.exp(-integralR)
        self.libor = pd.DataFrame(data=self.libor, index=self.datelistlong)
        return self.libor

    def getSmallLibor(self, datelist = None):
        # calculate indexes
        if(datelist is None):
            datelist = self.datelist
        #self.smallLibor = self.libor.loc[self.datelist]
        ind = self.return_indices1_of_a(self.datelistlong, datelist)
        self.smallLibor = self.libor.iloc[ind,:]
        return self.smallLibor

    def saveMeExcel(self):
        df = DataFrame(self.libor)
        df.to_excel(os.path.join(WORKING_DIR,'MC_Vasicek_Sim.xlsx'), sheet_name='libor', index=False)

    def return_indices1_of_a(self, a, b):
        b_set = set(b)
        ind = [i for i, v in enumerate(a) if v in b_set]
        return ind

    def return_indices2_of_a(self, a, b):
        index=[]
        for item in a:
            index.append(np.bisect.bisect(b,item))
        return np.unique(index).tolist()




    # def fitcurve(self, marketcurve, ):
    #     market_datelist = func(marketcurve)
    #     smalllibor = func(self.libor, market_datelist)
    #     # minimize |smalllibor - marketcurve| using some optimize function
    #     error = xxx
    #     calibrated_parameters = xxx
    #     return calibrated_parameters
    

if(__name__ == "__main__"):
    from parameters import WORKING_DIR, x0Vas, t_step, simNumber, trim_start, trim_end, freq, referenceDate
    from Scheduler.Scheduler2 import Scheduler
    import pandas as pd
    import numpy as np

    mydatelist = Scheduler(start=trim_start, end=trim_end, freq=freq, reference=referenceDate).datelist1
    x = x0Vas.values[0]
    mysim = MC_Vasicek_Sim(mydatelist, x, simNumber, t_step)
    # pandas.tseries.index.DatetimeIndex, list, pandas.tslib.Timestamp
    #a = pd.date_range(min(mydatelist), max(mydatelist))
    #b = a.tolist()
    # numpy.ndarray
    #rd = np.random.standard_normal(size=(5, 3))
    #r = np.zeros((np.shape(rd)[0], np.shape(rd)[1]+1))
    rr = mysim.getLibor()
    mysim.saveMeExcel()

    #print(rr.loc[mydatelist])
    #print(integralR)
    #print(libor)