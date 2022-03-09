#This library is meant to analyze airplane travel's effect on sleep duration using wearable device data. It 
#is being completed as part of the Stanford class BIODS 253: Software Engineering for Scientists 
#by Stanford Bioengineering graduate student Scott Piper (sjpiper@stanford.edu) in Winter quarter 2022.
#The content from this program is inspired by a problem set from the Stanford class BIOE 217: Translational Bioinformatics.
#Data comes from this research paper: Li, X., Dunn, J., Salins, D., Zhou, G., Zhou, W., Rose, S. M. S. F., ... & Sonecha, R. (2017). 
#Digital health: tracking physiomes and activity using wearable biosensors reveals useful health-related information. PLoS biology,
# 15(1), e2001402

#This program can be run from the command line interface and takes two input arguments. The first should be the csv file containing 
#the sleep data. The second should be the csvfile containing the activity data. To run the functions on the provided data, use 
#'python3 sleep_analysis_cli.py --sleep_data_csv sleep_to_03-31-16.csv --activity_data_csv activities.csv'. Run 
#'python3 sleep_analysis_cli.py -h' for more information.

#-------------------------------------------------------------------------------------------------------------------------------------

#Import necessary libraries and functions for the program

from numpy import mean
from numpy import var
import pandas as pd
import matplotlib.pyplot as plt
import logging
from datetime import timedelta
from scipy import stats
from math import sqrt
from IPython.display import display

#-------------------------------------------------------------------------------------------------------------------------------------

#Section 0: Define necessary support functions to be used with the main analysis functions in the following sections. These include
#reading in the data, calculating basic stats, plotting a histogram, and calculating cohen's d.

def read_data(sleep_data_in, activity_data_in):
    '''Reads input data from a csv into python.
    
    Arguments:
    sleep_data_in = a csv file with columns start_time_iso with GMT time and actual_minutes with sleep duration in minutes
    activity_data_in = a csv file with columns Start with GMT time, Duration with activity duration in seconds, Distance with activity distance in miles, and Activity with activity label
    
    Returns:
    sleep_data = a pandas dataframe of the sleep_data_in csv file
    activity_data = a pandas dataframe of the activity_data_in csv file'''
    #read in the sleep data
    sleep_data = pd.read_csv(sleep_data_in)
    #read in the activity data
    activity_data = pd.read_csv(activity_data_in)
    return sleep_data, activity_data

def basic_stats(data, label, Decimals):
    '''Calculates the basic statistics of a dataset.
    
    Arguments:
    data = a single column of a dataframe or a list with the data for which you want the statistics
    label = the label you want to be printed with the statistics, string
    Decimals = the number of decimals you want answers rounded to, integer
    
    Returns:
    my_mean = the mean of the data
    my_median = the median of the data
    my_std = the standard deviation of the data
    my_min = the minimum of the data
    my_max = the maximum of the data
    Prints each stat with a label'''
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
    '''Draws and annotates a histogram with a line at the mean
    
    Arguments:
    subplot = subplot in which to draw the histogram, a plt.figure subplot
    data = data to be plotted, a single column of a dataframe
    bins = bins to be used for plotting the data, a numpy array
    title = title of the graph, a string
    xlabel = x axis label, a string
    alpha = opacity of the histogram, decimal between 0 and 1
    color = color of the histogram, a string
    label = label for the legend, a string
    
    Returns:
    draws and displays a histogram'''
    #plot histogram
    hist = subplot.hist(data, bins=bins, alpha=alpha, label=label)
    #add title, axis labels, and x ticks
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel('count')
    plt.xticks(bins)
    #add mean line
    plt.axvline(data.mean(), color=color)
    #silence warning for if no legend is required, add a legend if there are labels
    logging.getLogger().setLevel(logging.CRITICAL)
    plt.legend()
    #draw
    plt.draw()

def cohend(d1, d2, Decimals):
    '''Calculates Cohen's d for independent samples
    
    Arguments:
    d1 = the first sample of data, a signle column of a dataframe or a list
    d2 = the second sample of data, a single column of a dataframe or a list
    Decimals = the number of decimals you want answers rounded to, integer
    
    Returns:
    eff_size = cohen's d, the effect size, a number
    eff_string = if the effect is trvial, small, medium, or large, a string
    prints out the effect size and a string with how large it is'''
    #calculate the size of samples
    n1, n2 = len(d1), len(d2)
    #calculate the variance of the samples
    s1, s2 = var(d1, ddof=1), var(d2, ddof=1)
    #calculate the pooled standard deviation
    s = sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
    #calculate the means of the samples
    u1, u2 = mean(d1, axis=0), mean(d2, axis=0)
    #calculate the effect size
    eff_size = round(pd.to_numeric((u1 - u2) / s), Decimals)
    abs_eff_size = abs(eff_size)
    print('Cohen\'s d =', eff_size)
    #determine magnitude of effect size
    if abs_eff_size < 0.2:
        eff_string = 'Effect size is trivial'
    elif abs_eff_size >= 0.2 and eff_size < 0.5:
        eff_string = 'Effect size is small'
    elif abs_eff_size >= 0.5 and eff_size < 0.8:
        eff_string = 'Effect size is medium'
    elif abs_eff_size >= 0.8:
        eff_string = 'Effect size is large'
    print(eff_string)
    return eff_size, eff_string   

#-------------------------------------------------------------------------------------------------------------------------------------

#Section 1: sleep duration processing and analysis

def sleep_processing(sleep_data, Date_string, Decimals):
    '''The sleep data in this study was collected using a Basis Watch. Data from a basis watch includes GMT start and end times (start_time_iso, end_time_iso). 
    We want to use GMT start time to determine what day the sleep occurs on and actual_minutes to determine sleep duration. 
    
    Arguments:
    sleep_data = a pandas dataframe with columns start_time_iso with GMT time and actual_minutes with sleep duration in minutes
    Date_string = the number of characters to keep from the start_time_iso column to keep just the date in the format YYYY-MM-DD
    Decimals = the number of decimals you want answers rounded to, integer

    Returns:
    sleep_sum_data = a dataframe with columns day with sleep start date in the format YYYY-MM-DD and actual_hours with sleep duration in hours
    prints out the basic stats for the sleep data'''
    #First, isolate the data we need for the histogram, just the start time and actual minutes
    sleep_hist_data = sleep_data.loc[:, ['start_time_iso','actual_minutes']]
    #The start_time_iso column contains the date as the first ten characters in a string in the format: YYYY-MM-DD
    #Keep just the date of the start time string
    sleep_hist_data['day'] = sleep_hist_data['start_time_iso'].str[:Date_string]
    #On some days there are multiple sleeps. We want the total duration slept on each day.
    #Use groupby to group the data by date and find the sum for each day of actual minutes of sleep.
    sleep_sum_data = sleep_hist_data.groupby('day')['actual_minutes'].sum().reset_index(name ='actual_minutes')
    #Convert the time to hours in a new column
    min_in_hour = 60
    sleep_sum_data['actual_hours'] = sleep_sum_data['actual_minutes'].div(min_in_hour).round(Decimals)
    #Run the basic stats function on the sleep data
    basic_stats(sleep_sum_data['actual_hours'], 'daily sleep', Decimals)
    return sleep_sum_data

#-------------------------------------------------------------------------------------------------------------------------------------

#Section 2: flight duration processing and analysis

def activity_processing(activity_data, Date_string, Decimals):
    '''In this function we isolate all of the flights from activities data. As with a lot of wearable data, our labels are imperfect. Some 
    flights are labeled `airplane` in the `Activity` column and others are labelled `transport`. However, `transport` is also used for car 
    rides, train rides, etc. We will define a flight as an activity that is either (labeled `airplane`) OR (labeled `transport` AND has an 
    average speed over 100 miles/hour). You can calculate speed from `Duration` (given in seconds) and `Distance` (given in miles). Additionally, 
    the fastest commercial flights run at around 660 mph. Therefore, we also filter out activities that are over 700 mph to avoid any measurements 
    that may have been errors. It is also likely that any very short duration activities tracked are errors. We get rid of any activities that 
    fall in our speed range under 30 minutes.
    
    Arguments:
    activity_data = a pandas dataframe with columns Start with GMT time, Duration with activity duration in seconds, Distance with activity distance in miles, and Activity with activity label
    Date_string = the number of characters to keep from the start_time_iso column to keep just the date in the format YYYY-MM-DD
    Decimals = the number of decimals you want answers rounded to, integer
    
    Returns:
    flights = a dataframe with columns day with flight date in the format YYYY-MM-DD and Duration with fligh duration in hours
    prints out the number of flights taken and the basic stats for flight duration'''
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
    flights = pd.concat([flights, transport_flights], axis=0)
    flights = flights.loc[:, ['day','Duration']]
    flights = flights.sort_values(by = 'day')
    #Remove flights with durations under 30 minutes, round duration
    lower_duration_threshold = 0.5
    flights = flights.loc[flights['Duration'] > lower_duration_threshold]
    flights['Duration'] = flights['Duration'].round(Decimals)
    #Print the total number of flights
    print('participant took' , len(flights), 'flights')
    #Run the basic stats function on the flight data
    basic_stats(flights['Duration'], 'flight duration', Decimals)
    return flights

#-------------------------------------------------------------------------------------------------------------------------------------

#Section 3: flight's affect on sleep

def flight_effect_sleep(flights, sleep_sum_data, Decimals):
    ''' Now we know when the participant travelled and how long they slept each day. Let’s put them together. We want to compare the participant's sleep 
    after travelling to their usual sleep. Generate a set of dates within 3 days of flight. That is, if they travelled on 3/23/14, then 
    you should include 3/23/14, 3/24/14, and 3/25/14 as "after-flight" dates.
    
    Arguments:
    flights = a dataframe with columns day with flight date in the format YYYY-MM-DD and Duration with fligh duration in hours
    sleep_sum_data = a dataframe with columns day with sleep start date in the format YYYY-MM-DD and actual_hours with sleep duration in hours
    Decimals = the number of decimals you want answers rounded to, integer
    
    Returns:
    flight_sleeps = dataframe with column sleep_duration with sleep duration in hours, contains sleeps affected by airplane travel
    non_flight_sleeps = dataframe with column sleep_duration with sleep duration in hours, contains sleeps not affected by airplane travel
    prints results from t test, cohen's d, and a string of how large the effect size is'''
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
    #perform ttest
    res = stats.ttest_ind(flight_sleeps, non_flight_sleeps)
    display(res)
    #calculate cohen's d
    cohend(flight_sleeps['sleep_duration'], non_flight_sleeps['sleep_duration'], Decimals)
    return flight_sleeps, non_flight_sleeps

#-------------------------------------------------------------------------------------------------------------------------------------

#Section 4: create plots

def plot_data(sleep_sum_data, flights, flight_sleeps, non_flight_sleeps, Sleep_bins, Flight_bins):
    '''Plots histograms of the sleep data, the flight data, and a comparative histogram of the sleeps affected by airplane flight or not.
    
    Arguments:
    sleep_sum_data = a dataframe with columns day with sleep start date in the format YYYY-MM-DD and actual_hours with sleep duration in hours
    flights = a dataframe with columns day with flight date in the format YYYY-MM-DD and Duration with fligh duration in hours
    flight_sleeps = dataframe with column sleep_duration with sleep duration in hours, contains sleeps affected by airplane travel
    non_flight_sleeps = dataframe with column sleep_duration with sleep duration in hours, contains sleeps not affected by airplane travel
    Sleep_bins = bins to be used for plotting the sleep data, a numpy array
    Flight_bins = bins to be used for plotting the  flight data, a numpy array

    Returns:
    draws and shows three histograms in one figure'''
    #Create a subplot, then call the histogram function for the sleep data
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(1, 3, 1)
    histogram(subplot=ax1, data=sleep_sum_data['actual_hours'], bins=Sleep_bins, title='Hours Slept Per Day', xlabel='hours slept')
    #Create a subplot, then call the histogram function for the activity data
    ax2 = fig1.add_subplot(1, 3, 2)
    histogram(subplot=ax2, data=flights['Duration'], bins=Flight_bins, title='Flight Durations', xlabel='flight duration (hours)')
    #Create a subplot, then call the histogram function for botht the flight affected and non flight affected sleep
    ax3 = fig1.add_subplot(1, 3, 3)
    histogram(subplot=ax3, data=flight_sleeps['sleep_duration'], bins=Sleep_bins, alpha=0.5, color='blue', label='flight sleeps')
    histogram(subplot=ax3, data=non_flight_sleeps['sleep_duration'], bins=Sleep_bins, title='Flight VS Non-Flight Sleeps', xlabel='hours slept', alpha=0.5, color='orange', label='non-flight sleeps')
    plt.show()