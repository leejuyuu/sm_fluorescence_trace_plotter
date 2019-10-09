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

xlspath = Path('D:/TYL/PriA_project/Analysis_Results/20190917/20190917parameterFile.xlsx')
# xlspath = Path('/mnt/linuxData/Research/PriA_project/analysis_result/20190911/20190911parameterFile.xlsx')

datapath = imscrollIO.def_data_path()
# datapath = Path('/mnt/linuxData/Research/PriA_project/analysis_result/20190911/20190911imscroll')
sheet_list = ['L3']
specified_n_state = 1
state_list = ['low', 'high']
on_off_str = ['on', 'off']
obs_off_str = ['obs', 'off']
im_format = 'svg'
for i_sheet in sheet_list:
    dfs = pd.read_excel(xlspath, sheet_name=i_sheet)
    nFiles = dfs.shape[0]

    interval_list = []


    for iFile in range(0, nFiles):
        filestr = dfs.filename[iFile]

        try:
            all_data, AOI_categories = binding_kinetics.load_all_data(datapath / (filestr + '_all.json'))
        except FileNotFoundError:
            print('{} file not found'.format(filestr))
            continue

        print(filestr + ' loaded')
        if str(specified_n_state) in AOI_categories['analyzable']:

            interval_list.append(all_data['intervals'].sel(AOI=AOI_categories['analyzable'][str(specified_n_state)]))

    max_time = all_data['data'].time.values.max()
    for i, item in enumerate(state_list):
        dwells = binding_kinetics.extract_dwell_time(interval_list, 0, i)
        if len(dwells) == 0:
            print('no {} state found'.format(item))
            continue
        max_dwell = dwells.max()

        bin_width = 10
        n_bins = math.floor(max_dwell / bin_width) + 1
        n_edge = n_bins + 1
        prob_den, edges = np.histogram(dwells, bins=range(0, n_edge * bin_width, bin_width), density=True)
        centers = (edges[0:-1] + edges[1:]) / 2

        mean_dwell = dwells.mean()
        params, params_covariance = optimize.curve_fit(single_exponential,
                                                       centers, prob_den,
                                                       p0=[1 / np.mean(dwells)])

        fit_x = np.arange(centers[0], centers[-1], 1)
        fit_y = single_exponential(fit_x, params)
        plt.plot(fit_x, fit_y, color='red')
        # plt.show()
        plt.bar(centers, prob_den, width=bin_width)
        plt.xlabel(r'$\tau_{{{}}}$ (s)'.format(on_off_str[i]), fontsize=16)
        plt.ylabel('probability density (s$^{-1}$)', fontsize=16)
        k_str = r'$k_{{{}}}$ = {:.5f} s$^{{-1}}$'.format(obs_off_str[i], params[0])
        ax = plt.gca()
        plt.text(0.55, 0.8, k_str, transform=ax.transAxes, fontsize=14)
        plt.xlim((0, max_time))

        # root = Tk()
        # save_fig_path = filedialog.asksaveasfilename()
        # root.destroy()
        save_fig_path = datapath / (i_sheet+'_'+ item + '_dwell' + '.' + im_format)
        # plt.show()
        plt.savefig(save_fig_path, format=im_format, Transparent=True,
                    dpi=300, bbox_inches='tight')
        plt.close()



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