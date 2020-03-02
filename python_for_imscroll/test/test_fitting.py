import unittest
import numpy as np
from python_for_imscroll import fitting

class TestFitting(unittest.TestCase):

    def test_functional(self):
        # Jack has a x, y dataset. He want to fit the data to a straight line.
        x = np.linspace(0, 100, 0.1)
        y = 2 * x + 1

        # Jack calls the main function in the fitting module, and gets a return
        # value called result, which is a dict.
        result = fitting.main(x, y)
        self.assertIs(result, dict)

        # Jack looks into the dict, and he finds keys called 'slope',
        # 'intercept', 'r_squared'. The corresponding values are the fitting
        # result.
        self.assertIn('slope', result)
        self.assertIn('intercept', result)
        self.assertIn('r_squared', result)

if __name__ == '__main__':
    unittest.main()
