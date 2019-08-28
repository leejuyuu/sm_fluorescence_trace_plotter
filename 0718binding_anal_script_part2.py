import imscrollIO
import binding_kinetics
import xarray as xr
import pandas as pd
from pathlib import Path

xlspath = Path('D:/TYL/PriA_project/Analysis_Results/20190718/20190718parameterFile.xlsx')
dfs = pd.read_excel(xlspath)
nFiles = dfs.shape[0]
state_1_intervals_list = []
for iFile in range(0, nFiles):
    out = {}
    filestr = dfs.filename[iFile]
    datapath = Path('D:/matlab_CoSMoS/data/')
    gdata_path = datapath / (filestr + '_data.nc')
    gintervals_path = datapath / (filestr + '_gintervals.nc')

    selected_data = imscrollIO.load_data_from_netcdf(gdata_path)
    # selected_data = binding_kinetics.collect_all_channel_state_info(selected_data)
    good_intervals = xr.load_dataset(gintervals_path)
    data_dict, intervals_dict = \
        binding_kinetics.group_analyzable_aois_into_state_number(selected_data, good_intervals)
    state_1_intervals_list.append(intervals_dict[1])
state_1_intervals = xr.concat(state_1_intervals_list, dim='files')

123