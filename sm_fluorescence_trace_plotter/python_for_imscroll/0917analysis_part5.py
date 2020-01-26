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



# xlspath = Path('D:/TYL/PriA_project/Analysis_Results/20190911/20190911parameterFile.xlsx')
xlspath = Path('/mnt/linuxData/Research/PriA_project/analysis_result/20190917/20190917parameterFile.xlsx')
datapath = Path('/mnt/linuxData/Research/PriA_project/analysis_result/20190917/20190917imscroll')
sheets = ['L1', 'L2', 'L3', 'L4']
out = dict()
for i_sheet in sheets:
    dfs = pd.read_excel(xlspath, sheet_name=i_sheet)
    # datapath = imscrollIO.def_data_path()

    nFiles = dfs.shape[0]
    specified_n_state = 1
    state_list = ['low', 'high']
    interval_list = []

    fraction_list = []
    for iFile in range(0, nFiles):
        filestr = dfs.filename[iFile]

        try:
            all_data, AOI_categories = binding_kinetics.load_all_data(datapath / (filestr + '_all.json'))
        except FileNotFoundError:
            print('{} file not found'.format(filestr))
            continue

        print(filestr + ' loaded')
        good_aoi_set = set()
        for item in AOI_categories['analyzable'].values():
            good_aoi_set.update(item)
        good_aoi_list = list(good_aoi_set)
        channel_data = all_data['data'].sel(channel='green', AOI=good_aoi_list)
        channel_state_info = binding_kinetics.collect_channel_state_info(channel_data)

        channel_data = channel_data.merge(channel_state_info)
        for iAOI in channel_data.AOI:
            channel_data['viterbi_path'].loc[dict(AOI=iAOI)] = \
                binding_kinetics.shift_state_number(channel_data.loc[dict(AOI=iAOI)])['viterbi_path']
        channel_viterbi_path_label = channel_data['viterbi_path'].sel(state='label')
        fraction = np.count_nonzero(channel_viterbi_path_label)/channel_viterbi_path_label.size
        fraction_list.append(fraction)

    out[i_sheet] = fraction_list[:]
    print(fraction_list)
    
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