__author__ = 'marcopereira'
import os
import pickle

import numpy as np
import pandas as pd
from dateutil import parser
from scipy.optimize import minimize
from parameters import trim_start, trim_end, t_step, simNumber


class CIRModel(object):

    def __init__(self, x=None):
        # __metaclass__ = Singleton
        # Vasicek Initialization
        self.t_step = t_step
        self.trim_start = trim_start
        self.trim_end = trim_end
        self.simNumber = simNumber
        self.x = x
        # internal representation of times series - integer multiples of t_step
        self.datelistlong = pd.date_range(self.trim_start, self.trim_end)
        self.datelistlong = [x.date() for x in self.datelistlong]
        self.ntimes = len(self.datelistlong)
        self.Libor = []
        self.smallLibor = []
        self.kappa = 0.0
        self.theta = 0.0
        self.sigma = 0.0
        self.r0 = 0.0
        # # SDE parameters - Vasicek SDE
        if (x != None):
            self.kappa = x[0]
            self.theta = x[1]
            self.sigma = x[2]
            self.r0 = x[3]
            self.LiborAvg = self.getLiborAvg(x=self.x, datelist=self.datelistlong)
            self.getLibor()
        #########################################
        #########################################
        #########################################
        #########################################

    def getLiborAvg(self, x, datelist):
        # this function is used to calculate bond under CIR framwork
        # dLambda(t) = kappa*(theta-Lambda(t))*dt + sigma*dW(t)
        kappa = x[0]
        theta = x[1]
        sigma = x[2]
        lambda0 = x[3]
        return Q


    def getLibor(self):
        # Integration of Vasicek Equation and addition on Column Zero of the
        # expected Vasicek Curve (Solution of Vsicek SDE.
        # Under these conditions, the pricing of any product contains in addition to the pricing on
        # each member of the emsemble of trajectories also the pricing under the expectation of those trajectories
        rd = np.random.standard_normal((self.ntimes, self.simNumber - 1))  # array of numbers for the number of samples
        r = np.zeros(np.shape(rd))
        nrows = np.shape(rd)[0]
        sigmaDT = self.sigma * np.sqrt(self.t_step)
        # calculate r(t)
        r[1, :] = self.r0 + r[1, :]
        for i in np.arange(2, nrows):
            r[i, :] = r[i - 1, :] + self.kappa * (self.theta - r[i - 1, :]) * self.t_step + sigmaDT * np.sqrt(
                r[i - 1, :]) * rd[i, :]
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

    #########################################
    #########################################
    #########################################

    def getSmallLibor(self, x=[], tenors=[], simNumber=1):
        # Get Libor simulated Curves for specific tenors or for all tenors if no datelist is provided
        # calculate indexes
        if (len(self.Libor) == 0):
            self.getLibor()
        self.smallLibor = self.Libor.loc[tenors]
        return pd.DataFrame(self.smallLibor, index=tenors)

    #####################################################################################
    def saveMeExcel(self, libor, liborName, fileName):
        df = pd.DataFrame(libor)
        df.to_excel(fileName, sheet_name=liborName, index=False)

    #####################################################################################
    def return_indices1_of_a(self, a, b):
        b_set = set(b)
        ind = [i for i, v in enumerate(a) if v in b_set]
        return ind

    #####################################################################################
    def return_indices2_of_a(self, a, b):
        index = []
        for item in a:
            index.append(np.bisect.bisect(b, item))
        return np.unique(index).tolist()

    def pickleMe(self, file):
        pickle.dump(self, open(file, "wb"))

    def unPickleMe(self, file):
        if (os.path.exists(file)):
            self = pickle.load(open(file, "rb"))
