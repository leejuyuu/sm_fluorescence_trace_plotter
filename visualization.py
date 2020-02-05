import matplotlib.pyplot as plt
import os
from pathlib import Path
import pandas as pd
import imscrollIO
import binding_kinetics


def main():
    xlspath = Path('D:/TYL/PriA_project/Analysis_Results/20190917/20190917parameterFile.xlsx')
    sheet = 'L3'
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

                iAOI = int(iAOI)
                fig = plt.figure(figsize=(10, 5))

                plt.suptitle('molecule {} ({})'.format(iAOI, key), fontsize=14)

                plt.xlim((0, data.time.max()))
                plt.xlabel('time', fontsize=16)
                # plt.ylabel('Intensity', fontsize=16)
                channel_list = list(set(data.channel.values.tolist()))
                channel_list.sort()
                for i, i_channel in enumerate(channel_list, 1):

                    plt.subplot(len(channel_list), 1, i)
                    y = data['intensity'].sel(AOI=iAOI, channel=i_channel)
                    vit = data['viterbi_path'].sel(AOI=iAOI, channel=i_channel, state='position')
                    plt.plot(y.time, y,
                             color=i_channel
                             )
                    plt.plot(vit.time, vit, color='black', linewidth=2)
                    if plt.ylim()[0] > 0:
                        plt.ylim(bottom=0)
                    plt.xlim((0, data.time.max()))

                fig.text(0.04, 0.4, 'Intensity', ha='center', fontsize=16, rotation='vertical')
                plt.xlabel('time (s)', fontsize=16)
                # plt.show()

                plt.savefig(datapath / filestr / ('molecule{}.'.format(iAOI)+im_format), Transparent=True,
                            dpi=300, bbox_inches='tight', format=im_format)

                plt.close()
    return None


if __name__ == '__main__':
    main()
