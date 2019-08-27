import imscrollIO
import binding_kinetics
from pathlib import Path
DNA_channel = 'red'
protein_channel = 'green'

path = Path('/mnt/linuxData/Google_drive_leejuyuu/Research/anal_dataset/L2_02_01_data.nc')
data = imscrollIO.load_data_from_netcdf(path)
DNA_channel_data = binding_kinetics.collect_channel_state_info(data.sel(channel=DNA_channel))
good_tethers = binding_kinetics.unlist_multiple_DNA(DNA_channel_data)
selected_data = binding_kinetics.remove_multiple_DNA_from_dataset(data, good_tethers)

bad_aoi_list = binding_kinetics.match_vit_path_to_intervals(selected_data, 'red')

123


