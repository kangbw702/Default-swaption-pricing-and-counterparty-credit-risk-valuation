import numpy as np
import math
from math import exp, sqrt
import datetime
from Curves.OIS.OIS import OIS
from scipy.optimize import leastsq, minimize, least_squares
QUANDL_API_KEY = "J_3ufFECZVffPxNDZuWf"
FRED_API_KEY = "90746840bcdc4851bf3ad921ded8a212"


class CIRLambdaCalibration(object):

    def __init__(self, trim_start="2005-01-10", trim_end="2010-01-10"):
        # SDE parameters - CIR SDE
        # dr(t) = k(θ − r(t))dt + σr(t)^0.5 dW(t)
        self.recovery = 0.4
        self.OIS = OIS(trim_start, trim_end)  # discount factor
        self.DCF = self.OIS.getDiscountFactor().loc[trim_start]
        self.fre = 3 / 12  # in the unit of year

    # closed form of CIR hazard rate survival probability,
    # similar to the zero coupon bond price under CIR short rate
    def getSurvival(self, initial_lambda, kappa, theta, sigma, duration):
        h = sqrt(kappa**2 + 2*sigma**2)
        A = (2*h*exp((h+kappa)*duration/2) / (2*h + (h+kappa)*(exp(h*duration)-1))) ** (2*kappa*theta/(sigma**2))
        B = 2*(exp(h*duration)-1)/(2*h + (h+kappa)*(exp(h*duration)-1))
        return A * exp(-initial_lambda * B)

    # Define the function for default leg
    def DefaultLeg(self, initial_lambda, kappa, theta, sigma, spread_datelist):
        spread_datelist = (spread_datelist*12).astype(int)
        fre = self.fre * 12
        DL = np.array([])
        for i in spread_datelist:
            tempDL = 0
            for j in range(int(i/fre)):
                CouponStart = j * fre /12
                CouponEnd = (j + 1) * fre /12
                QStart = self.getSurvival(initial_lambda,kappa,theta,sigma, CouponStart)
                QEnd = self.getSurvival(initial_lambda, kappa, theta, sigma, CouponEnd)
                tempDL += (1 - self.recovery) * self.DCF[(j+1)*fre] * (QStart - QEnd)
            DL = np.append(DL, tempDL)
        return DL

    # Define the function for risk annuity
    def RiskAnnuity(self, initial_lambda, kappa, theta, sigma, spread_datelist):
        spread_datelist = (spread_datelist * 12).astype(int)
        fre = self.fre * 12
        RA = np.array([])

        for i in spread_datelist:
            tempRA = 0
            for j in range(int(i/fre)):
                CouponStart, CouponEnd = (j*fre) / 12, ((j + 1)*fre) /12
                QStart = self.getSurvival(initial_lambda, kappa, theta, sigma, CouponStart)
                QEnd = self.getSurvival(initial_lambda, kappa, theta, sigma, CouponEnd)
                tempRA += 0.5 * (1/12) * fre * self.DCF[(j+1)*fre] * (QStart + QEnd)
            RA = np.append(RA, tempRA)

        return RA

    def getSpread_Model(self, initial_lambda, parameters, spread_datelist):
        dl = self.DefaultLeg(initial_lambda, parameters[0], parameters[1], parameters[2], spread_datelist)
        pl = self.RiskAnnuity(initial_lambda, parameters[0], parameters[1], parameters[2], spread_datelist)
        return dl / pl

    # def getSpread_Model(self, parameters, spread_datelist):
    #     dl = self.DefaultLeg(parameters[0], parameters[1], parameters[2], parameters[3], spread_datelist)
    #     pl = self.RiskAnnuity(parameters[0], parameters[1], parameters[2], parameters[3], spread_datelist)
    #     return dl / pl

    def getCalibratedParameters(self, initial_lambda, parameters, spread_datelist, spread_market):
        # ErrorFunc = lambda x: self.getSpread_Model(x, self.spread_datelist) - self.spread_market
        ErrorFunc = lambda x: (self.getSpread_Model(initial_lambda, x, spread_datelist) - spread_market)**2
        # bnds = ((0, None), (0, None), (0, None), (0, None))
        # cons = ({'type': 'ineq', 'fun': lambda x: 2 * x[1] * x[2] - x[3] * x[3]})
        result = least_squares(ErrorFunc, x0=parameters, bounds=([0, np.inf]))
        # result = minimize(ErrorFunc, x0=parameters, bounds=bnds, constraints=cons)
        return result.x

if(__name__ == "__main__"):
    import numpy as np
    import math
    from math import exp, sqrt
    from Curves.OIS.OIS import OIS
    # from math import exp
    from scipy.optimize import leastsq

    trim_start = "2005-01-10"
    trim_end = "2010-01-10"
    recovery = 0.4
    time0 = datetime.date(2005, 1, 10)
    spread_datelist = np.array([6/12, 1, 2, 3, 4, 5, 7, 10])
    # initialguess = np.array([0,1,1,0.13])
    initialguess = np.array([1, 0.1, 0.03])
    # spread_market = 0.0001 * np.array([12.1, 13.6, 20.0, 24.8, 31.1, 35, 72.9, 121.1])
    spread_market = 0.0001 * np.array([39.3, 40.40, 71.465, 130, 202.25, 265.433, 346.885, 378.250])

    freq = 3
    initial_lambda = 0.03
    kappa = 1
    theta = 0.1
    sigma = 0.03


    mycalibration = CIRLambdaCalibration(trim_start, trim_end)
    myq = mycalibration.getSurvival(initial_lambda, kappa, theta, sigma, 120/12)
    myDL = mycalibration.DefaultLeg(initial_lambda, kappa, theta, sigma, spread_datelist)
    myPL = mycalibration.RiskAnnuity(initial_lambda, kappa, theta, sigma, spread_datelist)
    mysp = mycalibration.getSpread_Model(initial_lambda, initialguess, spread_datelist)
    # myEr = mycalibration.ErrorFunc
    mycal = mycalibration.getCalibratedParameters(initial_lambda, initialguess, spread_datelist, spread_market)
    #mycal = mycalibration.getCalibratedParameters(initialguess)
    #bb = mycalibration.RiskAnnuity(initial_lambda,kappa,theta,sigma,mycalibration.spread_datelist)
    #aa = mycalibration.getSpread_Model(mycalibration.initialguess,mycalibration.spread_datelist)
    #mycalibration.getCalibratedParameters()
    print(mysp)
    print(spread_market)
    # print(myEr.__class__)
    print(mycal)



