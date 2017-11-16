__author__ = 'marcopereira'
import numpy as np
from pandas import DataFrame
from Scheduler.Scheduler import Scheduler
from MonteCarloSimulators.Vasicek.vasicekMCSim import MC_Vasicek_Sim
from parameters import trim_start, trim_end
#import quandl

class Bond(object):
    def __init__(self, libor, coupon, t_series):
        self.libor = libor
        self.coupon=coupon
        self.t_series = t_series
        self.ntimes=len(self.t_series)
        self.pvAvg=0.0
        self.ntimes = np.shape(self.libor)[0]
        self.ntrajectories = np.shape(self.libor)[1]
        self.cashFlows = DataFrame()
        return

    def PV(self):
        deltaT= np.zeros(self.ntrajectories)
        ones = np.ones(shape=[self.ntrajectories])
        for i in range(1,self.ntimes):
            deltaTrow = ((self.t_series[i]-self.t_series[i-1]).days/365)*ones
            deltaT = np.vstack ((deltaT,deltaTrow) )
        self.cashFlows= self.coupon*deltaT
        principal = ones
        self.cashFlows[self.ntimes-1,:] +=  principal
        pv = self.cashFlows*self.libor
        self.pvAvg = np.average(pv,axis=1)
        return self.pvAvg

    #def getScheduleComplete(self):
    #def setLibor(self, libor):
    #def getLiborAvg(self,yieldIn,datelist):
    def getYield(self,price):
        yield0 = 0.05 * self.ones
        self.price = price
        self.yieldIn -self.fitModel2Curve(x=yield0)
        return self.yieldIn

    def fitModel2Curve(self,x):
        results = minimize(fun=self.fCurve,x0=x)
        return results.x

    def fCurve(self,x):
        calCurve=self.getLiborAvg(x,self.datelist)
        thisPV = np.multiple(self.cashFlows,calcCurve).mean(axis=1).sum(axis=0)
        error = 1e4 * (self.price-thisPV) ** 2
        return

if(__name__ == "__main__"):
    coupon = 0.03
    myscheduler = Scheduler()
    datelist = myscheduler(start=trim_start,end=trim_end,freq="3M",referencedate=trim_start)
    myMC = MC_Vasicek_Sim(x=XR,datelist=datelist,simNumber=simnumber,t_step=t_step)
    libor = myMC.getSmallLibor(datelist=datelist)
    myBond = Bond(libor=libor, start=trim_start,maturity=trim_end,coupon=coupon, freq="3M",referencedate=trim_start)
    myPV = myBond.PV()
    print(myPV)
