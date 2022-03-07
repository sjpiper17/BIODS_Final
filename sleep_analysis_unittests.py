#This collection of unit tests is meant to test the functions in sleep_analysis_lib.py. It 
#is being completed as created as part of the Stanford class BIODS 253: Software Engineering for Scientists 
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

from sleep_analysis_lib import basic_stats, cohend, sleep_processing, activity_processing, flight_effect_sleep
import unittest
import numpy as np
import pandas as pd

#-------------------------------------------------------------------------------------------------------------------------------------

#Set constants

#Number of decimals to round to in reporting statisitics
Decimals = 2
#Which characters of a string to keep in order to isolate the date from time data
Date_string = 10
#Set bins for sleep duration histograms
Sleep_bins = np.arange(0, 20, 1)
#Set bins for flight duration histogram
Flight_bins = np.arange(0, 15, 1)


#-------------------------------------------------------------------------------------------------------------------------------------

#create test data

#create lists of test data for stats and cohen's functions
stats_test_data = pd.DataFrame([1, 3, 4, 5, 3, 6, 8, 9, 10, 5, 4, 4, 3])
cohen_test_1 = [1, 5, 5, 3, 5, 7, 8, 12, 32 ,17, 9]
cohen_test_2 = [3, 21, 29, 4, 16, 12, 7, 4, 3, 2, 6, 7, 8]

#read in csv sleep test input and output data
sleep_data_in = pd.read_csv('sleep_test_data_in.csv')
sleep_data_out = pd.read_csv('sleep_test_data_out.csv')

#read in csv activity test input and output data (two copies of input data needed, one for each time activity_processing function is called)
activity_data_in = pd.read_csv('activity_test_data_in.csv')
activity_data_in_1 = pd.read_csv('activity_test_data_in.csv')
activity_data_out = pd.read_csv('activity_test_data_out.csv')

#read in csv test output data
flight_efffect_data_out = pd.read_csv('flight_effect_test_data_out.csv')

#-------------------------------------------------------------------------------------------------------------------------------------

#Define the test function class and unit tests

class TestSleepAnalysis(unittest.TestCase):

    def setUp(self):
        # set stuff up here
        pass

    def tearDown(self):
        # tear stuff down here
        pass

    def test_basic_stats(self):
        '''This test determines if the basic_stats function correctly calculates and reports the statistics desired'''
        my_mean, my_median, my_std, my_min, my_max = basic_stats(stats_test_data, label = 'test', Decimals = Decimals)
        actual_stats = [my_mean.iloc[0], my_median.iloc[0], my_std.iloc[0], my_min.iloc[0], my_max.iloc[0]]
        expected_stats = [5, 4, 2.61, 1, 10]
        self.assertEqual(actual_stats, expected_stats)
        print('pass basic stats test')

    def test_cohens(self):
        '''This test determines that cohen's d is accurately calculated'''
        eff_size, eff_string = cohend(cohen_test_1, cohen_test_2, Decimals)
        actual_effs = [eff_size, eff_string]
        expected_effs = [0.01, 'Effect size is trivial']
        self.assertEqual(actual_effs, expected_effs)
        print('pass cohen\'s d test')

    def test_sleep_processing(self):
        '''This test makes sure that dates are parsed correctly, grouped correctly, and that the sume of hours slept per day is calculated
        from minutes correctly'''
        sleep_sum_data = sleep_processing(sleep_data_in, Date_string, Decimals, Sleep_bins)
        actual_sleep_days = sleep_sum_data['day'].tolist()
        expected_sleep_days = sleep_data_out['day'].tolist()
        actual_sleep_duration = sleep_sum_data['actual_hours'].tolist()
        expected_sleep_duration = sleep_data_out['actual_hours'].tolist()
        self.assertEqual(actual_sleep_days, expected_sleep_days)
        self.assertEqual(actual_sleep_duration, expected_sleep_duration)
        print('pass sleep processing test')

    def test_activity_processing(self):
        '''This test makes sure that dates are parsed correctly, and activities are filtered correctly'''
        flights = activity_processing(activity_data_in, Date_string, Decimals, Flight_bins)
        actual_flight_days = flights['day'].tolist()
        expected_flight_days = activity_data_out['day'].tolist()
        actual_flight_duration = flights['Duration'].tolist()
        expected_flight_duration = activity_data_out['Duration'].tolist()
        self.assertEqual(actual_flight_days, expected_flight_days)
        self.assertAlmostEqual(actual_flight_duration, expected_flight_duration)
        print('pass activity processing test')

    def test_flight_effect_sleep(self):
        ''''This test make sure dates are categorized correctly'''
        sleep_sum_data = sleep_processing(sleep_data_in, Date_string, Decimals, Sleep_bins)
        flights = activity_processing(activity_data_in_1, Date_string, Decimals, Flight_bins)
        actual_flight_sleeps, actual_non_flight_sleeps = flight_effect_sleep(flights, sleep_sum_data, Decimals, Sleep_bins)
        actual_flight_sleeps = actual_flight_sleeps['sleep_duration'].tolist() 
        actual_non_flight_sleeps = actual_non_flight_sleeps['sleep_duration'].tolist()
        expected_flight_sleeps = flight_efffect_data_out['flight_sleeps'].tolist()
        expected_non_flight_sleeps = flight_efffect_data_out['non_flight_sleeps'].dropna()
        expected_non_flight_sleeps = expected_non_flight_sleeps.tolist()
        self.assertEqual(actual_flight_sleeps, expected_flight_sleeps)
        self.assertEqual(actual_non_flight_sleeps, expected_non_flight_sleeps)
        print('pass flight effect test')

#-------------------------------------------------------------------------------------------------------------------------------------

#Run the tests

if __name__ == '__main__':
    unittest.main()