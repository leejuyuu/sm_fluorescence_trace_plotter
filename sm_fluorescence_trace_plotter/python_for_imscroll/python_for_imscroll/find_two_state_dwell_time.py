#  Copyright (C) 2020 Tzu-Yu Lee, National Taiwan University
#
#  This file (find_two_state_dwell_time.py) is part of python_for_imscroll.
#
#  python_for_imscroll is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  python_for_imscroll is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with python_for_imscroll.  If not, see <https://www.gnu.org/licenses/>.

"""This is a temporary script that analyzes the dwell times of two state model."""

from typing import List, Tuple
from pathlib import Path
import h5py
import numpy as np
import pandas as pd
import xarray as xr
import rpy2.robjects as robjects
import rpy2.robjects.pandas2ri
from rpy2.robjects.packages import importr
from rpy2.robjects.conversion import localconverter
from matplotlib import pyplot as plt
from lifelines import KaplanMeierFitter, ExponentialFitter
from python_for_imscroll import imscrollIO
from python_for_imscroll import binding_kinetics


def find_two_state_dwell_time(parameter_file_path: Path, sheet_list: List[str]):
    datapath = imscrollIO.def_data_path()
    state_category = '1'
    state_list = ['low', 'high']

    im_format = 'svg'
    for i_sheet in sheet_list:
        interval_list, n_good_traces, max_time = read_interval_data(parameter_file_path,
                                                                    datapath,
                                                                    i_sheet,
                                                                    state_category)
        for i, item in enumerate(state_list):
            dwells = binding_kinetics.extract_dwell_time(interval_list, i)
            if len(dwells.duration) == 0:
                print('no {} state found'.format(item))
                continue
            kmf = KaplanMeierFitter()
            exf = ExponentialFitter()
            kmf.fit(dwells.duration, dwells.event_observed)
            exf.fit(dwells.duration, dwells.event_observed)
            n_event = np.count_nonzero(dwells.event_observed)
            n_censored = len(dwells.event_observed) - n_event
            stat_counts = (n_event, n_censored, n_good_traces)
            save_fig_path = datapath / (i_sheet + '_' + item + '_dwell' + '.' + im_format)
            plot_survival_curve(kmf, exf, i, stat_counts, save_fig_path,
                                x_right_lim=max_time)


def find_first_dwell_time(parameter_file_path: Path, sheet_list: List[str],
                          time_offset: float = 0):
    datapath = imscrollIO.def_data_path()
    state_category = '1'
    im_format = 'svg'
    for i_sheet in sheet_list:
        time_offset = read_time_offset(parameter_file_path, i_sheet)
        zero_state_interval_list = read_interval_data(parameter_file_path,
                                                      datapath,
                                                      i_sheet,
                                                      '0',
                                                      first_only=True)[0]
        n_right_censored = len(zero_state_interval_list[0].AOI)
        interval_list, n_good_traces, max_time = read_interval_data(parameter_file_path,
                                                                    datapath,
                                                                    i_sheet,
                                                                    state_category,
                                                                    first_only=True)
        dwells = binding_kinetics.extract_first_binding_time(interval_list)
        dwells['duration'] += time_offset
        max_time += time_offset
        interval_censor_table = np.zeros((len(dwells.duration) + n_right_censored,
                                          2))

        interval_censor_table[0:len(dwells.duration), 0] = dwells.duration.values
        interval_censor_table[0:len(dwells.duration), 1] = xr.where(dwells.event_observed,
                                                                    1,
                                                                    2).values
        interval_censor_table[len(dwells.duration):, 0] = max_time
        interval_censor_table[len(dwells.duration):, 1] = 0
        df = pd.DataFrame(interval_censor_table, columns=['time', 'status'])

        if len(dwells.duration) == 0:
            print('no low state found')
            continue
        n_event = np.count_nonzero(dwells.event_observed)
        n_censored = len(dwells.event_observed) - n_event
        stat_counts = (n_event, n_censored, n_right_censored)

        save_fig_path = datapath / (i_sheet + '_' + '_first_dwellr' + '.' + im_format)
        call_r_survival(df, save_fig_path, stat_counts)


def call_r_survival(df: pd.DataFrame, save_path: Path, stat_counts: Tuple[int, int, int]):
    rpy2.robjects.pandas2ri.activate()
    survival = importr('survival')

    with localconverter(robjects.default_converter + rpy2.robjects.pandas2ri.converter):
        r_from_pd_df = robjects.conversion.py2rpy(df)
    robjects.r('surv <- with({}, Surv(time=time, time2=time, event=status, type="interval"))'.format(r_from_pd_df.r_repr()))
    robjects.r('fit <- survfit(surv~1, data={})'.format(r_from_pd_df.r_repr()))
    robjects.r('fit0 <- survfit0(fit)')
    time = robjects.r('fit0[["time"]]')
    surv = robjects.r('fit0[["surv"]]')
    upper_ci = robjects.r('fit0[["upper"]]')
    lower_ci = robjects.r('fit0[["lower"]]')

    robjects.r('exreg <- survreg(surv~1, data={}, dist="exponential")'.format(r_from_pd_df.r_repr()))
    intercept = robjects.r('exreg["coefficients"]')[0].item()
    log_var = robjects.r('exreg["var"]')[0].item()
    k = np.exp(-intercept)
    tau_ci = np.exp(intercept + np.array([-1, 1])*log_var)
    x = np.linspace(0, time[-1], time[-1]*10)
    y = np.exp(-k*x)

    plt.step(time, surv, where='post')
    plt.plot(x, y)
    plt.step(time, upper_ci, 'c', where='post')
    plt.step(time, lower_ci, 'c', where='post')
    plt.ylim(bottom=0)
    ax = plt.gca()
    k_str = r'$k_{{{}}}$ = {:.1f} s'.format('obs', 1/k.item())
    plt.text(0.6, 0.8, k_str, transform=ax.transAxes, fontsize=14)
    string = '{}, {}, {}'.format(*stat_counts)
    plt.text(0.6, 0.6, string, transform=ax.transAxes, fontsize=14)
    ci_string = 'ci: [{:.1f}, {:.1f}]'.format(tau_ci[0], tau_ci[1])
    plt.text(0.6, 0.7, ci_string, transform=ax.transAxes, fontsize=14)

    plt.rcParams['svg.fonttype'] = 'none'
    plt.savefig(save_path, format='svg', Transparent=True,
                dpi=300, bbox_inches='tight')
    plt.close()
    data_file_path = save_path.with_suffix('.hdf5')
    with h5py.File(data_file_path, 'w') as f:
        column_keys = np.array(['time', 'survival', 'upper_ci', 'lower_ci'], dtype='S')
        group_survival_curve = f.create_group('survival_curve')
        group_survival_curve.create_dataset('column_keys', column_keys.shape,
                                            column_keys.dtype, column_keys)
        surv_data = np.stack([time, surv, upper_ci, lower_ci])
        group_survival_curve.create_dataset('data', surv_data.shape,
                                            'f', surv_data)
        group_exp_model = f.create_group('exp_model')
        group_exp_model.create_dataset('k', (1,), 'f', k)
        group_exp_model.create_dataset('log_variance', (1,), 'f', log_var)


def plot_survival_curve(kmf: KaplanMeierFitter,
                        exf: ExponentialFitter,
                        state: int,
                        stat_counts: Tuple[int, int, int],
                        save_path: Path,
                        x_right_lim: float = None):
    on_off_str = ['on', 'off']
    obs_off_str = ['obs', 'off']
    ax = kmf.plot_survival_function()
    exf.plot_survival_function(ax=ax, ci_show=False)
    ax.get_legend().remove()
    plt.xlabel(r'$\tau_{{{}}}$ (s)'.format(on_off_str[state]), fontsize=16)
    plt.ylabel('probability', fontsize=16)
    k_str = r'$k_{{{}}}$ = {:.1f} s'.format(obs_off_str[state], exf.lambda_)
    string = '{}, {}, {}'.format(*stat_counts)
    plt.text(0.6, 0.8, k_str, transform=ax.transAxes, fontsize=14)
    plt.text(0.6, 0.6, string, transform=ax.transAxes, fontsize=14)
    plt.xlim(left=0)
    if x_right_lim is not None:
        plt.xlim(right=x_right_lim)

    plt.rcParams['svg.fonttype'] = 'none'
    plt.savefig(save_path, format='svg', Transparent=True,
                dpi=300, bbox_inches='tight')
    plt.close()


def read_time_offset(parameter_file_path: Path, sheet: str):
    dfs = pd.read_excel(parameter_file_path, sheet_name=sheet)
    return dfs['time offset'][0]


def read_interval_data(parameter_file_path: Path,
                       datapath: Path,
                       sheet: str,
                       state_category: str,
                       first_only: bool = False):
    dfs = pd.read_excel(parameter_file_path, sheet_name=sheet)
    if first_only:
        n_files = 1
    else:
        n_files = dfs.shape[0]
    interval_list = []
    n_good_traces = 0
    for iFile in range(0, n_files):
        filestr = dfs.filename[iFile]
        try:
            all_data, AOI_categories = binding_kinetics.load_all_data(datapath
                                                                      / (filestr + '_all.json'))
        except FileNotFoundError:
            print('{} file not found'.format(filestr))
            continue

        print(filestr + ' loaded')
        if state_category in AOI_categories['analyzable']:
            aoi_list = AOI_categories['analyzable'][state_category]
            n_good_traces += len(aoi_list)
            interval_list.append(all_data['intervals'].sel(AOI=aoi_list))
    max_time = all_data['data'].time.values.max()
    return interval_list, n_good_traces, max_time


def main():
    """main function"""
    xlsx_parameter_file_path = imscrollIO.get_xlsx_parameter_file_path()
    sheet_list = imscrollIO.input_sheets_for_analysis()
    # find_two_state_dwell_time(xlsx_parameter_file_path, sheet_list)
    find_first_dwell_time(xlsx_parameter_file_path, sheet_list)


if __name__ == '__main__':
    main()
