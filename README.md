# BIODS Final
# Project Description
This program is being created as part of the Stanford class BIODS 253: Software Engineering for Scientists by Stanford Bioengineering graduate student Scott Piper (sjpiper@stanford.edu) in Winter quarter 2022. This class has covered the basics of software engineering and how to write clean, usable code in a collaborative environment. Highlighted topics include testing, source control, variable naming, defining functions, and writing descriptive code.

The content from this program is inspired by a problem set from the Stanford class BIOE 217: Translational Bioinformatics. This problem set uses data from a digital health paper to analyze airplane travel’s affect on sleeping patterns using wearables (Li, X., Dunn, J., Salins, D., Zhou, G., Zhou, W., Rose, S. M. S. F., ... & Sonecha, R. (2017). Digital health: tracking physiomes and activity using wearable biosensors reveals useful health-related information. PLoS biology, 15(1), e2001402). The program consists of reading in wearable data, extracting sleeping events, categorizing them as affected by a flight or not, and then comparing the two groups. The original problem set was for one participant in the study, but by adapting the code from the Jupyter Notebook problem set into a python program, it will be more easily applied to more participants.

# Repository Contents
README.md = A readme file with a brief overview of the program, instructions, dependencies, and information on the program's design.

sjpiper_BIODS_253_final_design.doc = A detailed design document with an overview, background, goals a detailed design, user requirements, potential error states, privacy and security concerns, testing, dependencies, work estimates, and related works.

sleep_analysis_lib.py = Contains the functions used to process the data and create outputs

sleep_analysis_cli.py = Contains the argparse functions to create the command line interface used to run the functions with input data

sleep_analysis_unittests.py = Contains the unittests of several functions form the library

sleep_to_03-31-16.csv = Sleep data for participant one in the related research paper

activities.csv = Activity data for participant one in the related research paper

sleep_test_data_in.csv = Contains input data used to test the sleep_processing function

sleep_test_data_out.csv = Contains expected output from running the sleep_processing function with the input test data

activity_test_data_in.csv = Contains input data used to test the activity_processing function

activity_test_data_out.csv = Contains expected output from running the activity_processing function with the input test data

flight_effect_test_data_out.csv = Contains the expected output from running the flight_effect_sleep function with the outputs from sleep_processing and flight_processing using the test data

# How to Use
This program can be run from the command line. This program takes two input arguments. The first should be the csv file containing the sleep data from the wearable with columns 'start_time_iso' with GMT date and time of the sleep starting and 'actual_minutes' with sleep duration in minutes. The second should be the csv file containing the activity data from the wearable with columns 'Start' with GMT date and time of activity start, 'Duration' with activity duration in seconds, 'Distance' with distance travelled in miles, and 'Activity' with an activity type label. This program was written on Python 3.

An example of how to run the program from the command line would be: python3 sleep_analysis.py --sleep_data_csv sleep.csv --activity_data_csv activities.csv

Run 'python3 sleep_analysis.py -h' on the command line for more information.

# Dependencies
Third party library and function dependencies include:

-Numpy 

    -Mean
  
    -Var
  
-Pandas 

-Matplotlib.pyplot

-Logging

-Argparse 

-Datetime 

    -Timedelta 
  
-Scipy 

    -Stats 
  
-IPython

    -Display 
  
-Math 

    -Sqrt

-Unittest

-Os

-Sys

# Program Design
A library (sleep_analysis_lib.py) was created with the necessary functions to process the wearable data. First, some basic supporting functions are created. These include functions to read the input data, calculate basic statistics, draw a histogram, and calculate Cohen's d. The first main function, sleep_processing, takes the sleep data and determines how many hours of sleep the subject got on each day and calculates basic stats. The second main function takes activity data and determines the date and duration of flights taken by the subject and calculates basic stats. This is done using activities labeled as ‘airplane’ or those labele 'transport' with speeds between 100 and 700 mph. The third main funciton determines which dates were affected by airline travel and daily sleep is separated into either flight-affected sleep or non flight-affected sleep. A t-test is perfromed to compare the two groups and Cohen’s d is found to analyze the effect size of airline travel on sleep. Finally three histograms are created, one of the sleep data, one of the flight data, and one that compares the flight-affected and non-flight-affected sleeps. 

A command line interface (sleep_analysis_cli.py) was created to allow the user to run these functions while inputting data from the terminal. Unittests were created for all of the major functions (sleep_analysis_unittests.py) along with test data.
