import imscrollIO
import binding_kinetics
import xarray as xr
import pandas as pd
from pathlib import Path
import numpy as np
import math
from scipy import optimize
from matplotlib import pyplot as plt

datapath = imscrollIO.def_data_path()
xlspath = Path('D:/TYL/PriA_project/Analysis_Results/20190731/20190731parameterFile.xlsx')
dfs = pd.read_excel(xlspath)
nFiles = dfs.shape[0]
state_1_intervals_list = []
for iFile in range(0, nFiles):
    out = {}
    filestr = dfs.filename[iFile]

    gdata_path = datapath / (filestr + '_data.nc')
    gintervals_path = datapath / (filestr + '_gintervals.nc')

    selected_data = imscrollIO.load_data_from_netcdf(gdata_path)
    # selected_data = binding_kinetics.collect_all_channel_state_info(selected_data)
    good_intervals = xr.load_dataset(gintervals_path)
    data_dict, intervals_dict = \
        binding_kinetics.group_analyzable_aois_into_state_number(selected_data, good_intervals)
    state_1_intervals_list.append(intervals_dict[1])
# state_1_intervals = xr.concat(state_1_intervals_list, dim='files')
dwells = binding_kinetics.extract_dwell_time(state_1_intervals_list, 0, 1)
# np.savetxt('L2_02_dwell.csv', dwells, delimiter=',')
max_dwell = dwells.max()

bin_width = 10
n_bins = math.floor(max_dwell/bin_width)+1
n_edge = n_bins + 1
prob_den, edges = np.histogram(dwells, bins=range(0, n_edge*bin_width, bin_width), density=True)
centers = (edges[0:-1]+edges[1:])/2
def single_exponential(x, a):
    return a*np.exp(-a*x)

mean_dwell = dwells.mean()
params, params_covariance = optimize.curve_fit(single_exponential,
                                               centers, prob_den,
                                               p0=[1/np.mean(dwells)])


fit_x = np.arange(centers[0], centers[-1], 1)
fit_y = single_exponential(fit_x, params)
plt.plot(fit_x, fit_y, color='red')
# plt.show()
plt.bar(centers, prob_den, width=bin_width)
plt.xlabel('t (s)', fontsize=16)
plt.ylabel('probability density (s$^-$$^1$)', fontsize=16)
k_str = 'k = {:.5f} s^-1'.format((params[0]))
ax = plt.gca()
plt.text(0.65, 0.8, k_str, transform=ax.transAxes, fontsize=14)
plt.xlim((0, 400))


plt.savefig('L4_03_high_tplot', Transparent=True,
                   dpi=300, bbox_inches='tight')

print(params)



123