from pathlib import Path
import pandas as pd
import imscrollIO


def group_imscroll_data_to_xr_json(xlspath, sheet_list):
    datapath = imscrollIO.def_data_path()
    for i_sheet in sheet_list:
        dfs = pd.read_excel(xlspath, sheet_name=i_sheet)

        nFiles = dfs.shape[0]
        for iFile in range(0, nFiles):
            filestr = dfs.filename[iFile]

            data = imscrollIO.initialize_data_from_intensity_traces(datapath, filestr)
            data.attrs['target_channel'] = 'blue'
            data.attrs['binder_channel'] = ['green']
            data = imscrollIO.import_interval_results(data)
            try:
                data = imscrollIO.import_viterbi_paths(data)
            except FileNotFoundError:
                print('error in {}'.format(filestr))
                continue

            imscrollIO.save_data_to_json(datapath / (filestr + '_data.json'), data)


if __name__ == '__main__':
    xlsx_parameter_file_path = imscrollIO.get_xlsx_parameter_file_path()
    sheet_list = imscrollIO.input_sheets_for_analysis()
    group_imscroll_data_to_xr_json(xlsx_parameter_file_path, sheet_list)
