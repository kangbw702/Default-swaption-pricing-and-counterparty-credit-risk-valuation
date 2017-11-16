import numpy as np
import pandas as pd
import datetime
from MonteCarloSimulators.CIR.CIRMCSim import MC_CIR_Sim
from Scheduler.Scheduler import Scheduler
from Products.Credit.CDS import CDS
from Curves.OIS.OIS import OIS

#Monte Carlo Simulation Pricer for Credit Default Swaption

class CDSSwaption(object):

    def __init__(self, option_start, cds_start,cds_end,strike,cds_freq,cds_flavor,cds_recovery,Q):
        self.option_start = option_start
        self.strike = strike
        self.cds_start = cds_start
        self.cds_end = cds_end
        self.cds_freq = cds_freq
        # payer to pay strike K, spread - k; receiver to receive strike K, k - spread
        self.cds_flavor = cds_flavor
        self.cds_recovery = cds_recovery
        self.myScheduler = Scheduler()
        self.cds_datelist = self.myScheduler.getSchedule(self.cds_start,self.cds_end,self.cds_freq,self.cds_start)
        self.OIS = OIS(option_start,cds_end)
        self.Q = Q
        self.ntimes = np.shape(self.Q)[0]
        self.ntrajectories = np.shape(self.Q)[1]

    def getCDSSwaption(self,premium_rate):
        Q_truncation = self.Q[self.cds_start:]
        Q_truncation = Q_truncation.divide(Q_truncation.ix[0])
        OIS_DCF_List = []
        for cds_date in self.cds_datelist: OIS_DCF_List.append(self.OIS.getDF_trimstartDate(cds_date))
        OIS_truncation = pd.Series(OIS_DCF_List,index=self.cds_datelist)
        OIS_truncation = OIS_truncation.divide(OIS_truncation.ix[0])
        # add one day since this is header not index
        OIS_truncation = OIS_truncation[self.cds_start+datetime.timedelta(days=1):]
        self.CDS = CDS(OIS_truncation, Q_truncation, self.cds_start, self.cds_end, self.cds_freq, self.cds_flavor, self.cds_recovery)

        total_instance = 0
        for i in range(self.ntrajectories):
            cur_default = self.Q.loc[self.cds_start][i]
            cur_discount = self.OIS.getDF_trimstartDate(self.cds_start)
            cur_spread, cur_ra = self.CDS.getSingleSpread(self.CDS.Q[i])
            if self.cds_flavor: total_instance += cur_discount * cur_default * max(cur_spread-premium_rate,0) * cur_ra
            else: total_instance += cur_discount * cur_default * max(-cur_spread + premium_rate,0) * cur_ra

        return total_instance / self.ntrajectories



if(__name__ == "__main__"):
    import numpy as np
    import pandas as pd
    from datetime import datetime, timedelta
    from MonteCarloSimulators.CIR.CIRMCSim import MC_CIR_Sim
    from Scheduler.Scheduler import Scheduler
    from Products.Credit.CDS import CDS
    from Curves.OIS.OIS import OIS
    import numpy as np
    import datetime
    from Curves.OIS.OIS import OIS
    from MonteCarloSimulators.CIR.CIRMCSim import MC_CIR_Sim

    option_start = datetime.date(2005,1,10)
    trim_start = datetime.date(2006, 1, 10)
    trim_end = datetime.date(2010, 1, 10)
    recovery = 0.4
    initialguess = np.array([0.003, 0.1, 0.05, 0.13])
    t_step = 1.0 / 365
    simNumber = 5

    mysim = MC_CIR_Sim()
    mysim.setCIR(option_start, trim_end, initialguess, simNumber, t_step)
    myq, myhazard = mysim.getSurvival_daily()
    #mycds = CDS(option_start, trim_end, "3M", myq, 1, recovery=0.4)
    #mycdsvalue = mycds.getCDSValue(0)
    myswaption = CDSSwaption(option_start, trim_start,trim_end,0,"3M",1,0.4,myq)
    tt = myswaption.getCDSSwaption(0)
    # print(mycds.datelist[0].__class__)

    print(tt)