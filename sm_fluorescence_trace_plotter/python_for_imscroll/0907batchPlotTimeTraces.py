import scipy.io as sio
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path
import pandas as pd
import imscrollIO
import xarray as xr
xlspath = Path('D:/TYL/PriA_project/Analysis_Results/20190907/20190907parameterFile.xlsx')
dfs = pd.read_excel(xlspath)
datapath = imscrollIO.def_data_path()
nFiles = dfs.shape[0]
for iFile in range(0, nFiles):
    filestr = dfs.filename[iFile]

    data = imscrollIO.initialize_data_from_intensity_traces(datapath, filestr)
    nAOIs = len(data.AOI)


    if not os.path.isdir(datapath / filestr):
        os.mkdir(datapath / filestr)
    for iAOI in data.AOI:

        plt.figure(figsize=(10, 5))

        plt.suptitle('molecule {}'.format(iAOI.values), fontsize=14)
        plt.xlim((0, data.time.max()))
        plt.xlabel('time', fontsize=16)

        plt.ylabel('Intensity', fontsize=16)
        for i, i_channel in enumerate(data.channel.values, 1):

            plt.subplot(3, 1, i)
            y = data['intensity'].sel(AOI=iAOI, channel=i_channel)
            bool_nan = xr.ufuncs.logical_not(xr.ufuncs.isnan(y))
            plt.plot(data.time.where(bool_nan, drop=True),
                     y.where(bool_nan, drop=True),
                     color=i_channel
                     )
            plt.xlim((0, data.time.max()))



        plt.xlabel('time (s)', fontsize=16)

        plt.ylabel('Intensity', fontsize=16)
        # plt.show()




        plt.savefig(datapath / filestr / ('molecule{}.png'.format(iAOI.values)), Transparent=True,
                    dpi=300, bbox_inches='tight')

        plt.close()

123