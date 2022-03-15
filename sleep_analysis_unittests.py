#This collection of unit tests is meant to test the functions in sleep_analysis_lib.py. It 
#is being completed as part of the Stanford class BIODS 253: Software Engineering for Scientists 
#by Stanford Bioengineering graduate student Scott Piper (sjpiper@stanford.edu) in Winter quarter 2022.
#The content from this program is inspired by a problem set from the Stanford class BIOE 217: Translational Bioinformatics.
#Data come from this research paper: Li, X., Dunn, J., Salins, D., Zhou, G., Zhou, W., Rose, S. M. S. F., ... & Sonecha, R. (2017). 
#Digital health: tracking physiomes and activity using wearable biosensors reveals useful health-related information. PLoS biology,
# 15(1), e2001402

#These unit tests can be run from the command line using 'python3 sleep_analysis_unittests.py'. The unit tests use the test data 
#found in the files 'sleep_test_data_in.csv', 'sleep_test_data_out.csv', 'activity_test_data_in.csv', 'activity_test_data_out.csv', 
#and 'flight_effect_test_data_out.csv'. 

#-------------------------------------------------------------------------------------------------------------------------------------

#Import necessary libraries and functions for the program

from sleep_analysis_cli import DATE_STRING, DECIMALS
from sleep_analysis_lib import basic_stats, cohend, sleep_processing, activity_processing, flight_effect_sleep
import unittest
import pandas as pd
import os
import sys

#-------------------------------------------------------------------------------------------------------------------------------------

# #Set constants

# #Number of decimals to round to in reporting statisitics
# DECIMALS = 2
# #Which characters of a string to keep in order to isolate the date from time data
# DATE_STRING = 10

#-------------------------------------------------------------------------------------------------------------------------------------

#Create a class called HiddenPrints to supress print outputs of functions from the library

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout

#-------------------------------------------------------------------------------------------------------------------------------------

#Define the test function class and unit tests

class TestSleepAnalysis(unittest.TestCase):

    def setUp(self):
        #Create / read in test data

        #create lists of test data for stats and cohen's functions
        self.stats_test_data = pd.DataFrame([1, 3, 4, 5, 3, 6, 8, 9, 10, 5, 4, 4, 3])
        self.cohen_test_1 = [1, 5, 5, 3, 5, 7, 8, 12, 32 ,17, 9]
        self.cohen_test_2 = [3, 21, 29, 4, 16, 12, 7, 4, 3, 2, 6, 7, 8]

        #read in csv sleep test input and output data
        TESTDATA_DIR = 'testdata'
        self.sleep_data_in = pd.read_csv(os.path.join(TESTDATA_DIR, 'sleep_test_data_in.csv'))
        self.sleep_data_out = pd.read_csv(os.path.join(TESTDATA_DIR, 'sleep_test_data_out.csv'))

        #read in csv activity test input and output data (two copies of input data needed, one for each time activity_processing function is called)
        self.activity_data_in = pd.read_csv(os.path.join(TESTDATA_DIR, 'activity_test_data_in.csv'))
        self.activity_data_out = pd.read_csv(os.path.join(TESTDATA_DIR, 'activity_test_data_out.csv'))

        #read in csv test output data
        self.flight_effect_data_out = pd.read_csv(os.path.join(TESTDATA_DIR, 'flight_effect_test_data_out.csv'))

    def tearDown(self):
        # tear stuff down here
        pass

    def test_basic_stats(self):
        '''This test determines if the basic_stats function correctly calculates and reports the statistics desired'''
        with HiddenPrints():
            my_mean, my_median, my_std, my_min, my_max = basic_stats(self.stats_test_data, label = 'test', decimals = DECIMALS)
        actual_stats = [my_mean.iloc[0], my_median.iloc[0], my_std.iloc[0], my_min.iloc[0], my_max.iloc[0]]
        expected_stats = [5, 4, 2.61, 1, 10]
        self.assertEqual(actual_stats, expected_stats)

    def test_cohens(self):
        '''This test determines that cohen's d is accurately calculated'''
        with HiddenPrints():
            eff_size, eff_string = cohend(self.cohen_test_1, self.cohen_test_2, DECIMALS)
        actual_effs = [eff_size, eff_string]
        expected_effs = [0.01, 'Effect size is trivial']
        self.assertEqual(actual_effs, expected_effs)

    def test_sleep_processing(self):
        '''This test makes sure that dates are parsed correctly, grouped correctly, and that the sume of hours slept per day is calculated
        from minutes correctly'''
        with HiddenPrints():
            sleep_sum_data = sleep_processing(self.sleep_data_in, DATE_STRING, DECIMALS)
        actual_sleep_days = sleep_sum_data['day'].tolist()
        expected_sleep_days = self.sleep_data_out['day'].tolist()
        actual_sleep_duration = sleep_sum_data['actual_hours'].tolist()
        expected_sleep_duration = self.sleep_data_out['actual_hours'].tolist()
        self.assertEqual(actual_sleep_days, expected_sleep_days)
        self.assertEqual(actual_sleep_duration, expected_sleep_duration)

    def test_activity_processing(self):
        '''This test makes sure that dates are parsed correctly, and activities are filtered correctly'''
        with HiddenPrints():
            flights = activity_processing(self.activity_data_in, DATE_STRING, DECIMALS)
        actual_flight_days = flights['day'].tolist()
        expected_flight_days = self.activity_data_out['day'].tolist()
        actual_flight_duration = flights['Duration'].tolist()
        expected_flight_duration = self.activity_data_out['Duration'].tolist()
        self.assertEqual(actual_flight_days, expected_flight_days)
        self.assertAlmostEqual(actual_flight_duration, expected_flight_duration)

    def test_flight_effect_sleep(self):
        ''''This test makes sure dates are categorized correctly'''
        with HiddenPrints():
            sleep_sum_data = sleep_processing(self.sleep_data_in, DATE_STRING, DECIMALS)
            flights = activity_processing(self.activity_data_in, DATE_STRING, DECIMALS)
            actual_flight_sleeps, actual_non_flight_sleeps = flight_effect_sleep(flights, sleep_sum_data, DECIMALS)
        actual_flight_sleeps = actual_flight_sleeps['sleep_duration'].tolist() 
        actual_non_flight_sleeps = actual_non_flight_sleeps['sleep_duration'].tolist()
        expected_flight_sleeps = self.flight_effect_data_out['flight_sleeps'].tolist()
        expected_non_flight_sleeps = self.flight_effect_data_out['non_flight_sleeps'].dropna()
        expected_non_flight_sleeps = expected_non_flight_sleeps.tolist()
        self.assertEqual(actual_flight_sleeps, expected_flight_sleeps)
        self.assertEqual(actual_non_flight_sleeps, expected_non_flight_sleeps)

#-------------------------------------------------------------------------------------------------------------------------------------

#Run the tests

if __name__ == '__main__':
    unittest.main()