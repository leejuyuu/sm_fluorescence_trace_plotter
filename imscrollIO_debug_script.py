import imscrollIO

datapath = imscrollIO.def_data_path()
intensity = imscrollIO.import_intensity_traces(datapath, 'L2_02_01')
intensity = imscrollIO.import_image_path_from_driftfit(intensity)
intensity = imscrollIO.import_time_stamps(intensity)
intensity = imscrollIO.import_interval_results(intensity)