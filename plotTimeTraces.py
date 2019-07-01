import scipy.io as sio
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path
filestr = 'L3_04_02'
datapath = Path('D:/matlab_CoSMoS/data/')
intensity_file_path = datapath / (filestr +'_intcorrected.dat')
interval_file_path = datapath / (filestr + '_interval.dat')

intensity_file = sio.loadmat(intensity_file_path)
interval_file = sio.loadmat(interval_file_path)
aoifits = intensity_file['aoifits']
intervals = interval_file['Intervals']
aoifits_data = aoifits[0,0]['data']
nAOI = int(np.amax(aoifits_data[:,0]))
nFrame = int(np.amax(aoifits_data[:,1]))
intensity_table = aoifits_data[:,7].reshape((nFrame,nAOI))
os.mkdir(datapath / filestr)
for i in range(0,nAOI):
    Traces = intervals[0,0]['AllTracesCellArray'][i,12][:,0]
    frames = intervals[0,0]['AllTracesCellArray'][i,12][:,1]
    isHighEvent = (Traces % 2 != 0)
    t1 = frames[isHighEvent]
    I1 = intensity_table[:,i][isHighEvent]
    t2 = frames[np.logical_not(isHighEvent)]
    I2 = intensity_table[:,i][np.logical_not(isHighEvent)]
    plt.figure(figsize=(10,5))
    plt.scatter(t1,I1,color='green', s=2)
    plt.scatter(t2,I2,color='black',s=2)
    plt.title('molecule {}'.format(i+1),fontsize=14)
    plt.xlim((0,nFrame))
    plt.xlabel('frame',fontsize=16)
    plt.ylim((intensity_table.min()-1000,intensity_table.max()+3000))
    plt.ylabel('Intensity',fontsize=16)
    plt.savefig(datapath / filestr / ('molecule{}.png'.format(i+1)),Transparent = True , dpi = 300,bbox_inches='tight')
    plt.close()

123