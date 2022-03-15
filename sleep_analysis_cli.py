#This command line interface is meant to analyze airplane travel's affect on sleep duration using wearable device data using the 
#functions in sleep_analysis_lib.py. It is being completed as part of the Stanford class BIODS 253: Software Engineering 
#for Scientists by Stanford Bioengineering graduate student Scott Piper (sjpiper@stanford.edu) in Winter quarter 2022.
#The content from this program is inspired by a problem set from the Stanford class BIOE 217: Translational Bioinformatics.
#Data come from this research paper: Li, X., Dunn, J., Salins, D., Zhou, G., Zhou, W., Rose, S. M. S. F., ... & Sonecha, R. (2017). 
#Digital health: tracking physiomes and activity using wearable biosensors reveals useful health-related information. PLoS biology,
# 15(1), e2001402

#This program can be run from the command line interface and takes two input arguments. The first should be the csv file containing 
#the sleep data. The second should be the csvfile containing the activity data. To run the functions on the provided data, use 
#'python3 sleep_analysis_cli.py --sleep_data_csv sleep_to_03-31-16.csv --activity_data_csv activities.csv'. Run 
#'python3 sleep_analysis_cli.py -h' for more information.

#-------------------------------------------------------------------------------------------------------------------------------------

#Import necessary libraries and functions for the program

from time import sleep
from sleep_analysis_lib import read_data, sleep_processing, activity_processing, flight_effect_sleep, plot_data
import numpy as np
import matplotlib.pyplot as plt
import argparse

#-------------------------------------------------------------------------------------------------------------------------------------

#Set constants

#Number of decimals to round to in reporting statisitics
DECIMALS = 2
#Which characters of a string to keep in order to isolate the date from time data
DATE_STRING = 10
#Set bins for sleep duration histograms
sleep_bins = np.arange(0, 20, 1)
#Set bins for flight duration histogram
flight_bins = np.arange(0, 15, 1)

#-------------------------------------------------------------------------------------------------------------------------------------

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
    sleep_sum_data = sleep_processing(sleep_data, DATE_STRING, DECIMALS)
    #Process activity data
    flights = activity_processing(activity_data, DATE_STRING, DECIMALS)
    #Compare flight-effected sleeps vs non flight-effected sleeps
    flight_sleeps, non_flight_sleeps = flight_effect_sleep(flights, sleep_sum_data, DECIMALS)
    #Create plots
    plot_data(sleep_sum_data, flights, flight_sleeps, non_flight_sleeps, sleep_bins, flight_bins)