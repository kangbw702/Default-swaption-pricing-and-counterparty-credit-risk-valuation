
import numpy as np
import pandas as pd
from scipy.optimize import minimize

from Products.Credit.CDS import CDS
from Scheduler.Scheduler import Scheduler


class BootstrapperCDSLadder(object):
    #  Class with Bootstrapping methods
    #  It can be used with CDS Ladder or KK Ratings CDS Ladder Converted Values
    def __init__(self, start, periods, Libor, Q, OIS,R):
        self.myCDS=[]
        pass


    # %% GetSpread
    def getSpreadBootstrapped(self, xQ, myCDS, s_quotes):
        pass

    def getSpreadList(self, xQ):
        spread=0.0
        return spread

    #  Fit CDS Ladder using Vasicek,CRI,etc Model.  Input parameters are x0 vector
    def CalibrateCurve(self, x0, quotes):
        # Bootstrap CDS Ladder Directly
        results = minimize(self.getSpreadBootstrapped, x0, (self.myCDS, quotes))
        return results.x
