import sys
import os
import numpy as np
import pandas as pd
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

''' extract-timing-info
- Extract timing data from central framwework logging
- Use dataframe to store extracted values 
'''

# Function to count number of immediate subdirectories in a directory 'a_dir'
def get_immediate_subdirectories_num(a_dir):
    dir_list = [name for name in os.listdir(a_dir) if os.path.isdir(os.path.join(a_dir, name))]
    return len(dir_list)

# Function to get name of immediate subdirectories in a directory 'a_dir'
def get_immediate_subdirectories(a_dir):
    dir_list = [name for name in os.listdir(a_dir) if os.path.isdir(os.path.join(a_dir, name))]
    return dir_list[0]

# Function to check if all elements in list are positive
def positive(a_list):
    flag = 1
    for item in a_list:
        if item < 0:
            flag = 0
    return flag

# get parameters
p = re.search('(?<=-)[a-z]+', str(sys.argv[1]))
parameter_str = str(p.group(0))
num_param = 'no. of ' + parameter_str

# Create dataframe in which dataset will be stored
df = pd.DataFrame(columns=['job ID', \
                           num_param, \
                           'pre-job input', \
                           'opening input file', \
                           'upto appmgr start', \
                           'initialisation', \
                           'event loop', \
                           'ending'])

# Initialize counting variables
included = 0
num_of_nodes = 0

# Loop through all files in directory test1/output/ and search for log.EVNTtoHITS files for each Athena job
for subdir, dirs, files in os.walk('RESULTSDIR'+str(sys.argv[1])+'/output/'):

    for file in files:

        filepath = subdir + os.sep + file

        if filepath.endswith('.EVNTtoHITS'):

            # Extract job ID from file path and convert it to an integer
            j = re.search('\d+(?=.sdb)', filepath)
            curr_job_ID = int(j.group(0))

            # Extract lines containing certain strings from the log file and write the lines to a list
            linelist = [ line.rstrip('\n') for line in open(filepath) if ('Setting up DBRelease' in line or \
                                                                          'in ISF_Input' in line or \
                                                                          'Welcome to ApplicationMgr' in line or \
                                                                          'Event Counter process created' in line or \
                                                                          'Statuses of sub-processes' in line) ]

            # Extract last line of log file and append it to the list
            with open(filepath,'rb') as source:
                source.seek(-2, 2)
                while source.read(1) != b"\n":
                    source.seek(-2, 1)
                linelist.append(str(source.readline()))

            # Create a list 'timelist' of the first word (string containing timestamp) for each string in array linelist
            timelist = [line.split()[0] for line in linelist]

            # Convert each timestamp string element in the list to its equivalent value in seconds
            ftr = [3600,60,1]
            timelist = map(lambda x: sum([a*b for a,b in zip(ftr, [int(i) for i in x.split(":")])]), timelist)

            # Create a new list 'timelist2' containing the difference of each consecutive pair of elements from 'timelist'
            timelist2 = []
            timelist2 = np.diff(timelist)

            # If the list 'timelist2' has 6 elements (i.e., if the job finished execution and wasn't stopped prematurely), append the list to the dataframe;
            # if not, print error message
            if (len(timelist2) == 6 and positive(timelist2)):
                included = included + 1

                # Find number of nodes
                num_of_nodes = get_immediate_subdirectories_num('RESULTSDIR'+str(sys.argv[1])+'/output/'+str(curr_job_ID)+'.sdb/run/')

                # Find number of cores
                dir_name = get_immediate_subdirectories('RESULTSDIR'+str(sys.argv[1])+'/output/'+str(curr_job_ID)+'.sdb/run/')
                num_of_cores = get_immediate_subdirectories_num('RESULTSDIR'+str(sys.argv[1])+'/output/'+str(curr_job_ID)+'.sdb/run/'+dir_name+'/athenaMP-workers-EVNTtoHITS-sim/')
                num_of_cores = num_of_cores - 1

                # Find number of events
                with open('RESULTSDIR'+str(sys.argv[1])+'/output/'+str(curr_job_ID)+'.sdb/heartbeat.log','r') as source:
                    e = re.findall('(?<=evt )\d+', str(source.readline()))
                    num_of_events = int(e[1]) - int(e[0]) + 1

                if parameter_str == 'nodes':
                    event_stages = np.insert(timelist2, 0, num_of_nodes)
                elif parameter_str == 'cores':
                    event_stages = np.insert(timelist2, 0, num_of_cores)
                else:
                    event_stages = np.insert(timelist2, 0, num_of_events)

                event_stages = np.insert(event_stages, 0, curr_job_ID)

                # append to DF
                df = df.append(pd.Series(event_stages, index=['job ID', \
                                                              num_param, \
                                                              'pre-job input', \
                                                              'opening input file', \
                                                              'upto appmgr start', \
                                                              'initialisation', \
                                                              'event loop', \
                                                              'ending']), ignore_index=True)

            elif len(timelist2) < 6:
                print("Error for node in job %d: negative timing values") % curr_job_ID

            else:
                print("Error for node in job %d: events did not complete") % curr_job_ID

# Reduce all rows belonging to a single job to one row inthe dataframe
df2 = df[[num_param, \
        'pre-job input', \
        'opening input file', \
        'upto appmgr start', \
        'initialisation', \
        'event loop', \
        'ending']]
df_mean = df2.groupby(num_param).mean()
df_std = df2.groupby(num_param).std()

# plot mean values of parameters
plt.figure
df_mean.plot(yerr=df_std)
plt.savefig("EVTStoHITS-plot-"+parameter_str+"-mean.png")

# Write the dataframe to a CSV file
df_mean.to_csv('/work/d60/d60/shared/optimisation/benchmark/results/'+str(sys.argv[1])+'_EVNTtoHITS_stagetiming.csv')
