import scipy.io as sio
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path
import pandas as pd
xlspath = Path('D:/TYL/Google Drive/Research/All software editing\
/Imscroll-and-Utilities/imscroll/data/20190705.xlsx')
dfs = pd.read_excel(xlspath)
nFiles = dfs.shape[0]
for iFile in range(0, nFiles):

    filestr = dfs.filename[iFile]
    datapath = Path('D:/matlab_CoSMoS/data/')
    intensity_file_path = datapath / (filestr + '_FRETtraces.dat')

    FRET_file = sio.loadmat(intensity_file_path)

    traces = FRET_file['traces']
    donor = traces['donor'][0,0]
    acceptor = traces['acceptor'][0,0]
    total = traces['total'][0,0]
    FRET = traces['FRET'][0,0]
    nAOIs = donor.shape[0]
    nFrames = donor.shape[1]
    frames = np.arange(1,nFrames+1)
    if not os.path.isdir(datapath / filestr):
        os.mkdir(datapath / filestr)
    for iAOI in range(0, nAOIs):


        plt.figure(figsize=(10, 20))

        plt.title('molecule {}'.format(iAOI + 1), fontsize=14)
        plt.xlim((0, nFrames))
        plt.xlabel('frame', fontsize=16)
        plt.ylim((-1000, 5000))
        plt.ylabel('Intensity', fontsize=16)


        plt.subplot(4, 1, 1)
        plt.plot(frames, donor[iAOI, ])

        plt.subplot(4, 1, 2)
        plt.plot(frames, acceptor[iAOI,])

        plt.subplot(4, 1, 3)
        plt.plot(frames, total[iAOI,])

        plt.subplot(4, 1, 4)
        plt.plot(frames, FRET[iAOI,])
        plt.ylim((0,1))


        plt.savefig(datapath / filestr / ('molecule{}.png'.format(iAOI + 1)), Transparent=True,
                    dpi=300, bbox_inches='tight')

        plt.close()

123