import matplotlib.pyplot as plt
import os
from pathlib import Path
import pandas as pd
from sm_fluorescence_trace_plotter.python_for_imscroll import imscrollIO
from sm_fluorescence_trace_plotter.python_for_imscroll import binding_kinetics
import xarray as xr


def plot_one_trace_and_save(molecule_data: xr.Dataset, category: str = '',
                            save_dir: Path = Path(), save_format: str = 'svg'):
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

        if not os.path.isdir(datapath / filestr):
            os.mkdir(datapath / filestr)
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
