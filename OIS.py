import numpy as np
import pandas as pd
import quandl
import pickle, os
from Scheduler.Scheduler import Scheduler
from datetime import date
from parameters import WORKING_DIR, x0Vas, t_step, simNumber, trim_start, trim_end, freq, referenceDate
QUANDL_API_KEY = "J_3ufFECZVffPxNDZuWf"
FRED_API_KEY = "90746840bcdc4851bf3ad921ded8a212"

# Class OIS
class OIS(object):
    def __init__(self, trim_start, trim_end):
        self.OIS = 0.01 * quandl.get("USTREASURY/YIELD", authtoken=QUANDL_API_KEY, trim_start=trim_start, trim_end=trim_end)
        self.OIS.reset_index(level=0, inplace=True)
        self.startdate = trim_start
        self.datesAll = pd.DataFrame(pd.date_range(trim_start, trim_end), columns=['DATE'])
        self.OIS.columns = [x.upper() for x in self.OIS.columns]
        self.OIS = pd.merge(left=self.datesAll, right=self.OIS, how='left')
        self.OIS = self.OIS.fillna(method='ffill').fillna(method='bfill')
        self.OIS = self.OIS.T.fillna(method='ffill').fillna(method='bfill').T
        self.OIS.index = self.datesAll.DATE

    def getOIS(self, datelist=[]):
        if (len(datelist) != 0):
            return self.OIS.loc[datelist]
        else:
            return self.OIS

    # up to 120 months
    # tenor_list can be a single integer or a list of integers
    def getOISInterpMonthly(self, tenor_list=[]):
        self.OIS_copy = self.OIS.copy()
        del self.OIS_copy["DATE"]
        # del self.OIS_copy["10 YR"]
        del self.OIS_copy["20 YR"]
        del self.OIS_copy["30 YR"]
        # del self.OIS_copy["7 YR"]
        # del self.OIS_copy["5 YR"]
        # del self.OIS_copy["3 YR"]
        self.OIS_copy.columns = (1, 3, 6, 12, 24, 36, 60, 84, 120)
        deltaTenor = self.OIS_copy.columns[1:] - self.OIS_copy.columns[:-1]

        for i in range(len(self.OIS_copy.columns) - 1):
            for j in range(deltaTenor[i] - 1):
                diff_rate = self.OIS_copy[self.OIS_copy.columns[i + 1]] - self.OIS_copy[self.OIS_copy.columns[i]]
                diff_mth1 = self.OIS_copy.columns[i + 1] - self.OIS_copy.columns[i]
                delta_rate = diff_rate / diff_mth1
                diff_mth2 = j + 1
                self.OIS_copy[self.OIS_copy.columns[i]+j+1] = self.OIS_copy[self.OIS_copy.columns[i]] + delta_rate * diff_mth2

        self.OIS_copy[self.OIS_copy.columns] = self.OIS_copy[sorted(self.OIS_copy.columns)]
        self.OIS_copy.columns = sorted(self.OIS_copy.columns)
        if tenor_list != []: return self.OIS_copy[tenor_list]
        else: return self.OIS_copy

    def getDiscountFactor(self, tenor_list=[]):
        rates_mth = self.getOISInterpMonthly(tenor_list)
        OIS_tmp = pd.DataFrame.as_matrix(rates_mth)
        OIS_tmp = OIS_tmp.astype(float)
        discount = np.exp(-OIS_tmp)
        self.discount = pd.DataFrame(data=discount, index=rates_mth.index)
        self.discount.columns = rates_mth.columns
        return self.discount

    def getDF_trimstartDate(self, ref_date):
        trim_start = self.startdate
        delta_days = (ref_date - trim_start).days / 30
        ceiling = int(delta_days) + 1
        floor = int(delta_days)
        delta_days_small = (ref_date - trim_start).days - floor * 30
        monthly_DF = self.getDiscountFactor()
        DF_trim_start = monthly_DF.loc[trim_start]
        if floor == 0: DF_ref = (DF_trim_start[ceiling] - 1) / 30 * delta_days_small + 1
        else: DF_ref = (DF_trim_start[ceiling] - DF_trim_start[floor])/30 * delta_days_small + DF_trim_start[floor]
        return DF_ref


if(__name__ == "__main__"):
    import quandl
    from datetime import date
    import pandas as pd
    import numpy as np

    trim_start, trim_end = date(2005,1,10), date(2010,1,10)
    start, referenceDate = date(2005,3,30), date(2005,1,12)

    myois = OIS(trim_start, trim_end)

    aa = myois.getDiscountFactor()
    bb = aa.loc[trim_start]
    cc = bb[60]
    dd = myois.getDF_trimstartDate(referenceDate)
    #print(myois.OIS)
    print(dd)
    print(dd.__class__)

