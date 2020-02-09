
import pandas as pd
import imscrollIO
import binding_kinetics as bk
from pathlib import Path


def categorize_binding_traces(parameter_file_path, sheet_list):
    datapath = imscrollIO.def_data_path()
    # datapath = Path('/mnt/linuxData/Research/PriA_project/analysis_result/20190911/20190911imscroll')

    for i_sheet in sheet_list:
        dfs = pd.read_excel(parameter_file_path, sheet_name=i_sheet)
        nFiles = dfs.shape[0]
        for iFile in range(0, nFiles):
            filestr = dfs.filename[iFile]
            AOI_categories = {}

            try:
                data = imscrollIO.load_data_from_json(datapath / (filestr + '_data.json'))
            except FileNotFoundError:
                continue

            state_info = bk.collect_all_channel_state_info(data)
            bad_tethers = bk.list_multiple_tethers(state_info.sel(channel=data.target_channel))
            AOI_categories['multiple_tethers'] = bad_tethers
            remaining_aois = list(set(data.AOI.values) - set(bad_tethers))
            selected_data = data.sel(AOI=remaining_aois)
            protein_channel_data = bk.get_channel_data(selected_data, data.binder_channel[0])
            non_colocalized_aois, intervals = bk.colocalization_analysis(protein_channel_data)
            AOI_categories['false_binding'] = non_colocalized_aois
            analyzable_aois = list(set(remaining_aois) - set(non_colocalized_aois))
            good_intervals = intervals.sel(AOI=analyzable_aois)
            AOI_categories['analyzable'] = \
                bk.group_analyzable_aois_into_state_number(good_intervals)
            all_data = {'data': data,
                        'intervals': intervals,
                        'state_info': state_info}
            bk.save_all_data(all_data, AOI_categories, datapath / (filestr + '_all.json'))

            print(filestr + ' finished')
    return None


if __name__ == '__main__':
    xlsx_parameter_file_path = imscrollIO.get_xlsx_parameter_file_path()
    sheet_list = imscrollIO.input_sheets_for_analysis()
    categorize_binding_traces(xlsx_parameter_file_path, sheet_list)
