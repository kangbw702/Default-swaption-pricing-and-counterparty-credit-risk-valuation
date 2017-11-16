from pandas import DataFrame
import numpy as np
import pandas as pd
from parameters import WORKING_DIR
from Scheduler.Scheduler import Scheduler
import os

class MC_CIR_Sim(object):
    def __init__(self):
        pass

    def setCIR(self, minDay, maxDay, x, simNumber, t_step):
        # dλ(t) = k(θ − λ(t))dt + σ*sqrt(λ(t))*dW(t)
        self.kappa = x[0]
        self.theta = x[1]
        self.sigma = x[2]
        self.r0 = x[3]
        self.simNumber = simNumber
        self.t_step = t_step
        # creation of a fine grid for Monte Carlo integration
        # Create fine date grid for SDE integration
        self.Schedule = Scheduler()
        self.datelistlong = self.Schedule.getSchedule(start=minDay,end=maxDay,freq="1M",referencedate=minDay)
        self.datelistlong_daily = pd.date_range(minDay, maxDay).tolist()
        self.datelistlong_daily = [x.date() for x in self.datelistlong_daily]
        self.ntimes = len(self.datelistlong)
        self.ntimes_daily = len(self.datelistlong_daily)
        self.survival = []
        self.smallSurvival = []

    def getSurvival(self):
        rd = np.random.standard_normal((self.ntimes, self.simNumber))  # array of numbers for the number of samples
        r = np.zeros(np.shape(rd))
        nrows = np.shape(rd)[0]
        sigmaDT = self.sigma * np.sqrt(self.t_step)
        #calculate λ(t)
        r[1,:] = self.r0 + r[1,:]
        for i in np.arange(2, nrows):
            r[i,:] = r[i-1,:] + self.kappa * (self.theta - r[i-1,:]) * self.t_step + sigmaDT * rd[i,:]*np.sqrt(r[i-1,:])
        # calculate integral(λ(s)ds)
        integralR = r.cumsum(axis=0) * self.t_step
        # calculate Survival Prob
        self.survival = np.exp(-integralR)
        self.survival = pd.DataFrame(data=self.survival, index=self.datelistlong)
        return self.survival

    def getSurvival_daily(self):
        t_step = 1.0/365
        rd = np.random.standard_normal((self.ntimes_daily, self.simNumber))  # array of numbers for the number of samples
        r = np.zeros(np.shape(rd))
        nrows = np.shape(rd)[0]
        sigmaDT = self.sigma * np.sqrt(t_step)
        #calculate λ(t)
        r[1,:] = self.r0 + r[1,:]
        for i in np.arange(2, nrows):
            r[i,:] = r[i-1,:] + self.kappa * (self.theta - r[i-1,:]) * t_step + sigmaDT * rd[i,:]*np.sqrt(r[i-1,:])
        # calculate integral(λ(s)ds)
        integralR = r.cumsum(axis=0) * t_step
        # calculate Survival Prob
        self.survival = np.exp(-integralR)
        self.survival = pd.DataFrame(data=self.survival, index=self.datelistlong_daily)
        # r = pd.DataFrame(data=r, index=self.datelistlong_daily)
        return self.survival

    def getHazard_daily(self):
        t_step = 1.0/365
        rd = np.random.standard_normal((self.ntimes_daily, self.simNumber))  # array of numbers for the number of samples
        r = np.zeros(np.shape(rd))
        nrows = np.shape(rd)[0]
        sigmaDT = self.sigma * np.sqrt(t_step)
        #calculate λ(t)
        r[1,:] = self.r0 + r[1,:]
        for i in np.arange(2, nrows):
            r[i,:] = r[i-1,:] + self.kappa * (self.theta - r[i-1,:]) * t_step + sigmaDT * rd[i,:]*np.sqrt(r[i-1,:])
        r = pd.DataFrame(data=r, index=self.datelistlong_daily)
        return r

    def getSmallSurvival(self,datelist = None):
        # calculate indexes
        if (datelist is None):
            datelist = self.datelist
        ind = self.return_indices1_of_a(self.datelistlong, datelist)
        self.smallSruvival = self.survival.iloc[ind, :]
        return self.smallSurvival

    def saveMeExcel(self):
        df = DataFrame(self.libor)
        df.to_excel(os.path.join(WORKING_DIR,'MC_CIR_Sim.xlsx'), sheet_name='survival', index=False)

    def return_indices1_of_a(self, a, b):
        b_set = set(b)
        ind = [i for i, v in enumerate(a) if v in b_set]
        return ind

    def return_indices2_of_a(self, a, b):
        index = []
        for item in a:
            index.append(np.bisect.bisect(b,item))
        return np.unique(index).tolist()


if(__name__ == "__main__"):
    import numpy as np
    import datetime
    from math import exp, sqrt
    from Scheduler.Scheduler import Scheduler
    from Calibration.CIR_calibrate import CIRLambdaCalibration

    trim_start = datetime.date(2005, 1, 10)
    trim_end = datetime.date(2010, 1, 10)
    t_step = 1/12
    simNumber = 5
    spread_datelist = np.array([6 / 12, 1, 2, 3, 4, 5, 7, 10])
    initialguess = np.array([0.003, 0.1, 0.05, 0.13])
    spread_market = 0.0001 * np.array([12.1, 13.6, 20.0, 24.8, 31.1, 35, 72.9, 121.1])

    # mycalibration = CIRLambdaCalibration(trim_start, trim_end)
    # mypara = mycalibration.getCalibratedParameters(initialguess, spread_datelist, spread_market)
    mysim = MC_CIR_Sim()
    mysim.setCIR(trim_start, trim_end, initialguess, simNumber, t_step)
    myq, r = mysim.getSurvival_daily()
    # print(mypara)
    print(r)


