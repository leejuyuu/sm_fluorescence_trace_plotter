import numpy as np
from pathlib import Path
import pandas as pd
import imscrollIO
import binding_kinetics
import math
from scipy import optimize
from matplotlib import pyplot as plt


def exclude_inintial_no_binding_aois(intervals):
    not_is_first_interval_0 = intervals.state_number.isel(interval_number=0) != 0
    selected_aois = intervals.AOI[not_is_first_interval_0]
    selected_intevals = intervals.sel(AOI=selected_aois.values)
    return selected_intevals



def main():
    # xlspath = Path('D:/TYL/PriA_project/Analysis_Results/20190917/20190917parameterFile.xlsx')
    xlspath = Path('/mnt/linuxData/Research/PriA_project/analysis_result/20191002/20191002parameterFile.xlsx')

    datapath = imscrollIO.def_data_path()
    # datapath = Path('/mnt/linuxData/Research/PriA_project/analysis_result/20190911/20190911imscroll')
    sheet_list = ['L7']
    specified_n_state = 1
    state_list = ['low', 'high']
    on_off_str = ['on', 'off']
    obs_off_str = ['obs', 'off']
    im_format = 'svg'
    for i_sheet in sheet_list:
        dfs = pd.read_excel(xlspath, sheet_name=i_sheet)
        nFiles = dfs.shape[0]
        interval_list = []
        total_number = 0
        total_cat = {}
        for iFile in range(0, nFiles):
            filestr = dfs.filename[iFile]
            try:
                all_data, AOI_categories = binding_kinetics.load_all_data(datapath / (filestr + '_all.json'))
            except FileNotFoundError:
                print('{} file not found'.format(filestr))
                continue

            print(filestr + ' loaded')

            AOIs_with_binding_event = []
            for key in AOI_categories['analyzable'].keys():
                if key != '0':
                    AOIs_with_binding_event += AOI_categories['analyzable'][key]

            selected_intervals = all_data['intervals'].sel(AOI=AOIs_with_binding_event)
            selected_intervals2 = exclude_inintial_no_binding_aois(selected_intervals)
            number_of_good_traces = 0
            categorizing_good_traces = {}

            for aoi in selected_intervals2.AOI:
                aoi_interval = selected_intervals2.sel(AOI=aoi)
                num_states = int(max(aoi_interval.state_number))
                ar = np.arange(num_states, -1, -1)
                if np.array_equal(aoi_interval.state_number.dropna(dim='interval_number'), ar):
                    number_of_good_traces += 1
                    total_number += 1
                    if num_states not in categorizing_good_traces:
                        categorizing_good_traces[num_states] = 1
                    else:
                        categorizing_good_traces[num_states] += 1
                    if num_states not in total_cat:
                        total_cat[num_states] = 1
                    else:
                        total_cat[num_states] += 1
            print(number_of_good_traces)
            print(categorizing_good_traces)
            print(filestr + ' finished')

        print(total_number)
        print(total_cat)


if __name__ == '__main__':
    main()
