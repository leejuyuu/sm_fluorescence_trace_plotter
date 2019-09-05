import imscrollIO
from pathlib import Path
import pandas as pd

xlspath = Path('D:/TYL/PriA_project/Analysis_Results/20190731/20190731parameterFile.xlsx')
datapath = imscrollIO.def_data_path()
dfs = pd.read_excel(xlspath)
nFiles = dfs.shape[0]
for iFile in range(0, nFiles):
    filestr = dfs.filename[iFile]
    data = imscrollIO.import_everything(filestr, datapath)
    datapath = data.datapath
    imscrollIO.save_data_to_netcdf(datapath / (filestr + '_data.nc'), data)
    print(filestr)
