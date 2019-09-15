import scipy.io as sio
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path
import pandas as pd
import imscrollIO
import xarray as xr
import binding_kinetics
import math
from scipy import optimize
from matplotlib import pyplot as plt
from tkinter import Tk, filedialog


def single_exponential(x, a):
    return a * np.exp(-a * x)

# xlspath = Path('D:/TYL/PriA_project/Analysis_Results/20190911/20190911parameterFile.xlsx')
xlspath = Path('/mnt/linuxData/Research/PriA_project/analysis_result/20190911/20190911parameterFile.xlsx')
dfs = pd.read_excel(xlspath)
# datapath = imscrollIO.def_data_path()
datapath = Path('/mnt/linuxData/Research/PriA_project/analysis_result/20190911/20190911imscroll')
nFiles = dfs.shape[0]
specified_n_state = 1
state_list = ['low', 'high']
interval_list = []


for iFile in range(0, nFiles):
    filestr = dfs.filename[iFile]

    try:
        all_data, AOI_categories = binding_kinetics.load_all_data(datapath / (filestr + '_all.json'))
    except FileNotFoundError:
        print('{} file not found'.format(filestr))
        continue

    print(filestr + ' loaded')
    AOI_dict = dict(AOI_categories)
    for key, value in AOI_categories.items():
        if key == 'analyzable':
            del AOI_dict[key]
            for key2, value2 in AOI_categories[key].items():
                AOI_dict[key2] = len(value2)
        else:
            AOI_dict[key] = len(value)
    print(AOI_dict)
    input('press enter to continue')




123
    
    #
    # nAOIs = len(data.AOI)
    #
    #
    # if not os.path.isdir(datapath / filestr):
    #     os.mkdir(datapath / filestr)
    # for iAOI in data.AOI:
    #
    #     plt.figure(figsize=(10, 5))
    #
    #     plt.suptitle('molecule {}'.format(iAOI.values), fontsize=14)
    #     plt.xlim((0, data.time.max()))
    #     plt.xlabel('time', fontsize=16)
    #
    #     plt.ylabel('Intensity', fontsize=16)
    #     for i, i_channel in enumerate(data.channel.values, 1):
    #
    #         plt.subplot(3, 1, i)
    #         y = data['intensity'].sel(AOI=iAOI, channel=i_channel)
    #         bool_nan = xr.ufuncs.logical_not(xr.ufuncs.isnan(y))
    #         plt.plot(data.time.where(bool_nan, drop=True),
    #                  y.where(bool_nan, drop=True),
    #                  color=i_channel
    #                  )
    #         plt.xlim((0, data.time.max()))
    #
    #
    #
    #     plt.xlabel('time (s)', fontsize=16)
    #
    #     plt.ylabel('Intensity', fontsize=16)
    #     # plt.show()
    #
    #
    #
    #
    #     plt.savefig(datapath / filestr / ('molecule{}.png'.format(iAOI.values)), Transparent=True,
    #                 dpi=300, bbox_inches='tight')
    #
    #     plt.close()

123