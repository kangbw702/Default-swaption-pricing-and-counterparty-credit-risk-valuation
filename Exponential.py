__author__ = 'marcopereira'
import numpy as np
import pandas as pd
from dateutil import parser
from parameters import xR, trim_start, trim_end, t_step, simNumber



class Exponential(object):

    def __init__(self, x=[]):
        # Vasicek Initialization
        self.t_step = t_step
        self.trim_start = trim_start
        self.trim_end = trim_end
        self.simNumber = simNumber
        self.t_step = t_step
        self.datelist = []
        # internal representation of times series - integer multiples of t_step
        self.datelistlong = pd.date_range(self.trim_start, self.trim_end)
        self.datelistlong = [x.date() for x in self.datelistlong]
        self.ntimes = len(self.datelistlong)
        self.Libor = []
        self.x = x
        if (len(x) != 0):
            self.r0 = x[0]
            self.sigma = x[1]
            self.LiborAvg = self.getLiborAvg(x=self.x, datelist=self.datelistlong)
            self.getLibor()


    def getLibor(self):
        # Integration of Vasicek Equation and addition on Column Zero of the
        # expected Vasicek Curve (Solution of Vsicek SDE.
        # Under these conditions, the pricing of any product contains in addition to the pricing on
        # each member of the emsemble of trajectories also the pricing under the expectation of those trajectories
        rd = np.random.standard_normal((self.ntimes, self.simNumber - 1))  # array of numbers for the number of samples
        r = np.zeros(np.shape(rd))
        self.ntimes = nrows = np.shape(rd)[0]
        sigmaDT = self.sigma * np.sqrt(self.t_step)
        # calculate r(t)
        r[1, :] = self.r0 + r[1, :]
        for i in np.arange(2, nrows):
            r[i, :] = r[i - 1, :] + self.r0 * r[i - 1, :] * self.t_step + sigmaDT * r[i - 1, :] * rd[i, :]
            # calculate integral(r(s)ds)
        integralR = r.cumsum(axis=0) * self.t_step
        # calculate Libor
        self.Libor = pd.DataFrame(np.exp(-integralR), index=self.datelistlong)
        self.Libor.reset_index(level=0, inplace=True)
        self.LiborAvg.reset_index(level=0, inplace=True)
        self.Libor = pd.merge(left=self.LiborAvg[['index', 0]], right=self.Libor, how='left', on='index')
        self.Libor.set_index(keys=['index'], inplace=True)
        self.Libor.columns = np.arange(len(self.Libor.columns))
        self.LiborAvg.set_index(keys='index', inplace=True)
        return self.Libor

    def getLiborAvg(self, x, datelist):
        self.datelist = datelist
        ntimes = len(self.datelist)
        self.r = x[0]
        time0 = trim_start
        # this function is used to calculate exponential single parameter (r or lambda) Survival or Libor Functions
        QValues = np.exp(-(self.r + self.sigma * self.sigma * 0.5) * pd.DataFrame(
            [(x - trim_start).days / 365.0 for x in self.datelist], index=self.datelist))
        Q = pd.DataFrame(pd.np.tile(QValues.values, [1, simNumber]), index=self.datelist)
        return Q

    def getSmallLibor(self, x=[], datelist=[]):
        # Get Libor simulated Curves for specific datelist or for all datelist if no datelist is provided
        # calculate indexes
        if (len(self.Libor) == 0):
            self.getLibor()
        self.smallLibor = self.Libor.loc[datelist]
        return pd.DataFrame(self.smallLibor, index=datelist)


if(__name__=="__main__"):
    myExp= Exponential(x=xR)
    myExp.getLibor()
    mydateList=pd.date_range(start=trim_start,end=trim_end, freq="M").date
    mydateList.insert(trim_start)
    myExpData = myExp.getLiborAvg(x=xR, datelist=mydateList)
    print(myExpData)
    a=1
    myExpDataRnd = myExp.getSmallLibor(x=xR, datelist=mydateList)
    print(myExpDataRnd)
