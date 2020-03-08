#  Copyright (C) 2020 Tzu-Yu Lee, National Taiwan University
#
#  This file (test_categorize_binding_traces.py) is part of python_for_imscroll.
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

from pathlib import Path
import pytest
import xarray.testing
from python_for_imscroll import binding_kinetics
from python_for_imscroll import categorize_binding_traces_script as cbt



def test_categorization():
    test_data_path = Path(__file__).parent / 'test_data/20200228/'
    test_parameter_file_path = test_data_path / '20200228parameterFile.xlsx'

    all_data, aoi_categories = cbt.categorize_binding_traces(test_parameter_file_path,
                                                             ['L2'],
                                                             test_data_path,
                                                             save_file=False)
    true_all_data, true_aoi_categories = binding_kinetics.load_all_data(test_data_path
                                                                        / 'L2_all.json')
    analyzable_key_casted = dict()
    for key, value in aoi_categories['analyzable'].items():
        analyzable_key_casted[str(key)] = list(value)
    for key, value in aoi_categories.items():
        if key == 'analyzable':
            continue
        aoi_categories[key] = list(value)
    aoi_categories['analyzable'] = analyzable_key_casted
    assert aoi_categories == true_aoi_categories
    for key in true_all_data:
        if key in ('state_info', 'intervals'):
            xarray.testing.assert_equal(all_data[key], true_all_data[key])
        else:
            for channel in set(true_all_data[key].channel.values.tolist()):
                xarray.testing.assert_equal(all_data[key].sel(channel=channel),
                                            true_all_data[key].sel(channel=channel))
