from typing import List
from pathlib import Path
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from lifelines import KaplanMeierFitter, ExponentialFitter
from python_for_imscroll import imscrollIO
from python_for_imscroll import binding_kinetics


def find_two_state_dwell_time(parameter_file_path: Path, sheet_list: List[str]):
    datapath = imscrollIO.def_data_path()
    specified_n_state = 1
    state_list = ['low', 'high']
    on_off_str = ['on', 'off']
    obs_off_str = ['obs', 'off']
    im_format = 'svg'
    for i_sheet in sheet_list:
        dfs = pd.read_excel(parameter_file_path, sheet_name=i_sheet)
        nFiles = dfs.shape[0]
        interval_list = []
        n_good_traces = 0
        for iFile in range(0, nFiles):
            filestr = dfs.filename[iFile]
            try:
                all_data, AOI_categories = binding_kinetics.load_all_data(datapath
                                                                          / (filestr + '_all.json'))
            except FileNotFoundError:
                print('{} file not found'.format(filestr))
                continue

            print(filestr + ' loaded')
            if str(specified_n_state) in AOI_categories['analyzable']:

                interval_list.append(all_data['intervals'].sel(AOI=AOI_categories['analyzable'][str(specified_n_state)]))
            n_good_traces += len(AOI_categories['analyzable']['1'])
        max_time = all_data['data'].time.values.max()
        for i, item in enumerate(state_list):
            dwells = binding_kinetics.extract_dwell_time(interval_list, i)
            if len(dwells.duration) == 0:
                print('no {} state found'.format(item))
                continue
            kmf = KaplanMeierFitter()
            exf = ExponentialFitter()
            kmf.fit(dwells.duration, dwells.event_observed)
            exf.fit(dwells.duration, dwells.event_observed)

            ax = kmf.plot()
            exf.plot_survival_function(ax=ax, ci_show=False)
            ax.get_legend().remove()

            plt.xlabel(r'$\tau_{{{}}}$ (s)'.format(on_off_str[i]), fontsize=16)
            plt.ylabel('probability', fontsize=16)
            k_str = r'$k_{{{}}}$ = {:.1f} s'.format(obs_off_str[i], exf.lambda_)

            n_event = np.count_nonzero(dwells.event_observed)
            n_censored = len(dwells.event_observed) - n_event
            string = '{}, {}, {}'.format(n_event, n_censored, n_good_traces)
            plt.text(0.6, 0.8, k_str, transform=ax.transAxes, fontsize=14)
            plt.text(0.6, 0.6, string, transform=ax.transAxes, fontsize=14)
            plt.xlim((0, max_time))

            save_fig_path = datapath / (i_sheet+'_' + item + '_dwell' + '.' + im_format)
            # plt.show()
            plt.rcParams['svg.fonttype'] = 'none'
            plt.savefig(save_fig_path, format=im_format, Transparent=True,
                        dpi=300, bbox_inches='tight')
            plt.close()


def main():
    """main function"""
    xlsx_parameter_file_path = imscrollIO.get_xlsx_parameter_file_path()
    sheet_list = imscrollIO.input_sheets_for_analysis()
    find_two_state_dwell_time(xlsx_parameter_file_path, sheet_list)


if __name__ == '__main__':
    main()
