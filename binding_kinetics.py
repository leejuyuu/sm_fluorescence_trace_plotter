import xarray as xr
import numpy as np


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

    def remove_two_state_with_lowest_not_equal_to_zero(badTethers=set()):
        good_tethers = all_tethers_set - badTethers
        new_bad_tether_list = []
        for iAOI in good_tethers:
            if nStates.loc[iAOI] != 2:
                continue
            bool_lowest_state = data['viterbi_path'].sel(state='label', channel=DNA_channel, AOI=iAOI)\
                == lowest_state_label.loc[iAOI]

            lowest_state_std = np.std(data['intensity'].sel(
                                     channel=DNA_channel, AOI=iAOI)[bool_lowest_state])
            lowest_state_mean = np.mean(data['viterbi_path'].sel(state='position',
                                                                 channel=DNA_channel,
                                                                 AOI=iAOI)[bool_lowest_state])
            if abs(lowest_state_mean) > 2*lowest_state_std:
                new_bad_tether_list.append(iAOI)
        badTethers = badTethers | set(new_bad_tether_list)

        return badTethers

    lowest_state_label = find_state_with_lowest_intensity()
    nStates = get_number_of_states()
    all_tethers_set = set(data.AOI.values)
    badTethers = remove_more_than_two_states()
    badTethers = remove_two_state_with_lowest_not_equal_to_zero(badTethers=badTethers)
    good_tethers = all_tethers_set - badTethers
    selected_data = data.sel(AOI=list(good_tethers))
    return selected_data


