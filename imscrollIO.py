import scipy.io as sio
import numpy as np
from pathlib import Path
import xarray as xr
from tkinter import Tk, filedialog


def import_everything(filestr, datapath):

    data = initialize_data_from_intensity_traces(datapath, filestr)
    data = import_image_path_from_driftfit(data)
    data = import_time_stamps(data)
    data = import_interval_results(data)
    data = import_viterbi_paths(data)
    return data


def def_data_path():
    # with open('pathconfig.txt', 'r') as pathconfig:
    #     path = pathconfig.readline()
    # path = path[:-1]
    # datapath = Path(path)
    root = Tk()
    data_dir_str = filedialog.askdirectory()
    root.destroy()
    datapath = Path(data_dir_str)
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
                             coords={'AOI': range(1, array_shape[0]+1),
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
                                   coords={'AOI': range(1, data.intensity.shape[0]+1),
                                           'channel': [channel]})
    data['interval_traces'] = interval_traces
    return data


def import_viterbi_paths(data):
    eb_file_path = data.datapath / (data.filestr + '_eb.dat')
    eb_file = sio.loadmat(eb_file_path)
    red_vit = np.zeros((len(data.AOI), len(data.time), 2))
    green_vit = np.zeros((len(data.AOI), len(data.time), 2))
    for iAOI in range(0, len(data.AOI)):
        red_vit[iAOI, :, 0] = eb_file['redVit'][0, iAOI]['x'].reshape((len(data.time)))
        red_vit[iAOI, :, 1] = eb_file['redVit'][0, iAOI]['z'].reshape((len(data.time)))
    for iAOI in range(0, len(data.AOI)):
        green_vit[iAOI, :, 0] = eb_file['greenVit'][0, iAOI]['x'].reshape((len(data.time)))
        green_vit[iAOI, :, 1] = eb_file['greenVit'][0, iAOI]['z'].reshape((len(data.time)))
    viterbi_path = np.stack((red_vit, green_vit), -1)
    viterbi_path = xr.DataArray(viterbi_path,
                                dims=('AOI', 'time', 'state', 'channel'),
                                coords={'channel': ['red', 'green'],
                                        'state': ['position', 'label']})
    data['viterbi_path'] = viterbi_path
    return data


def save_data_to_netcdf(path, data):
    data.attrs['datapath'] = str(data.datapath)
    data.attrs['image_path'] = str(data.image_path)
    data.to_netcdf(path)
    return 0

def load_data_from_netcdf(path):
    data = xr.open_dataset(path)
    data.attrs['datapath'] = Path(data.datapath)
    data.attrs['image_path'] = Path(data.image_path)
    return data
