import unittest
from python_for_imscroll import binding_kinetics as bk
import numpy as np
import xarray as xr

class Test(unittest.TestCase):
    def test_find_state_end_equal_steps(self):
        sequence = xr.DataArray(np.repeat(np.arange(5), 10),
                                dims='time')
        state_end_index = bk.find_state_end_point(sequence)
        np.testing.assert_array_equal(state_end_index, np.array(range(9, 40, 10)))

    def test_assign_event_time_equal_steps(self):
        sequence = xr.DataArray(np.repeat(np.arange(5), 10),
                                dims='time',
                                coords={'time': range(50)})
        state_end_index = np.array(range(9, 40, 10))
        event_time = bk.assign_event_time(sequence, state_end_index)
        expected_result = np.concatenate(([0], state_end_index+0.5, [49]))
        np.testing.assert_array_equal(event_time, expected_result)




if __name__ == '__main__':
    unittest.main()
