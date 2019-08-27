import imscrollIO
import binding_kinetics
import xarray as xr
selected_data = imscrollIO.load_data_from_netcdf('good_data.nc')
# selected_data = binding_kinetics.collect_all_channel_state_info(selected_data)
good_intervals = xr.load_dataset('good_intervals.nc')
data_dict, intervals_dict = \
    binding_kinetics.group_analyzable_aois_into_state_number(selected_data, good_intervals)

123