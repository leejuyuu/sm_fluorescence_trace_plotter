#  Copyright (C) 2020 Tzu-Yu Lee, National Taiwan University
#
#  This file (visualization.py) is part of python_for_imscroll.
#
#  python_for_imscroll is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  python_for_imscroll is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with python_for_imscroll.  If not, see <https://www.gnu.org/licenses/>.

"""Visualization module handles single-molecule fluorescence data visualization"""

import matplotlib.pyplot as plt
import os
from pathlib import Path
import pandas as pd
import imscrollIO
import binding_kinetics
import xarray as xr


def plot_one_trace_and_save(molecule_data: xr.Dataset, category: str = '',
                            save_dir: Path = Path(), save_format: str = 'svg'):
    """Take dataset of one molecule and plot time trajectory.

    Each subplot corresponds to one channel (color).
    Input:
        molecule_data: Dataset of a certain molecule, should contain time and
        channel coordinates, with 'intensity' and 'viterbi_path' variables.

        category: The category of that trace.
        save_dir: The directory to save the image.
        save_format: The image file format to save.
    """
    molecule_number = int(molecule_data.AOI)
    fig = plt.figure(figsize=(10, 5))
    plt.suptitle('molecule {} ({})'.format(molecule_number, category), fontsize=14)
    channel_list = list(set(molecule_data.channel.values.tolist()))
    channel_list.sort()
    for i, i_channel in enumerate(channel_list, 1):
        plt.subplot(len(channel_list), 1, i)
        y = molecule_data['intensity'].sel(channel=i_channel)
        vit = molecule_data['viterbi_path'].sel(channel=i_channel, state='position')
        plt.plot(y.time, y, color=i_channel)
        plt.plot(vit.time, vit, color='black', linewidth=2)
        if plt.ylim()[0] > 0:
            plt.ylim(bottom=0)
        plt.xlim((0, molecule_data.time.max()))

    fig.text(0.04, 0.4, 'Intensity', ha='center', fontsize=16, rotation='vertical')
    plt.xlabel('time (s)', fontsize=16)
    plt.rcParams['svg.fonttype'] = 'none'
    plt.savefig(save_dir / ('molecule{}.{}'.format(molecule_number, save_format)),
                Transparent=True, dpi=300, bbox_inches='tight', format=save_format)
    plt.close()
    return None


def main():
    """Plot traces from every molecule in the dataset and save them as png files."""
    xlspath = Path('/run/media/tzu-yu/linuxData/Research/PriA_project/analysis_result/20191106//20191106parameterFile.xlsx')
    sheet = 'L1_03'
    dfs = pd.read_excel(xlspath, sheet_name=sheet)
    datapath = imscrollIO.def_data_path()
    im_format = 'svg'
    nFiles = dfs.shape[0]
    for iFile in range(0, nFiles):
        filestr = dfs.filename[iFile]

        try:
            all_data, AOI_categories = binding_kinetics.load_all_data(datapath / (filestr + '_all.json'))
        except FileNotFoundError:
            print('{} file not found'.format(filestr))
            continue
        data = all_data['data']
        print(filestr + ' loaded')
        save_dir = datapath / filestr
        if not save_dir.is_dir():
            save_dir.mkdir()
        AOI_dict = dict(AOI_categories)
        for key, value in AOI_categories.items():
            if key == 'analyzable':
                del AOI_dict[key]
                for key2, value2 in AOI_categories[key].items():
                    AOI_dict[key2] = value2

        for key, AOI_list in AOI_dict.items():
            for iAOI in AOI_list:
                molecule_data = data.sel(AOI=iAOI)
                plot_one_trace_and_save(molecule_data, key,
                                        save_dir=(datapath / filestr), save_format=im_format)
    return None


if __name__ == '__main__':
    main()
