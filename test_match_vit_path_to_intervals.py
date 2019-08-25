import unittest
import binding_kinetics as bk
import numpy as np
import xarray as xr

class Test(unittest.TestCase):
    def test_equal_steps(self):
        sequence = xr.DataArray(np.repeat(np.arange(5), 10),
                                dims='time')
        state_start_index = bk.find_state_start_point(sequence)
        np.testing.assert_array_equal(state_start_index, np.array(range(9, 40, 10)))



if __name__ == '__main__':
    unittest.main()
