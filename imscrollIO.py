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


def initialize_data_from_intensity_traces(datapath, filestr):
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


    data = xr.Dataset({'intensity': (['AOI', 'time', 'channel'], intensity)},
                      coords={'AOI': intensity.AOI,
                              'time': intensity.time,
                              'channel': intensity.channel})
    data.attrs['datapath'] = datapath
    data.attrs['filestr'] = filestr

    return data

def import_image_path_from_driftfit(data):
    driftfit_file_path = data.datapath / (data.filestr + '_driftfit.dat')
    driftfit_file = sio.loadmat(driftfit_file_path)
    data.attrs['image_path'] = Path(driftfit_file['aoifits']['tifFile'][0][0][0])
    return data


def import_time_stamps(data):
    time_stamp_txt = data.attrs['image_path'].with_suffix('.txt')
    time_data = np.loadtxt(time_stamp_txt)
    time_data[1, :] = np.cumsum(time_data[1, :])
    intcorrected_file_path = data.datapath / (data.filestr + '_intcorrected.dat')
    intcorrected_file = sio.loadmat(intcorrected_file_path)
    frames_used_in_intensity_cal = intcorrected_file['aoifits']['dataRed'][0, 0][:, 1]
    frame_start = int(frames_used_in_intensity_cal.min())
    frame_end = int(frames_used_in_intensity_cal.max())

    data.attrs['frame_start'] = frame_start
    data.attrs['frame_end'] = frame_end

    time_stamps = time_data[1, frame_start:frame_end+1]
    data = data.assign_coords(time=time_stamps)

    return data


def import_interval_results(data, channel='green'):
    interval_file_path = data.datapath / (data.filestr + '_interval.dat')
    interval_file = sio.loadmat(interval_file_path)
    interval_traces = np.zeros(data.intensity.shape[0:2])
    for iAOI in range(0, data.intensity.shape[0]):
        interval_traces[iAOI, :] = \
            interval_file['IntervalDataStructure'][0, 0]['AllTracesCellArray'][iAOI, 0][:, 0]
    interval_traces = np.expand_dims(interval_traces, 3)
    interval_traces = xr.DataArray(interval_traces,
                                   dims=('AOI', 'time', 'channel'),
                                   coords={'AOI': range(data.intensity.shape[0]),
                                           'channel': [channel]})
    data['interval_traces'] = interval_traces


    return data


