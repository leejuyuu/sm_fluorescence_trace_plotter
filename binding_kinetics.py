import xarray as xr
import numpy as np



def remove_multiple_DNA(data, DNA_channel):
    def find_state_with_lowest_intensity():
        DNA_viterbi_intensity = data['viterbi_path'].sel(state='position', channel=DNA_channel)
        lowest_intensity = DNA_viterbi_intensity.min(dim='time')
        isLowest = (DNA_viterbi_intensity == lowest_intensity)
        DNA_viterbi_state_label = data['viterbi_path'].sel(state='label', channel=DNA_channel)
        selected_state_label = xr.DataArray(np.zeros(lowest_intensity.shape),
                                            dims='AOI',
                                            coords={'AOI': data.AOI})
        for iAOI in DNA_viterbi_state_label.AOI.values:
            bool_selected_time = isLowest.sel(AOI=iAOI)
            all_low_state_label_array = DNA_viterbi_state_label.sel(AOI=iAOI)[bool_selected_time]
            distinct_state_labels = set(all_low_state_label_array.values)
            if len(distinct_state_labels)==1:
                selected_state_label.loc[iAOI] = list(distinct_state_labels)[0]
        return selected_state_label


    def set_remove_more_than_two_states():

        return 0
        
    selected_state_label = find_state_with_lowest_intensity()
    return 0