import numpy as np
import pandas as pd
import datetime
from Curves.OIS.OIS import OIS
from Calibration.CIR_calibrate import CIRLambdaCalibration
from MonteCarloSimulators.CIR.CIRMCSim import MC_CIR_Sim
from Scheduler.Scheduler import Scheduler
from Products.Credit.CDS import CDS
from parameters import WORKING_DIR
import os

class CDS_exposure(object):

    def __init__(self, Q, start_date, maturity, freq, flavor, recovery=0.4):
        # freq: use mth as unit
        self.start = start_date
        self.maturity = maturity
        self.recovery = recovery
        self.OIS = OIS(start_date, maturity)
        self.Q = Q
        self.freq = freq
        self.flavor = flavor  # 1 or -1
        # self.ntimes = np.shape(self.Q)[0]
        self.ntrajectories = np.shape(self.Q)[1]
        self.freq_num = int(freq[:-1])
        self.datelist = self.getScheduleComplete()[1]
        self.DCF = self.getOIS()
        self.CDS = CDS(self.DCF, Q, start_date, maturity, freq, flavor, recovery=0.4)

    def getOIS(self):
        OIS_DCF_List = []
        for cds_date in self.datelist: OIS_DCF_List.append(self.OIS.getDF_trimstartDate(cds_date))
        OIS_truncation = pd.Series(OIS_DCF_List, index=self.datelist)
        OIS_truncation = OIS_truncation.divide(OIS_truncation.ix[0])
        # add one day since this is header not index
        OIS_truncation = OIS_truncation[self.start + datetime.timedelta(days=1):]
        return OIS_truncation

    def getScheduleComplete(self):
        myscheduler = Scheduler()
        self.datelist = myscheduler.getSchedule(self.start, self.maturity, self.freq, self.start)
        self.ntimes = len(self.datelist)
        fullset = sorted(set(self.datelist).union([self.start]).union([self.maturity]))
        return fullset, self.datelist

    def getExposure(self, Q_path):
        exposure_list = []
        initial_spread = self.CDS.getSingleSpread(Q_path)[0]
        for d in self.datelist:
            CDS_tmp = CDS(self.DCF, self.Q, d, self.maturity, self.freq, self.flavor, self.recovery)
            new_DL = CDS_tmp.getDefaultLeg(Q_path)
            new_RA = CDS_tmp.getRA(Q_path)
            exposure_list.append(new_DL - initial_spread * new_RA)
        exposure_pd = pd.Series(exposure_list, index=self.datelist)
        return exposure_pd

    def getEE(self):
        ee_list = []
        for d in self.datelist:
            tmp = 0
            for i in range(self.ntrajectories):
                tmp += self.getExposure(self.Q[i]).loc[d]
            ee_list.append(tmp / self.ntrajectories)
        ee_pd = pd.DataFrame(ee_list, index=self.datelist, columns=["EE"])
        return ee_pd

    def getEPE(self):
        epe_list = []
        for d in self.datelist:
            tmp = 0
            for i in range(self.ntrajectories):
                tmp += max(self.getExposure(self.Q[i]).loc[d],0)
            epe_list.append(tmp / self.ntrajectories)
        epe_pd = pd.DataFrame(epe_list, index=self.datelist, columns=["EPE"])
        return epe_pd

    def getENE(self):
        ene_list = []
        for d in self.datelist:
            tmp = 0
            for i in range(self.ntrajectories):
                tmp += min(self.getExposure(self.Q[i]).loc[d],0)
            ene_list.append(tmp / self.ntrajectories)
        ene_pd = pd.DataFrame(ene_list, index=self.datelist, columns=["ENE"])
        return ene_pd

    def getPFE(self, significance):
        pfe_list = []
        k = int(significance * self.ntrajectories)
        for d in self.datelist:
            tmp = []
            for i in range(self.ntrajectories):
                tmp.append(self.getExposure(self.Q[i]).loc[d])
            pfe_list.append(sorted(tmp)[k])
        pfe_pd = pd.DataFrame(pfe_list, index=self.datelist,columns=["PFE_"+str(significance)])
        return pfe_pd


    def saveMeExcel(self):
        frames = [self.getEE(),self.getEPE(), self.getENE(), self.getPFE(0.9), self.getPFE(0.1)]
        df = pd.concat(frames,axis=1)
        df.to_excel(os.path.join(WORKING_DIR,'Exposure.xlsx'), sheet_name='exposure', index=True)

    def getCVA(self):
        EPE = self.getEPE()
        DP = []
        D = self.getOIS()
        LGD = 1 - self.recovery
        for d in self.datelist:
            tmp = 0
            for i in range(self.ntrajectories):
                tmp += self.Q[i].loc[d]
            DP.append(tmp / self.ntrajectories)
        DP = pd.DataFrame(DP, index=self.datelist, columns=["DP"])
        tmp2 = 0
        for dd in self.datelist[1:]:
            tmp2 += EPE.loc[dd].values * DP.loc[dd].values * D.loc[dd]
        cva = tmp2 * LGD
        return cva

    def getParspread_single(self, Q_path):
        initial_spread = self.CDS.getSingleSpread(Q_path)[0]
        return initial_spread

    def getParspread_ave(self):
        tmp1 = 0
        tmp2 = 0
        for i in range(self.ntrajectories):
            tmp = self.getParspread_single(self.Q[i])
            tmp1 += tmp
            tmp2 += tmp * tmp
        mean = tmp1 / self.ntrajectories
        sd = (tmp2 / self.ntrajectories - mean * mean) ** 0.5
        return mean, sd



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
    simNumber = 15

    # myois = OIS(trim_start, trim_end)
    # mydcf = myois.getDF_trimstartDate(trim_start)
    mysim = MC_CIR_Sim()
    mysim.setCIR(trim_start, trim_end, initialguess, simNumber, t_step)
    myq = mysim.getSurvival_daily()
    myexposure = CDS_exposure(myq, trim_start, trim_end, "3M", 1, recovery=0.4)
    # aa = myexposure.getExposure(myq[0])
    # ee = myexposure.getEE()
    # epe = myexposure.getEPE()
    # ene = myexposure.getENE()
    # pfe = myexposure.getFPE(0.7)
    # bb = myexposure.saveMeExcel()
    # tt = myexposure.getCVA()
    rr = myexposure.getParspread_single(myq[0])
    yy, zz = myexposure.getParspread_ave()
    print(rr)
    print(yy)
    print(zz)


