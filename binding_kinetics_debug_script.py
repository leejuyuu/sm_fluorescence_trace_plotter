import imscrollIO
import binding_kinetics
from pathlib import Path
DNA_channel = 'red'
protein_channel = 'green'
out = {}
path = Path('/mnt/linuxData/Google_drive_leejuyuu/Research/anal_dataset/L2_02_01_data.nc')
data = imscrollIO.load_data_from_netcdf(path)
data = binding_kinetics.collect_all_channel_state_info(data)
DNA_channel_data = binding_kinetics.collect_channel_state_info(data.sel(channel=DNA_channel))
bad_tethers = binding_kinetics.list_multiple_DNA(DNA_channel_data)
out['multiple_tethers'], selected_data \
    = binding_kinetics.split_data_set_by_specifying_aoi_subset(data, bad_tethers)

bad_aoi_set, intervals = binding_kinetics.match_vit_path_to_intervals(selected_data.sel(channel=protein_channel))
out['false_binding'], selected_data \
    = binding_kinetics.split_data_set_by_specifying_aoi_subset(selected_data, bad_aoi_set)

bad_intervals, good_intervals = binding_kinetics.split_data_set_by_specifying_aoi_subset(intervals, bad_aoi_set)



123


