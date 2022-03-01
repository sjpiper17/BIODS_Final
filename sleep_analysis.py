#This program is meant to analyze airline travel's affect on sleep duration using wearable device data. It 
#is being completed as created as part of the Stanford class BIODS 253: Software Engineering for Scientists 
#by Stanford Bioengineering graduate student Scott Piper (sjpiper@stanford.edu) in Winter quarter 2022.
#The content from this program is inspired by a problem set from the Stanford class BIOE 217: Translational Bioinformatics.
#Data come from this research paper: Li, X., Dunn, J., Salins, D., Zhou, G., Zhou, W., Rose, S. M. S. F., ... & Sonecha, R. (2017). 
#Digital health: tracking physiomes and activity using wearable biosensors reveals useful health-related information. PLoS biology,
# 15(1), e2001402

#This program takes two input arguments. The first should be the csv file containing the sleep data. The second should be the csv
#file containing the activity data. Run 'python3 sleep_analysis.py -h' for more information.
#-------------------------------------------------------------------------------------------------------------------------------------

#import necessary libraries and functions for the program

import sys
import numpy as np
from numpy import mean
from numpy import var
import pandas as pd
import matplotlib.pyplot as plt
import warnings
import argparse
from datetime import datetime as dt
from datetime import timedelta
from scipy import stats
from math import sqrt

#-------------------------------------------------------------------------------------------------------------------------------------

#Create help statements and arguments for the command line interface

#if name = main

#Add description of what the program does.
parser = argparse.ArgumentParser(description='Analyze wearable data to determine airplane travel\'s effect on sleep. Takes two input CSV files as arguments, \'sleep_data_csv\' and \'activity_data_csv\'.')

#Add argument for sleep data input file
parser.add_argument('--sleep_data_csv', required = True,
                    help='sleep data from wearable with column \'start_time_iso\' with GMT date and time of sleep starting and \'actual_minutes\' with sleep duration in minutes')

#Add argument for activity data input file
parser.add_argument('--activity_data_csv', required = True,
                    help='activity data from wearable with columns \'Start\' with GMT date and time of activity start, \'Duration\' with activity duration in seconds, \'Distance\' with distance travelled in miles, and \'Activity\' with activity type label ')

#Create arguments
args = parser.parse_args()

#-------------------------------------------------------------------------------------------------------------------------------------

#Define a function to read in data from the command line

def read_data(sleep_data_in, activity_data_in):
    
    #make output data variables global to be accessible by subsequent functions
    global sleep_data
    global activity_data

    #read in the sleep data
    sleep_data = pd.read_csv(sleep_data_in)

    #read in the activity data
    activity_data = pd.read_csv(activity_data_in)

#-------------------------------------------------------------------------------------------------------------------------------------

#Define a function to calculate the basic statistics of a dataset. 'data' argument should be a single column of a dataframe or a list
#and contain the data for which you want the statistics. 'label' argument contains the label you want to be printed with the 
#statistics. 'decimals' is the number of decimals you want answers rounded to.

def basic_stats(data, label, decimals):
    #find mean
    mean = data.mean()
    print('mean', label, '=', round(mean, decimals), 'hours')

    #find median
    median = data.median()
    print('median', label, '=', round(median, decimals), 'hours')

    #find std
    std = data.std()
    print('standard deviation', label, '=', round(std, decimals), 'hours')

    #find min
    min = data.min()
    print('minimum', label, '=', round(min, decimals), 'hours')

    #find max
    max = data.max()
    print('maximum', label, '=', round(max, decimals), 'hours')

#-------------------------------------------------------------------------------------------------------------------------------------

#Define a function to draw a histogram

def histogram(subplot, data, bins, title, xlabel):
    hist = subplot.hist(data, bins = bins)
    plt.title(title)
    plt.axvline(data.mean(), color = 'r')
    plt.xlabel(xlabel)
    plt.ylabel('count')
    plt.xticks(bins)
    plt.draw()

#-------------------------------------------------------------------------------------------------------------------------------------

#Section 1: sleep duration processing and analysis

#The data in this study was collected using a Basis Watch. Data from a basis watch includes local start and end times (local_start_time, 
#local_end_time) as well as timestamps (start_timestamp, end_timestamp) and GMT start and end times (start_time_iso, end_time_iso). 
#We want to use GMT start time to determine what day the sleep occurs on and actual_minutes to determine sleep duration. Outputs are a
#histogram of the total number of hours slept each day with a line showing the average, mean, median, standard deviation, and minimum and 
#maximum time slept.

def sleep_processing(sleep_data):

    #First, isolate the data we need for the histogram, just the start time and actual minutes
    sleep_hist_data = sleep_data.loc[:, ['start_time_iso','actual_minutes']]

    #The start_time_iso column contains the date as the first ten characters in a string in the format: YYYY-MM-DD
    #Keep just the date of the start time string
    sleep_hist_data['day'] = sleep_hist_data['start_time_iso'].str[:date_string]

    #On some days there are multiple sleeps. We want the total duration slept on each day.
    #Use groupby to group the data by date and find the sum for each day of actual minutes of sleep.
    sleep_sum_data = sleep_hist_data.groupby('day')['actual_minutes'].sum().reset_index(name ='actual_minutes')

    #Convert the time to hours in a new column and drop the minutes column
    min_in_hour = 60
    sleep_sum_data['actual_hours'] = sleep_sum_data['actual_minutes'].div(min_in_hour).round(decimals)
    sleep_sum_data.drop(['actual_minutes'], axis = 1, inplace = True)

    #Create bins and a subplot, then call the histogram function
    sleep_bins = np.arange(0, 20, 1)
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(1, 1, 1)
    histogram(subplot = ax1, data = sleep_sum_data['actual_hours'], bins = sleep_bins, title = 'Hours Slept Per Day', xlabel = 'hours slept')

    #Run the basic stats function on the sleep data.
    basic_stats(sleep_sum_data['actual_hours'], 'daily sleep', decimals)

#-------------------------------------------------------------------------------------------------------------------------------------

#Section 2: flight duration processing and analysis

#In this section we isolate all of the flights from activities data. Outputs include the total number of flights and a histogram.

#As with a lot of wearable data, our labels are imperfect. Some flights are labeled `airplane` in the `Activity` column and others are 
#labelled `transport`. However, `transport` is also used for car rides, train rides, etc. We will define a flight as an activity that is 
#either (labeled `airplane`) OR (labeled `transport` AND has an average speed over 100 miles/hour). You can calculate speed from 
#`Duration` (given in seconds) and `Distance` (given in miles). Additionally, the fastest commercial flights run at around 660 mph. 
#Therefore, we also filter out activities that are over 700 mph to avoid any measurements that may have been errors. It is also likely
#that any very short duration activities tracked are errors. We get rid of any activities under 30 minutes.

def activity_processing(activity_data):

    #Keep just the date of the start string
    activity_data['day'] = activity_data['Start'].str[:date_string]

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
    flight_bins = np.arange(0, 15, 1)
    fig2 = plt.figure()
    ax2 = fig2.add_subplot(1, 1, 1)
    histogram(subplot = ax2, data = flights['Duration'], bins = flight_bins, title = 'Flight Durations', xlabel = 'flight duration (hours)')

    #Run the basic stats function on the flight data.
    basic_stats(flights['Duration'], 'flight duration', decimals)

# #-------------------------------------------------------------------------------------------------------------------------------------

# #Section 3: flight's affect on sleep

# #Now we know when the participant travelled and when they slept. Let’s put them together. We want to compare the participant's sleep 
# #after travelling to their usual sleep. generate a set of dates within 3 days of flight. That is, if they travelled on 3/23/14, then 
# #you should include 3/23/14, 3/24/14, and 3/25/14 as "after-flight" dates. We will make a histogram, run a t-test, and calculate
# #cohen's d to compare the amount of sleep on a normal night vs an "after-flight" night.

# #Create new dataframe of just the flight dates and drop any duplicates.
# flight_dates = flights['day']
# flight_dates = flight_dates.to_frame()
# flight_dates.columns = ['day']
# flight_dates = flight_dates.drop_duplicates()

# #Convert the values in the dataframe to datetime objects.
# flight_dates['day'] = flight_dates['day'].astype('datetime64[ns]')

# #Now we need to make the list of all after-flight days. We will create an empty list. Then, using a for loop, we will go through each
# #day in the flight_dates dataframe and add one and two days using the timedelta function. Each of those days is converted back to a
# #string and added to the list.
# all_flight_days = []
# for day in flight_dates['day']:
#     for offset in range(3):
#         a = day + timedelta(days = offset)
#         all_flight_days.append(a.strftime('%Y-%m-%d'))
#     # a = day
#     # a = a.strftime('%Y-%m-%d')
#     # b = day + timedelta(days = 1)
#     # b = b.strftime('%Y-%m-%d')
#     # c = day + timedelta(days = 2)
#     # c = c.strftime('%Y-%m-%d')
#     # all_flight_days.append(a)
#     # all_flight_days.append(b)
#     # all_flight_days.append(c)

# #Change the list to a dataframe and drop duplicates. Then squeeze it into a series.
# all_flight_days = pd.DataFrame(all_flight_days, columns = ['all flight days'])
# all_flight_days = all_flight_days.drop_duplicates()
# all_flight_days = all_flight_days.squeeze()

# # #initialize lists
# # flight_sleeps = []
# # non_flight_sleeps = []

# # #go through each row in the sleep data
# # for i, r in sleep_sum_data.iterrows():
# #     #if the date from the sleep data is one affected by a flight, add sleep duration
# #     #to corresponding list
# #     if r['day'] in all_flight_days.unique():
# #         flight_sleeps.append(r['actual_hours'])
# #     #otherwise, add it to the other list
# #     else:
# #         non_flight_sleeps.append(r['actual_hours'])

# # #convert lists to dfs
# # flight_sleeps = pd.DataFrame(flight_sleeps, columns = ['sleep_duration'])
# # non_flight_sleeps = pd.DataFrame(non_flight_sleeps, columns = ['sleep_duration'])

# # #plot
# # plt.hist(flight_sleeps, bins = np.arange(0, 20, 1), alpha = 0.5, label = 'flight_sleeps')
# # plt.hist(non_flight_sleeps, bins = np.arange(0, 20, 1), alpha = 0.5, label = 'non_flight_sleeps')
# # plt.xlabel('Hours Slept')
# # plt.ylabel('Count')
# # plt.legend()
# # plt.axvline(flight_sleeps.sleep_duration.mean(), color = 'blue')
# # plt.axvline(non_flight_sleeps.sleep_duration.mean(), color = 'orange')
# # plt.xticks(np.arange(0, 20, 1))
# # plt.show()

# # #perform ttest
# # res = stats.ttest_ind(flight_sleeps, non_flight_sleeps)
# # display(res)

# # # function to calculate Cohen's d for independent samples
# # def cohend(d1, d2):
# #     # calculate the size of samples
# #     n1, n2 = len(d1), len(d2)
# #     # calculate the variance of the samples
# #     s1, s2 = var(d1, ddof=1), var(d2, ddof=1)
# #     # calculate the pooled standard deviation
# #     s = sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
# #     # calculate the means of the samples
# #     u1, u2 = mean(d1), mean(d2)
# #     # calculate the effect size
# #     return (u1 - u2) / s

# # #calculate
# # d = cohend(flight_sleeps, non_flight_sleeps)
# # print('Cohen\'s d: %.3f' % d)

#-------------------------------------------------------------------------------------------------------------------------------------

#Set constants

#Number of decimals to round to in reporting statisitics
decimals = 2

#Which characters of a string to keep in order to isolate the date from time data
date_string = 10

#-------------------------------------------------------------------------------------------------------------------------------------

#Call the functions

read_data(args.sleep_data_csv, args.activity_data_csv)
sleep_processing(sleep_data)
activity_processing(activity_data)

#Make it so that plots show
plt.show()