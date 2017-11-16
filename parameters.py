__author__ = 'marcopereira'
import os
from datetime import date
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKING_DIR = os.path.join(BASE_DIR, 'workspace')
trim_start = date(2005,1,10)
trim_end = date(2006,1,10)
start = date(2005, 3, 30)
referenceDate = date(2005, 3, 30)  # 6 months after trim_start
simNumber = 5
R = 0.4
inArrears = True
freq = '3M'
periods = ['5Y']

# % Vasicek initial guesses
x0Vas = []
x0Vas.append([0.000377701101971, 0.06807420742631265, 0.020205128906558, 0.002073084987793])
x0Vas.append([0.000279919484103, 0.09181159494219767, 0.020199490652279, 0.002074503244439])
x0Vas.append([0.000279098482384, 0.37478438638015319, -0.043475095829618, 0.005391997288885])
x0Vas.append([0.000241182283994, 0.37624139076990623, -0.039701685607549, 0.007109990514207])
x0Vas = pd.DataFrame(x0Vas)

# SDE parameter
# self.kappa = x[0]
# self.theta = x[1]
# self.sigma = x[2]
# self.r0 = x[3]

t_step = 1.0 / 365
xR = [3.0, 0.03, 0.01, 0.03]
rho = 0.5
xQ = [3.0, 0.03, 0.01, 0.03]
Coupon = 0.05
r = 0.04

# CashFlow Dates
QuotesRate = pd.DataFrame([[12.9, 25.5, 40.4, 58, 72, 88.3, 115, 136],
                           [17.6, 20.9, 28.3, 32, 35.8, 40, 44.8, 45.9],
                           [14, 22.75, 29.75, 37.8, 45.5, 57.05, 77, 86.87],
                           [41, 57, 81, 115, 149, 185, 233, 274]
                           ]) * 1E-4

