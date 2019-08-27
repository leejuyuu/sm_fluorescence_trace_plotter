import xarray as xr
import numpy as np
import matplotlib.pyplot as plt


def remove_multiple_DNA(data, DNA_channel):
    def find_state_with_lowest_intensity():
        DNA_viterbi_intensity = data['viterbi_path'].sel(state='position', channel=DNA_channel)
        lowest_intensity = DNA_viterbi_intensity.min(dim='time')
        bool_lowest = (DNA_viterbi_intensity == lowest_intensity)
        DNA_viterbi_state_label = data['viterbi_path'].sel(state='label', channel=DNA_channel)
        selected_state_label = xr.DataArray(np.zeros(lowest_intensity.shape),
                                            dims='AOI',
                                            coords={'AOI': data.AOI})
        for iAOI in DNA_viterbi_state_label.AOI.values:
            bool_selected_time = bool_lowest.sel(AOI=iAOI)
            all_low_state_label_array = DNA_viterbi_state_label.sel(AOI=iAOI)[bool_selected_time]
            distinct_state_labels = set(all_low_state_label_array.values)
            if len(distinct_state_labels) == 1:
                selected_state_label.loc[iAOI] = list(distinct_state_labels)[0]
        return selected_state_label

    def get_number_of_states():
        DNA_viterbi_state_label = data['viterbi_path'].sel(state='label', channel=DNA_channel)
        nStates = DNA_viterbi_state_label.max(dim='time')
        return nStates

    def remove_more_than_two_states():
        badTethers = set(np.where(nStates>2)[0] + 1)
        return badTethers

    def check_if_lowest_state_equal_to_zero():
        bool_lowest_state_equal_to_zero = xr.DataArray(np.zeros(len(data.AOI)),
                                                       dims='AOI',
                                                       coords={'AOI': data.AOI})
        for iAOI in data.AOI:
            bool_lowest_state = data['viterbi_path'].sel(state='label', channel=DNA_channel, AOI=iAOI) \
                                == lowest_state_label.loc[iAOI]
            lowest_state_std = np.std(data['intensity'].sel(
                channel=DNA_channel, AOI=iAOI)[bool_lowest_state])
            lowest_state_mean = np.mean(data['viterbi_path'].sel(state='position',
                                                                 channel=DNA_channel,
                                                                 AOI=iAOI)[bool_lowest_state])
            bool_lowest_state_equal_to_zero.loc[iAOI] = abs(lowest_state_mean) < 2*lowest_state_std
        return bool_lowest_state_equal_to_zero

    def remove_two_state_with_lowest_not_equal_to_zero(badTethers=set()):
        bad_tether_condition = (nStates != 2) \
                               & xr.ufuncs.logical_not(bool_lowest_state_equal_to_zero)
        new_bad_tether_set = set(data.AOI[bad_tether_condition].values)
        badTethers = badTethers | new_bad_tether_set
        return badTethers

    lowest_state_label = find_state_with_lowest_intensity()
    bool_lowest_state_equal_to_zero = check_if_lowest_state_equal_to_zero()
    nStates = get_number_of_states()
    data['lowest_state_label'] = lowest_state_label
    data['nStates'] = nStates
    data['bool_lowest_state_equal_to_zero'] = bool_lowest_state_equal_to_zero

    all_tethers_set = set(data.AOI.values)
    badTethers = remove_more_than_two_states()
    badTethers = remove_two_state_with_lowest_not_equal_to_zero(badTethers=badTethers)
    good_tethers = all_tethers_set - badTethers
    selected_data = data.sel(AOI=list(good_tethers))
    return selected_data


def match_vit_path_to_intervals(data, DNA_channel):
    bad_aoi_list = []
    for iAOI in data.AOI:
        print(iAOI)
        state_sequence = data['viterbi_path'].sel(state='label', channel='green', AOI=iAOI)
        state_start_index = find_state_end_point(state_sequence)
        event_time = assign_event_time(state_sequence, state_start_index)
        intervals = set_up_intervals(data.time, event_time)
        intervals = assign_state_number_to_intervals(data.sel(AOI=iAOI), intervals)
        if find_any_bad_intervals(data.sel(AOI=iAOI), intervals):
            bad_aoi_list.append(iAOI.values)
    print(bad_aoi_list)
    return 0


def find_state_end_point(state_sequence):
    change_array = state_sequence.diff(dim='time')
    state_start_index = np.nonzero(change_array.values)[0]
    return state_start_index


def assign_event_time(state_sequence, state_end_index):
    time_for_each_frame = state_sequence.time
    event_time = np.zeros((len(state_end_index) + 2))
    event_time[0] = time_for_each_frame[0]
    event_time[-1] = time_for_each_frame[-1]
    # Assign the time point for events as the mid-point between two points that have different
    # state labels
    for i, i_end_index in enumerate(state_end_index):
        event_time[i+1] = (time_for_each_frame[i_end_index] +
                           time_for_each_frame[i_end_index+1])/2
    return event_time


def set_up_intervals(time_coord, event_time):
    intervals = xr.Dataset({'indices': (['interval_number'], np.zeros((len(event_time)-1),
                                                                      dtype=object))},
                           coords={'interval_number': range(len(event_time)-1)})
    intervals['duration'] = xr.DataArray(np.diff(event_time),
                                         dims='interval_number',
                                         coords={'interval_number': intervals.interval_number})
    intervals['start'] = xr.DataArray(event_time[0:-1], dims='interval_number')
    intervals['end'] = xr.DataArray(event_time[1:], dims='interval_number')
    return intervals


def shift_state_number(AOI_data):
    if AOI_data['bool_lowest_state_equal_to_zero']:
        if AOI_data['lowest_state_label'] == 1:
            AOI_data['viterbi_path'].loc[:, 'label', 'green'] = AOI_data['viterbi_path'].loc[:, 'label', 'green']-1
        else:
            raise ValueError('shift_state_number:\nlowest state not equal to 1')
    return AOI_data



def assign_state_number_to_intervals(AOI_data, intervals):
    AOI_data = shift_state_number(AOI_data)
    intervals_state_number = xr.DataArray(np.zeros(len(intervals.interval_number)),
                                          dims='interval_number',
                                          coords={'interval_number': intervals.interval_number})
    for i in intervals['interval_number']:
        interval_slice = slice(intervals['start'].loc[i], intervals['end'].loc[i])
        distinct_state_numbers = set(AOI_data['viterbi_path'].sel(state='label',
                                                                  channel='green',
                                                                  time=interval_slice).values)
        if len(distinct_state_numbers) == 1:
            intervals_state_number.loc[i] = list(distinct_state_numbers)[0]

        else:
            raise ValueError('assign_state_number_to_intervals:\nThere are more than one state in this interval.')
    intervals['state_number'] = intervals_state_number
    return intervals


def find_any_bad_intervals(AOI_data, intervals):
    out = False
    for i in intervals['interval_number']:
        interval_slice = slice(intervals['start'].loc[i], intervals['end'].loc[i])
        chunk_of_interval_traces = AOI_data['interval_traces'].sel(time=interval_slice,
                                                                   channel='green')
        if (intervals['state_number'].loc[i] != 0) & \
                (sum(chunk_of_interval_traces) < 0.9*len(chunk_of_interval_traces)):
            out = True
            break
    return out









