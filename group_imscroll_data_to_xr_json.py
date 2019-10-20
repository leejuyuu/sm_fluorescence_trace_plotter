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
    while True:
        xlsx_parameter_file_path = imscrollIO.qt_getfile()
        print(xlsx_parameter_file_path)
        yes_no = input('Confirm [y/n]: ')
        if yes_no == 'y':
            xlsx_parameter_file_path = Path(xlsx_parameter_file_path)
            break
    while True:
        input_str = input('Enter the sheets to be analyzed: ')
        sheet_list_out = input_str.split(', ')
        print(sheet_list_out)
        yes_no2 = input('Confirm [y/n]: ')
        if yes_no2 == 'y':
            break
    group_imscroll_data_to_xr_json(xlsx_parameter_file_path, sheet_list_out)
