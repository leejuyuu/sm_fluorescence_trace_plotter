import imscrollIO
import xarray as xr

datapath = imscrollIO.def_data_path()
data = imscrollIO.initialize_data_from_intensity_traces(datapath, 'L2_02_01')
data = imscrollIO.import_image_path_from_driftfit(data)
data = imscrollIO.import_time_stamps(data)
data = imscrollIO.import_interval_results(data)
data = imscrollIO.import_viterbi_paths(data)

123