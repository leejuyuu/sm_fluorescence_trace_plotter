import imscrollIO
import binding_kinetics
from pathlib import Path


path = Path('/mnt/linuxData/Google_drive_leejuyuu/Research/anal_dataset/L2_02_01_data.nc')
data = imscrollIO.load_data_from_netcdf(path)
binding_kinetics.remove_multiple_DNA(data, 'red')
123


