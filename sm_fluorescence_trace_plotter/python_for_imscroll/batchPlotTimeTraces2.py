import scipy.io as sio
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path
import pandas as pd
xlspath = Path('D:/TYL/PriA_project/Analysis_Results/20190718/20190718parameterFile.xlsx')
dfs = pd.read_excel(xlspath)
nFiles = dfs.shape[0]
for iFile in range(0, nFiles):

    filestr = dfs.filename[iFile]
    datapath = Path('D:/matlab_CoSMoS/data/')
    intensity_file_path = datapath / (filestr + '_traces.dat')

    FRET_file = sio.loadmat(intensity_file_path)

    traces = FRET_file['traces']
    green = traces['green'][0, 0]
    red = traces['red'][0, 0]
    nAOIs = green.shape[0]
    nFrames = green.shape[1]

    interval_file_path = datapath / (filestr + '_interval.dat')
    interval_file = sio.loadmat(interval_file_path)
    intervals = interval_file['IntervalDataStructure']


    frames = np.arange(1,nFrames+1)
    if not os.path.isdir(datapath / filestr):
        os.mkdir(datapath / filestr)
    for iAOI in range(0, nAOIs):

        plt.figure(figsize=(10, 5))

        plt.suptitle('molecule {}'.format(iAOI + 1), fontsize=14)
        plt.xlim((0, nFrames))
        plt.xlabel('frame', fontsize=16)
        plt.ylim((-1000, 5000))
        plt.ylabel('Intensity', fontsize=16)


        plt.subplot(2, 1, 1)
        plt.plot(frames, red[iAOI,])
        plt.xlim((0, nFrames))

        plt.subplot(2, 1, 2)

        intervalTraces = intervals[0, 0]['AllTracesCellArray'][iAOI, 0][:, 0]

        isHighEvent = (intervalTraces % 2 != 0)
        t1 = frames[isHighEvent]
        I1 = green[iAOI,][isHighEvent]
        t2 = frames[np.logical_not(isHighEvent)]
        I2 = green[iAOI,][np.logical_not(isHighEvent)]

        plt.scatter(t1, I1, color='green', s=2)
        plt.scatter(t2, I2, color='black', s=2)

        plt.xlim((0, nFrames))
        plt.xlabel('frame', fontsize=16)
        plt.ylim((green.min() - 1000, 15000))
        plt.ylabel('Intensity', fontsize=16)
        #plt.show()




        plt.savefig(datapath / filestr / ('molecule{}.png'.format(iAOI + 1)), Transparent=True,
                    dpi=300, bbox_inches='tight')

        plt.close()

123