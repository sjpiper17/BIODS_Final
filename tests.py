#import stuff you need
import unittest
import sys
import numpy as np
from numpy import mean
from numpy import var
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import logging
from datetime import datetime as dt
from datetime import timedelta
from scipy import stats
from math import sqrt
from IPython.display import display

#import your map and reduce functions from the program
from sleep_analysis_lib import basic_stats, cohend

#create test data
stats_test_data = pd.DataFrame([1, 3, 4, 5, 3, 6, 8, 9, 10, 5, 4, 4, 3])
cohen_test_1 = [1, 5, 5, 3, 5, 7, 8, 12, 32 ,17, 9]
cohen_test_2 = [3, 21, 29, 4, 16, 12, 7, 4, 3, 2, 6, 7, 8]

#Define the test function class
class TestSleepAnalysis(unittest.TestCase):
    
    def setUp(self):
        # set stuff up here
        pass

    def tearDown(self):
        # tear stuff down here
        pass

    #this test determines if the basic_stats function correctly calculates and reports the statistics desired
    def test_basic_stats(self):
        my_mean, my_median, my_std, my_min, my_max = basic_stats(stats_test_data, label = 'test', Decimals = 2)
        self.assertEqual([my_mean.iloc[0], my_median.iloc[0], my_std.iloc[0], my_min.iloc[0], my_max.iloc[0]], [5, 4, 2.61, 1, 10])
        print('pass test')

    #this test determines that cohen's d is accurately calculated
    def cohens_test(self):
        eff_size, eff_string = cohend(cohen_test_1, cohen_test_2)
        self.assertEqual([eff_size, eff_string], [0.01, 'Effect size is trivial'])
        print('pass test')

if __name__ == '__main__':
    unittest.main()





# from sleep_analysis import basic_stats


# def test_basic_stats():
#     # Test case 1
#     expected_output_1 = (,,,,,)
#     output_1 = basic_stats(,,,)
#     assert(expected_output_1 == output_1)


# if __name__ == '__main__':
