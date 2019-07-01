import scipy.io as sio
import numpy as np

import os
from pathlib import Path
filestr = 'L3_04_02'
datapath = Path('D:/matlab_CoSMoS/data/')
# datapath = Path('D:/TYL/PriA_project/Analysis_Results/20190513/')
interval_file_path = datapath / (filestr + '_interval.dat')
interval_file = sio.loadmat(interval_file_path)
intervals = interval_file['Intervals']

AllTracesCellArray = intervals[0,0]['AllTracesCellArray']
nAOIs = AllTracesCellArray.shape[0]
count = 0
for iAOI in range(0,nAOIs):
    Traces = AllTracesCellArray[iAOI,12][:,0]
    isAllLow = (Traces ==  -2)
    if np.any(np.logical_not(isAllLow)):
        count = count + 1

print(count)
print(nAOIs)




123