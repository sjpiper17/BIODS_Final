#This library is meant to analyze airline travel's affect on sleep duration using wearable device data. It 
#is being completed as created as part of the Stanford class BIODS 253: Software Engineering for Scientists 
#by Stanford Bioengineering graduate student Scott Piper (sjpiper@stanford.edu) in Winter quarter 2022.
#The content from this program is inspired by a problem set from the Stanford class BIOE 217: Translational Bioinformatics.
#Data come from this research paper: Li, X., Dunn, J., Salins, D., Zhou, G., Zhou, W., Rose, S. M. S. F., ... & Sonecha, R. (2017). 
#Digital health: tracking physiomes and activity using wearable biosensors reveals useful health-related information. PLoS biology,
# 15(1), e2001402

#This program can be run from the command line interface and takes two input arguments. The first should be the csv file containing
#the sleep data. The second should be the csv file containing the activity data. Run 'python3 sleep_analysis_cli.py -h' for more 
#information.

#-------------------------------------------------------------------------------------------------------------------------------------

#Import necessary libraries and functions for the program

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

#-------------------------------------------------------------------------------------------------------------------------------------

#Section 0: Define necessary support functions to be used with the main analysis functions in the following sections. These include
#reading in the data, calculating basic stats, plotting a histogram, and calculating cohen's d.

def read_data(sleep_data_in, activity_data_in):
    '''Define a function to read in data from the command line. '''
    #make output data variables global to be accessible by subsequent functions
    # global sleep_data
    # global activity_data
    #read in the sleep data
    sleep_data = pd.read_csv(sleep_data_in)
    #read in the activity data
    activity_data = pd.read_csv(activity_data_in)
    return sleep_data, activity_data

def basic_stats(data, label, Decimals):
    '''Define a function to calculate the basic statistics of a dataset. 'data' argument should be a single column of a dataframe or a list
    and contain the data for which you want the statistics. 'label' argument contains the label you want to be printed with the 
    statistics. 'decimals' is the number of decimals you want answers rounded to.'''
    #find mean
    my_mean = round(data.mean(), Decimals)
    print('mean', label, '=', my_mean , 'hours')
    #find median
    my_median = round(data.median(), Decimals)
    print('median', label, '=', my_median, 'hours')
    #find std
    my_std = round(data.std(), Decimals)
    print('standard deviation', label, '=', my_std, 'hours')
    #find min
    my_min = round(data.min(), Decimals)
    print('minimum', label, '=', my_min, 'hours')
    #find max
    my_max = round(data.max(), Decimals)
    print('maximum', label, '=', my_max, 'hours')
    return my_mean, my_median, my_std, my_min, my_max

def histogram(subplot, data, bins, title='', xlabel='', alpha=1, color='r', label=''):
    '''Define a function to draw a histogram'''
    #plot histogram
    hist = subplot.hist(data, bins=bins, alpha=alpha, label=label)
    #add title, axis labels, and x ticks
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel('count')
    plt.xticks(bins)
    #add mean line
    plt.axvline(data.mean(), color = color)
    #silence warning for if no legend is required, add a legend if there are labels
    logging.getLogger().setLevel(logging.CRITICAL)
    plt.legend()
    #draw
    plt.draw()

def cohend(d1, d2, Decimals):
    '''Define a function to calculate Cohen's d for independent samples'''
    #calculate the size of samples
    n1, n2 = len(d1), len(d2)
    #calculate the variance of the samples
    s1, s2 = var(d1, ddof=1), var(d2, ddof=1)
    #calculate the pooled standard deviation
    s = sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
    #calculate the means of the samples
    u1, u2 = mean(d1, axis = 0), mean(d2, axis = 0)
    #calculate the effect size
    eff_size = round(pd.to_numeric((u1 - u2) / s), Decimals)
    abs_eff_size = abs(eff_size)
    print('Cohen\'s d =', eff_size)
    #determine magnitude of effect size
    if abs_eff_size < 0.2:
        eff_string = 'Effect size is trivial'
        print(eff_string)
    elif abs_eff_size >= 0.2 and eff_size < 0.5:
        eff_string = 'Effect size is small'
        print(eff_string)
    elif abs_eff_size >= 0.5 and eff_size < 0.8:
        eff_string = 'Effect size is medium'
        print(eff_string)
    elif abs_eff_size >= 0.8:
        eff_string = 'Effect size is large'
        print(eff_string)
    return eff_size, eff_string   

#-------------------------------------------------------------------------------------------------------------------------------------

#Section 1: sleep duration processing and analysis

def sleep_processing(sleep_data, Date_string, Decimals, Sleep_bins):
    '''The data in this study was collected using a Basis Watch. Data from a basis watch includes local start and end times (local_start_time, 
    local_end_time) as well as timestamps (start_timestamp, end_timestamp) and GMT start and end times (start_time_iso, end_time_iso). 
    We want to use GMT start time to determine what day the sleep occurs on and actual_minutes to determine sleep duration. Outputs are a
    histogram of the total number of hours slept each day with a line showing the average, the mean, median, standard deviation, and minimum and 
    maximum time slept.'''
    #Make output global
    # global sleep_sum_data
    #First, isolate the data we need for the histogram, just the start time and actual minutes
    sleep_hist_data = sleep_data.loc[:, ['start_time_iso','actual_minutes']]
    #The start_time_iso column contains the date as the first ten characters in a string in the format: YYYY-MM-DD
    #Keep just the date of the start time string
    sleep_hist_data['day'] = sleep_hist_data['start_time_iso'].str[:Date_string]
    #On some days there are multiple sleeps. We want the total duration slept on each day.
    #Use groupby to group the data by date and find the sum for each day of actual minutes of sleep.
    sleep_sum_data = sleep_hist_data.groupby('day')['actual_minutes'].sum().reset_index(name ='actual_minutes')
    #Convert the time to hours in a new column and drop the minutes column
    min_in_hour = 60
    sleep_sum_data['actual_hours'] = sleep_sum_data['actual_minutes'].div(min_in_hour).round(Decimals)
    sleep_sum_data.drop(['actual_minutes'], axis=1, inplace=True)
    #Create bins and a subplot, then call the histogram function
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(1, 1, 1)
    histogram(subplot=ax1, data=sleep_sum_data['actual_hours'], bins=Sleep_bins, title='Hours Slept Per Day', xlabel='hours slept')
    #Run the basic stats function on the sleep data
    basic_stats(sleep_sum_data['actual_hours'], 'daily sleep', Decimals)
    return sleep_sum_data

#-------------------------------------------------------------------------------------------------------------------------------------

#Section 2: flight duration processing and analysis

def activity_processing(activity_data, Date_string, Decimals, Flight_bins):
    '''In this section we isolate all of the flights from activities data. Outputs include the total number of flights, a histogram, and the
    basic stats. As with a lot of wearable data, our labels are imperfect. Some flights are labeled `airplane` in the `Activity` column and 
    others are labelled `transport`. However, `transport` is also used for car rides, train rides, etc. We will define a flight as an activity
    that is either (labeled `airplane`) OR (labeled `transport` AND has an average speed over 100 miles/hour). You can calculate speed from 
    `Duration` (given in seconds) and `Distance` (given in miles). Additionally, the fastest commercial flights run at around 660 mph. 
    Therefore, we also filter out activities that are over 700 mph to avoid any measurements that may have been errors. It is also likely
    that any very short duration activities tracked are errors. We get rid of any activities that fall in our speed range under 30 minutes.'''
    #Make output global
    # global flights
    #Keep just the date of the start string
    activity_data['day'] = activity_data['Start'].str[:Date_string]
    #The duration of the activity is given in seconds. Convert duration to hours
    seconds_in_hour = 3600
    activity_data['Duration'] = activity_data['Duration'].div(seconds_in_hour)
    #First, separate out the activities with the 'airplane' label
    flights = activity_data.loc[activity_data['Activity'] == 'airplane']
    #Calculate the speed of all the activities
    activity_data['speed'] = activity_data['Distance'] / activity_data['Duration']
    #Isolate activites with speeds over 100 mph and under 700 mph
    lower_speed_threshold = 100
    transport_flights = activity_data.loc[activity_data['speed'] > lower_speed_threshold]
    upper_speed_threshold = 700
    transport_flights = transport_flights.loc[transport_flights['speed'] < upper_speed_threshold]
    #Isolate activities with speeds in the target range labeled 'transport
    transport_flights = transport_flights.loc[transport_flights['Activity'] == 'transport']
    #Add the transport flights to the airplane flights, drop columns besides day and duration, and sort the columns by date.
    flights = pd.concat([flights, transport_flights], axis = 0)
    flights = flights.loc[:, ['day','Duration']]
    flights = flights.sort_values(by = 'day')
    #Remove flights with durations under 30 minutes
    lower_duration_threshold = 0.5
    flights = flights.loc[flights['Duration'] > lower_duration_threshold]
    #Print the total number of flights
    print('participant took' , len(flights), 'flights')
    #Create bins and a subplot, then call the histogram function
    fig2 = plt.figure()
    ax2 = fig2.add_subplot(1, 1, 1)
    histogram(subplot=ax2, data=flights['Duration'], bins=Flight_bins, title='Flight Durations', xlabel='flight duration (hours)')
    #Run the basic stats function on the flight data
    basic_stats(flights['Duration'], 'flight duration', Decimals)
    return flights

#-------------------------------------------------------------------------------------------------------------------------------------

#Section 3: flight's affect on sleep

def flight_effect_sleep(flights, sleep_sum_data, Decimals, Sleep_bins):
    ''' Now we know when the participant travelled and how long they slept each day. Let’s put them together. We want to compare the participant's sleep 
    after travelling to their usual sleep. Generate a set of dates within 3 days of flight. That is, if they travelled on 3/23/14, then 
    you should include 3/23/14, 3/24/14, and 3/25/14 as "after-flight" dates. We will make a histogram, run a t-test, and calculate
    cohen's d to compare the amount of sleep on a normal night vs an "after-flight" night. '''
    #Create new dataframe of just the flight dates and drop any duplicates.
    flight_dates = flights['day']
    flight_dates = flight_dates.to_frame()
    flight_dates.columns = ['day']
    flight_dates = flight_dates.drop_duplicates()
    #Convert the values in the dataframe to datetime objects.
    flight_dates['day'] = flight_dates['day'].astype('datetime64[ns]')
    #Now we need to make the list of all after-flight days. We will create an empty list. Then, using nested for loops, we will
    #add the days of and following a flight to the list of after-flight days.
    all_flight_days = []
    days_affected_by_flight = 3
    for day in flight_dates['day']:
        for offset in range(days_affected_by_flight):
            a = day + timedelta(days = offset)
            all_flight_days.append(a.strftime('%Y-%m-%d'))
    #Change the list to a dataframe and drop duplicates. Then squeeze it into a series.
    all_flight_days = pd.DataFrame(all_flight_days, columns = ['all flight days'])
    all_flight_days = all_flight_days.drop_duplicates()
    all_flight_days = all_flight_days.squeeze()
    #initialize lists
    flight_sleeps = []
    non_flight_sleeps = []
    #Go through each row in the sleep data. If the date from the sleep data is one affected by a flight, add sleep duration
    #to corresponding list. Otherwise, add it to the other list.
    for i, r in sleep_sum_data.iterrows():
        if r['day'] in all_flight_days.unique():
            flight_sleeps.append(r['actual_hours'])
        else:
            non_flight_sleeps.append(r['actual_hours'])
    #convert lists to dfs
    flight_sleeps = pd.DataFrame(flight_sleeps, columns = ['sleep_duration'])
    non_flight_sleeps = pd.DataFrame(non_flight_sleeps, columns = ['sleep_duration'])
    #plot both sets of sleep durations on the same histogram
    fig3 = plt.figure()
    ax3 = fig3.add_subplot(1, 1, 1)
    histogram(subplot=ax3, data=flight_sleeps['sleep_duration'], bins=Sleep_bins, alpha=0.5, color='blue', label='flight sleeps')
    histogram(subplot=ax3, data=non_flight_sleeps['sleep_duration'], bins=Sleep_bins, title='Flight VS Non-Flight Sleeps', xlabel='hours slept', alpha=0.5, color='orange', label='non-flight sleeps')
    #perform ttest
    res = stats.ttest_ind(flight_sleeps, non_flight_sleeps)
    display(res)
    #calculate cohen's d
    cohend(flight_sleeps['sleep_duration'], non_flight_sleeps['sleep_duration'], Decimals)

#-------------------------------------------------------------------------------------------------------------------------------------

# #Set constants
# #Number of decimals to round to in reporting statisitics
# Decimals = 2
# #Which characters of a string to keep in order to isolate the date from time data
# Date_string = 10
# #Set bins for sleep duration histograms
# Sleep_bins = np.arange(0, 20, 1)
# #Set bins for flight duration histogram
# Flight_bins = np.arange(0, 15, 1)

#-------------------------------------------------------------------------------------------------------------------------------------

#Create help statements and arguments for the command line interface, call the functions
# if __name__ == '__main__':
#     #Add description of what the program does.
#     parser = argparse.ArgumentParser(description='Analyze wearable data to determine airplane travel\'s effect on sleep. Takes two input CSV files as arguments, \'sleep_data_csv\' and \'activity_data_csv\'.')
#     #Add argument for sleep data input file
#     parser.add_argument('--sleep_data_csv', required=True,
#                         help='sleep data from wearable with columns \'start_time_iso\' with GMT date and time of sleep starting and \'actual_minutes\' with sleep duration in minutes')
#     #Add argument for activity data input file
#     parser.add_argument('--activity_data_csv', required=True,
#                         help='activity data from wearable with columns \'Start\' with GMT date and time of activity start, \'Duration\' with activity duration in seconds, \'Distance\' with distance travelled in miles, and \'Activity\' with activity type label ')
#     #Create arguments
#     args = parser.parse_args()
#     #Read in the data
#     read_data(args.sleep_data_csv, args.activity_data_csv)
#     #Process the sleep data, get stats, and show histogram
#     sleep_processing(sleep_data)
#     #Process activity data
#     activity_processing(activity_data)
#     #Compare flight-effected sleeps vs non flight-effected sleeps
#     flight_effect_sleep(flights, sleep_sum_data)
#     #Make it so that plots show
#     plt.show()