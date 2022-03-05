from sleep_analysis_lib import read_data, sleep_processing, activity_processing, flight_effect_sleep, basic_stats, cohend, histogram
from multiprocessing import pool
from statistics import stdev
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

#Set constants
#Number of decimals to round to in reporting statisitics
Decimals = 2
#Which characters of a string to keep in order to isolate the date from time data
Date_string = 10
#Set bins for sleep duration histograms
Sleep_bins = np.arange(0, 20, 1)
#Set bins for flight duration histogram
Flight_bins = np.arange(0, 15, 1)

#Create help statements and arguments for the command line interface, call the functions
if __name__ == '__main__':
    #Add description of what the program does.
    parser = argparse.ArgumentParser(description='Analyze wearable data to determine airplane travel\'s effect on sleep. Takes two input CSV files as arguments, \'sleep_data_csv\' and \'activity_data_csv\'.')
    #Add argument for sleep data input file
    parser.add_argument('--sleep_data_csv', required=True,
                        help='sleep data from wearable with columns \'start_time_iso\' with GMT date and time of sleep starting and \'actual_minutes\' with sleep duration in minutes')
    #Add argument for activity data input dfile
    parser.add_argument('--activity_data_csv', required=True,
                        help='activity data from wearable with columns \'Start\' with GMT date and time of activity start, \'Duration\' with activity duration in seconds, \'Distance\' with distance travelled in miles, and \'Activity\' with activity type label ')
    #Create arguments
    args = parser.parse_args()
    #Read in the data
    sleep_data, activity_data = read_data(args.sleep_data_csv, args.activity_data_csv)
    #Process the sleep data, get stats, and show histogram
    sleep_sum_data = sleep_processing(sleep_data, Date_string, Decimals, Sleep_bins)
    #Process activity data
    flights = activity_processing(activity_data, Date_string, Decimals, Flight_bins)
    #Compare flight-effected sleeps vs non flight-effected sleeps
    flight_effect_sleep(flights, sleep_sum_data, Decimals, Sleep_bins)
    #Make it so that plots show
    plt.show()