#This program is meant to analyze airline travel's affect on sleep duration using wearable device data. It 
#is being completed as created as part of the Stanford class BIODS 253: Software Engineering for Scientists 
#by Stanford Bioengineering graduate student Scott Piper (sjpiper@stanford.edu) in Winter quarter 2022.
#The content from this program is inspired by a problem set from the Stanford class BIOE 217: Translational Bioinformatics.
#Data come from this research paper: Li, X., Dunn, J., Salins, D., Zhou, G., Zhou, W., Rose, S. M. S. F., ... & Sonecha, R. (2017). 
#Digital health: tracking physiomes and activity using wearable biosensors reveals useful health-related information. PLoS biology,
# 15(1), e2001402

#This program takes two input arguments. The first should be the csv file containing the sleep data. The second should be the csv
#file containing the activity data. An example of the command line used to run the program is:
#python3 sleep_analysis.py sleep_data.csv activity_data.csv

#-------------------------------------------------------------------------------------------------------------------------------------

#import necessary libraries and functions for the program

import sys
import numpy as np
from numpy import mean
from numpy import var
import pandas as pd
import matplotlib.pyplot as plt
import warnings
from datetime import datetime as dt
from datetime import timedelta
from scipy import stats
from math import sqrt

#-------------------------------------------------------------------------------------------------------------------------------------

#Ignore future warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

#-------------------------------------------------------------------------------------------------------------------------------------

#create input data

#read in the sleep data
sleep_data = sys.argv[1]
sleep_data = pd.read_csv(sleep_data)


#read in the activity data
activity_data = sys.argv[2]
activity_data = pd.read_csv(activity_data) 

#-------------------------------------------------------------------------------------------------------------------------------------

#Section 1: sleep duration processing and analysis

#The data in this study was collected using a Basis Watch. Data from a basis watch includes local start and end times (local_start_time, 
#local_end_time) as well as timestamps (start_timestamp, end_timestamp) and GMT start and end times (start_time_iso, end_time_iso). 
#We want to use GMT start time to determine what day the sleep occurs on and actual_minutes to determine sleep duration. Outputs are a
#histogram of the total number of hours slept each day with a line showing the average, mean, median, standard deviation, and minimum and 
#maximum time slept.

#First, isolate the data we need for the histogram, just the start time and actual minutes
sleep_hist_data = sleep_data.loc[:, ['start_time_iso','actual_minutes']]

#The start_time_iso column contains the date as the first ten characters in a string in the format: YYYY-MM-DD
#Keep just the date of the start time string
date_string_length = 10
sleep_hist_data['day'] = sleep_hist_data['start_time_iso'].str[:date_string_length]

#On some days there are multiple sleeps. We want the total duration slept on each day.
#Use groupby to group the data by date and find the sum for each day of actual minutes of sleep.
sleep_sum_data = sleep_hist_data.groupby('day')['actual_minutes'].sum().reset_index(name ='actual_minutes')

#Convert the time to hours in a new column and drop the minutes column
min_in_hour = 60
decimals = 2
sleep_sum_data['actual_hours'] = sleep_sum_data['actual_minutes'].div(min_in_hour).round(decimals)
sleep_sum_data.drop(['actual_minutes'], axis = 1, inplace = True)

#plot histogram, average line, and label x axis
sleep_bins = np.arange(0, 20, 1)
fig1 = plt.figure()
ax1 = fig1.add_subplot(1, 1, 1)
sleep_hist = ax1.hist(sleep_sum_data['actual_hours'], bins = sleep_bins)
plt.title('Hours Slept Per Day')
plt.axvline(sleep_sum_data.actual_hours.mean(), color = 'r')
plt.xlabel('hours slept')
plt.ylabel('count')
plt.xticks(sleep_bins)
plt.draw()

#find mean
mean = sleep_sum_data['actual_hours'].mean()
print('mean daily sleep =', round(mean, decimals), 'hours')

#find median
median = sleep_sum_data['actual_hours'].median()
print('median daily sleep =', median, 'hours')

#find std
std = sleep_sum_data['actual_hours'].std()
print('standard deviation =', round(std, decimals), 'hours')

#find min
min = sleep_sum_data['actual_hours'].min()
print('minimum daily sleep =', min, 'hours')

#find max
max = sleep_sum_data['actual_hours'].max()
print('maximum daily sleep =', max, 'hours')

#-------------------------------------------------------------------------------------------------------------------------------------

#Section 2: flight duration processing and analysis

#In this section we isolate all of the flights from activities data. Outputs include the total number of flights and a histogram.

#As with a lot of wearable data, our labels are imperfect. Some flights are labeled `airplane` in the `Activity` column and others are 
#labelled `transport`. However, `transport` is also used for car rides, train rides, etc. We will define a flight as an activity that is 
#either (labeled `airplane`) OR (labeled `transport` AND has an average speed over 100 miles/hour). You can calculate speed from 
#`Duration` (given in seconds) and `Distance` (given in miles). Additionally, the fastest commercial flights run at around 660 mph. 
#Therefore, we also filter out activities that are over 700 mph to avoid any measurements that may have been errors. It is also likely
#that any very short duration activities tracked are errors. We get rid of any activities under 30 minutes.

#Keep just the date of the start string
activity_data['day'] = activity_data['Start'].str[:date_string_length]

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

#Remove activities in the speed range with durations under 30 minutes
lower_duration_threshold = 0.5
transport_flights = transport_flights.loc[transport_flights['Duration'] > lower_duration_threshold]

#Isolate activities with speeds over 100 mph labeled 'transport
transport_flights = transport_flights.loc[transport_flights['Activity'] == 'transport']

#Add the transport flights to the airplane flights, drop columns besides day and duration, and sort the columns by date
flights = flights.append(transport_flights)
flights = flights.loc[:, ['day','Duration']]
flights = flights.sort_values(by = 'day')
print('Participant 1 took' , len(flights), 'flights')

#plot histogram, average line, and label x axis
flight_bins = np.arange(0, 15, 1)
fig2 = plt.figure()
ax2 = fig2.add_subplot(1, 1, 1)
flight_histogram = ax2.hist(flights['Duration'], bins = flight_bins)
plt.axvline(flights.Duration.mean(), color = 'r')
plt.title('Flight Durations')
plt.xlabel('flight duration (hours)')
plt.ylabel('count')
plt.xticks(flight_bins)
plt.draw()

#-------------------------------------------------------------------------------------------------------------------------------------

# #Section 3: flight's affect on sleep

# #create new df of just the dates, drop the duplicates, and change to datetime objects
# flight_dates = flights['day']
# flight_dates = flight_dates.to_frame()
# flight_dates.columns = ['day']
# flight_dates = flight_dates.drop_duplicates()
# flight_dates['day'] = flight_dates['day'].astype('datetime64[ns]')

# #For every day in the df, add that day, the day after, and 2 days after to a list
# all_days = []
# for day in flight_dates['day']:
#     a = day
#     a = a.strftime('%Y-%m-%d')
#     b = day + timedelta(days = 1)
#     b = b.strftime('%Y-%m-%d')
#     c = day + timedelta(days = 2)
#     c = c.strftime('%Y-%m-%d')
#     all_days.append(a)
#     all_days.append(b)
#     all_days.append(c)

# #change list to df and drop duplicates, squeeze into series
# all_flight_days = pd.DataFrame(all_days, columns = ['all flight days'])
# all_flight_days = all_flight_days.drop_duplicates()
# all_flight_days = all_flight_days.squeeze()

# #initialize lists
# flight_sleeps = []
# non_flight_sleeps = []

# #go through each row in the sleep data
# for i, r in sleep_sum_data.iterrows():
#     #if the date from the sleep data is one affected by a flight, add sleep duration
#     #to corresponding list
#     if r['day'] in all_flight_days.unique():
#         flight_sleeps.append(r['actual_hours'])
#     #otherwise, add it to the other list
#     else:
#         non_flight_sleeps.append(r['actual_hours'])

# #convert lists to dfs
# flight_sleeps = pd.DataFrame(flight_sleeps, columns = ['sleep_duration'])
# non_flight_sleeps = pd.DataFrame(non_flight_sleeps, columns = ['sleep_duration'])

# #plot
# plt.hist(flight_sleeps, bins = np.arange(0, 20, 1), alpha = 0.5, label = 'flight_sleeps')
# plt.hist(non_flight_sleeps, bins = np.arange(0, 20, 1), alpha = 0.5, label = 'non_flight_sleeps')
# plt.xlabel('Hours Slept')
# plt.ylabel('Count')
# plt.legend()
# plt.axvline(flight_sleeps.sleep_duration.mean(), color = 'blue')
# plt.axvline(non_flight_sleeps.sleep_duration.mean(), color = 'orange')
# plt.xticks(np.arange(0, 20, 1))
# plt.show()

# #perform ttest
# res = stats.ttest_ind(flight_sleeps, non_flight_sleeps)
# display(res)

# # function to calculate Cohen's d for independent samples
# def cohend(d1, d2):
#     # calculate the size of samples
#     n1, n2 = len(d1), len(d2)
#     # calculate the variance of the samples
#     s1, s2 = var(d1, ddof=1), var(d2, ddof=1)
#     # calculate the pooled standard deviation
#     s = sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
#     # calculate the means of the samples
#     u1, u2 = mean(d1), mean(d2)
#     # calculate the effect size
#     return (u1 - u2) / s

# #calculate
# d = cohend(flight_sleeps, non_flight_sleeps)
# print('Cohen\'s d: %.3f' % d)

#-------------------------------------------------------------------------------------------------------------------------------------

#Make it so that plots show
plt.show()