import scipy.io as sio
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path
import pandas as pd
import xarray as xr


def def_data_path():
    datapath = Path('D:/matlab_CoSMoS/data/')
    return datapath


def import_intensity_traces(datapath, filestr):
    intensity_file_path = datapath / (filestr + '_traces.dat')
    traces_file = sio.loadmat(intensity_file_path)
    array_shape = traces_file['traces']['green'][0, 0].shape
    intensity = np.stack((traces_file['traces']['green'][0, 0],
                          traces_file['traces']['red'][0, 0]),
                         -1)
    intensity = xr.DataArray(intensity,
                             dims=('AOI', 'time', 'channel'),
                             coords={'AOI': range(array_shape[0]),
                                     'channel': ['green', 'red']})
    intensity.attrs['datapath'] = datapath
    intensity.attrs['filestr'] = filestr

    return intensity

def import_image_path_from_driftfit(intensity):
    driftfit_file_path = intensity.datapath / (intensity.filestr + '_driftfit.dat')
    driftfit_file = sio.loadmat(driftfit_file_path)
    intensity.attrs['image_path'] = Path(driftfit_file['aoifits']['tifFile'][0][0][0])
    return intensity


def import_time_stamps(intensity):
    time_stamp_txt = intensity.attrs['image_path'].with_suffix('.txt')
    time_data = np.loadtxt(time_stamp_txt)
    time_data[1, :] = np.cumsum(time_data[1, :])
    intcorrected_file_path = intensity.datapath / (intensity.filestr + '_intcorrected.dat')
    intcorrected_file = sio.loadmat(intcorrected_file_path)
    frames_used_in_intensity_cal = intcorrected_file['aoifits']['dataRed'][0, 0][:, 1]
    frame_start = int(frames_used_in_intensity_cal.min())
    frame_end = int(frames_used_in_intensity_cal.max())

    intensity.attrs['frame_start'] = frame_start
    intensity.attrs['frame_end'] = frame_end

    time_stamps = time_data[1, frame_start:frame_end+1]
    intensity = intensity.assign_coords(time=time_stamps)

    return intensity
