# BIODS Final
# Project Description
This program is being created as part of the Stanford class BIODS 253: Software Engineering for Scientists by Stanford Bioengineering graduate student Scott Piper (sjpiper@stanford.edu) in Winter quarter 2022. This class has covered the basics of software engineering and how to write clean, usable code in a collaborative environment. Highlighted topics include testing, source control, variable naming, defining functions, and writing descriptive code.

The content from this program is inspired by a problem set from the Stanford class BIOE 217: Translational Bioinformatics. This problem uses data from a digital health paper to analyze airline travel’s affect on sleeping patterns using wearables (Li, X., Dunn, J., Salins, D., Zhou, G., Zhou, W., Rose, S. M. S. F., ... & Sonecha, R. (2017). Digital health: tracking physiomes and activity using wearable biosensors reveals useful health-related information. PLoS biology, 15(1), e2001402). The program consists of reading in wearable data, extracting sleeping events, categorizing them as affected by a flight or not, and then comparing the two groups. The original problem set was for one participant in the study, but by adapting the code from the Jupyter Notebook problem set into a python program, it will be more easily applied to more participants.

# Repository Contents
README.md = A readme file with a brief overview of the program, instructions, dependencies, and information on the program's design.
design_doc.__ = A detailed design document with an overview, background, goals a detailed design, user requirements, potential error states, privacy and security concerns, testing, dependencies, work estimates, and related works.
sleep_analysis.py = The program used to analyze the data, can be run from the command line.
sleep_to_03-31-16.csv = Sleep data for participant one in the related research paper
activities.csv = activity data for participant one in the related research paper

# How to Use
This program can be run from the command line. This program takes two input arguments. The first should be the csv file containing the sleep data from the wearable with columns 'start_time_iso' with GMT date and time of the sleep starting and 'actual_minutes' with sleep duration in minutes. The second should be the csv file containing the activity data from the wearable with columns 'Start' with GMT date and time of activity start, 'Duration' with activity duration in seconds, 'Distance' with distance travelled in miles, and 'Activity' with an activity type label. This program was written on Python 3.

An example of how to run the program from the command line would be: python3 sleep_analysis.py --sleep_data_csv sleep.csv --activity_data_csv activities.csv

Run 'python3 sleep_analysis.py -h' on the command line for more information.

# Dependencies
Third party library and function dependencies include:

-Sys

-Numpy 

    -Mean
  
    -Var
  
-Pandas 

-Matplotlib.pyplot

-Argparse 

-Datetime 

    -Timedelta 
  
-Scipy 

    -Stats 
  
-IPython

    -Display 
  
-Math 

    -Sqrt

# Program Design
The program is broken into a few basic sections for each task necessary to analyze the data. Each section is its own function. The program begins with some brief comments giving an introduction to the program and how to use it. Next, the necessary libraries and functions are imported. After this, the arguments and help statements are generated. Then we define a few functions to read in the input data from the command line, calculate basic statistics, plot a histogram, and calculate Cohen’s d.

After this initial material comes the first main section of the code. Section one defines a function that takes the sleep data and determines how many hours of sleep the subject got on each day. A histogram is returned and basic stats are calculated.

The second section defines a function that takes activity data and determines the date and duration of flights taken by the subject. This is done using activities labeled as ‘airplane’ or those with speeds over 100 mph. A histogram is returned here as well.

Section three defines a function in which the dates affected by airline travel are determined and daily sleep is separated into either the flight-affected sleep or non flight-affected sleep. A histogram and t-test are delivered to compare the two groups. Additionally, Cohen’s d is found to analyze the effect size of airline travel on sleep.

Once all these functions are defined, some constants are set and the functions are called.
