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
    arrayShape = traces_file['traces']['green'][0, 0].shape
    a = (1, 100)
    b = a + (120,)
    t = arrayShape + (2 ,)
    intensity = np.zeros((arrayShape + (2,)))
    intensity[:, :, 0] = traces_file['traces']['green'][0, 0]
    intensity[:, :, 1] = traces_file['traces']['red'][0, 0]

    intensity = xr.DataArray(intensity,
                             dims=('AOI', 'time', 'channel'),
                             coords={'AOI': range(arrayShape[0]),
                                     'channel': ['green', 'red']})

    return intensity



