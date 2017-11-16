import numpy as np
import datetime
from Curves.OIS.OIS import OIS
from Calibration.CIR_calibrate import CIRLambdaCalibration
from MonteCarloSimulators.CIR.CIRMCSim import MC_CIR_Sim
from Scheduler.Scheduler import Scheduler

class CDS(object):

    def __init__(self, OIS, Q, start_date, maturity, freq, flavor, recovery=0.4):
        # freq: use mth as unit
        self.start = start_date
        self.maturity = maturity
        self.recovery = recovery
        self.OIS = OIS
        self.Q = Q
        self.freq = freq
        self.flavor = flavor  # 1 or -1
        self.ntimes = np.shape(self.Q)[0]
        self.ntrajectories = np.shape(self.Q)[1]
        self.freq_num = int(freq[:-1])
        self.datelist = self.getScheduleComplete()[1]

    def getScheduleComplete(self):
        myscheduler = Scheduler()
        self.datelist = myscheduler.getSchedule(self.start, self.maturity, self.freq, self.start)
        self.ntimes = len(self.datelist)
        fullset = sorted(set(self.datelist).union([self.start]).union([self.maturity]))
        return fullset, self.datelist

    def getDefaultLeg(self, Q_path):
        DL = 0
        for i in range(len(self.datelist)-1):
            Qstart = Q_path.loc[self.datelist[i]]
            Qend = Q_path.loc[self.datelist[i+1]]
            DCF_paydate = self.OIS.loc[(self.datelist[i+1])] # add 1 more since the first date in this list including the start time
            DL += (1 - self.recovery) * DCF_paydate * (Qstart - Qend)
        return DL

    def getRA(self, Q_path):
        RA = 0
        for i in range(len(self.datelist) - 1):
            Qstart = Q_path.loc[self.datelist[i]]
            Qend = Q_path.loc[self.datelist[i+1]]
            DCF_paydate = self.OIS.loc[(self.datelist[i+1])] # add 1 more since the first date in this list including the start time
            RA += 0.5 * DCF_paydate * (Qstart + Qend) * (self.freq_num / 12)
        return RA

    def getSingleSpread(self, Q_path):
        dl = self.getDefaultLeg(Q_path)
        ra = self.getRA(Q_path)
        return dl / ra, ra

    def getCDSValue(self, premium_rate):
        total_instance = 0
        for i in range(self.ntrajectories):
            cur_spread, cur_ra = self.getSingleSpread(self.Q[i])
            total_instance += (cur_spread - premium_rate) * cur_ra * self.flavor
        return total_instance / self.ntrajectories




if(__name__ == "__main__"):
    import numpy as np
    import datetime
    from Curves.OIS.OIS import OIS
    from MonteCarloSimulators.CIR.CIRMCSim import MC_CIR_Sim

    trim_start = datetime.date(2005, 1, 10)
    trim_end = datetime.date(2010, 1, 10)
    recovery = 0.4
    initialguess = np.array([0.003, 0.1, 0.05, 0.13])
    t_step = 1.0 / 365
    simNumber = 5

    myois = OIS(trim_start, trim_end)
    mydcf = myois.getDiscountFactor()[1]
    mysim = MC_CIR_Sim()
    mysim.setCIR(trim_start, trim_end, initialguess, simNumber, t_step)
    myq = mysim.getSurvival_daily()[0]
    # mycds = CDS(myois, myq, trim_start, trim_end, "3M" , 1, recovery=0.4)
    # mycdsvalue = mycds.getCDSValue(0)
    print(mydcf)
    print(mydcf.loc[trim_start])
    # print(mycdsvalue)

