import scipy.io as sio
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path
import pandas as pd
import imscrollIO
import xarray as xr
import binding_kinetics

xlspath = Path('/mnt/linuxData/Research/PriA_project/analysis_result/20190907/20190907parameterFile.xlsx')

datestr = '20190907'
sheet = 'L3'
dfs = pd.read_excel(xlspath, sheet_name=sheet)
datapath = imscrollIO.def_data_path()
im_format = 'svg'
nFiles = dfs.shape[0]
filestr = 'L3_01_04'


try:
    all_data, AOI_categories = binding_kinetics.load_all_data(datapath / (filestr + '_all.json'))
except FileNotFoundError:
    print('{} file not found'.format(filestr))

data = all_data['data']
# data = imscrollIO.initialize_data_from_intensity_traces(datapath, filestr)
print(filestr + ' loaded')

if not os.path.isdir(datapath / filestr):
    os.mkdir(datapath / filestr)
AOI_list = [38, 74]

for iAOI in AOI_list:

    iAOI = int(iAOI)
    fig = plt.figure(figsize=(10, 5))

    plt.suptitle('{} {} molecule {}'.format(datestr, filestr, iAOI), fontsize=14)

    plt.xlim((0, data.time.max()))
    plt.xlabel('time', fontsize=16)



    # plt.ylabel('Intensity', fontsize=16)
    channel_list = list(set(data.channel.values.tolist()))
    channel_list.sort()
    for i, i_channel in enumerate(channel_list, 1):

        plt.subplot(len(channel_list), 1, i)
        y = data['intensity'].sel(AOI=iAOI, channel=i_channel)
        vit = data['viterbi_path'].sel(AOI=iAOI, channel=i_channel, state='position')
        plt.plot(y.time,y,
                 color=i_channel
                 )
        plt.plot(vit.time, vit, color='black', linewidth=2)
        if plt.ylim()[0] > 0:
            plt.ylim(bottom=0)
        plt.xlim((0, data.time.max()))

    fig.text(0.04, 0.4, 'Intensity', ha='center', fontsize=16, rotation='vertical')
    plt.xlabel('time (s)', fontsize=16)



    plt.show()

    plt.rcParams['svg.fonttype'] = 'none'
    plt.savefig(datapath / filestr / ('molecule{}.'.format(iAOI)+im_format), Transparent=True,
                dpi=300, bbox_inches='tight', format=im_format)

    plt.close()

123