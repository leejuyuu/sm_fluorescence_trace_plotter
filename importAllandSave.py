import imscrollIO
from pathlib import Path
import pandas as pd

xlspath = Path('D:/TYL/PriA_project/Analysis_Results/20190907/20190907parameterFile.xlsx')
datapath = imscrollIO.def_data_path()
dfs = pd.read_excel(xlspath)
nFiles = dfs.shape[0]
for iFile in range(0, nFiles):
    filestr = dfs.filename[iFile]

    data = imscrollIO.initialize_data_from_intensity_traces(datapath, filestr)
    data = imscrollIO.import_interval_results(data)
    data = imscrollIO.import_time_stamps(data)

    data = imscrollIO.import_viterbi_paths(data)

    imscrollIO.save_data_to_netcdf(datapath / (filestr + '_data.nc'), data)
    print(filestr)
