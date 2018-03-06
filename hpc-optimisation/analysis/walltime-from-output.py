import os
import sys
import numpy as np
import pandas as pd
import re
import itertools
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Function to count number of immediate subdirectories in a directory 'a_dir'
def get_immediate_subdirectories(a_dir):
    dir_list = [name for name in os.listdir(a_dir) if os.path.isdir(os.path.join(a_dir, name))]
    return len(dir_list)

# Find out what parameter is being considered from the input string (cores/nodes/events)
p = re.search('(?<=-)[a-z]+', str(sys.argv[1]))
parameter_str = str(p.group(0))

# Create dataframe in which dataset will be stored
df = pd.DataFrame(columns=['job ID', \
                           'nodes', \
                           'cores', \
                           'events', \
                           'req walltime', \
                           'used walltime'], dtype=float)

# Loop through all files in directory test1/output/ and search for ath-NxExCx.oXXXXXXX files for each worker on each job
dest_dir = 'RESULTSDIR'+str(sys.argv[1])
files = [ f for f in os.listdir(dest_dir) if os.path.isfile(os.path.join(dest_dir, f)) ]

for file in files:

    filepath = str(dest_dir + os.sep + file)

    # get ID and job metadata from filepath
    if 'ath-N' in filepath and '.o' in filepath:
        print(filepath)

        j = re.search('(?<=.o)\d+', filepath)
        curr_job_ID = int(j.group(0))

        n = re.search('(?<=N)\d+', filepath)
        num_of_nodes = int(n.group(0))

        e = re.search('(?<=E)\d+', filepath)
        num_of_events = int(e.group(0))

        c = re.search('(?<=C)\d+', filepath)
        num_of_cores = int(c.group(0))

        # Extract lines containing certain strings from the log file and write the lines to a list
        # extract all timestamps matching regular expression from the list 'linelist' and write the strings to a list
        linelist = [ line.rstrip('\n') for line in open(filepath, 'rb') if 'walltime' in line ]
        walltimes = [re.findall('(?<=walltime=)\d\d:\d\d:\d\d', line) for line in linelist]
        walltimes = list(itertools.chain(*walltimes))

        # Convert each timestamp string element in the list to its equivalent value in seconds
        ftr = [3600,60,1]
        walltimes = map(lambda x: sum([a*b/60.0 for a,b in zip(ftr, [int(i) for i in x.split(":")])]), walltimes)

        # Merge extracted data into single Series and append it to the dataframe
        if (walltimes[0] > walltimes[1] and walltimes[1] > 20):
            job_info = [curr_job_ID, num_of_nodes, num_of_cores, num_of_events, walltimes[0], walltimes[1]]
       	    df = df.append(pd.Series(job_info, index=['job ID', \
                                                      'nodes', \
                                                      'cores', \
                                                      'events', \
                                                      'req walltime', \
                                                      'used walltime']), ignore_index=True)



# get mean and std for each parameter
df2 = df[[parameter_str, 'used walltime']].sort(parameter_str)
df_mean = df2.groupby(parameter_str).mean()
df_std = df2.groupby(parameter_str).std()

# plot means (with std error)
plt.figure
df_mean.plot(yerr=df_std)
plt.savefig("walltime-info-"+parameter_str+"-mean.png")

# Write dataframe to CSV file
df.to_csv('/work/d60/d60/shared/optimisation/benchmark/results/'+str(sys.argv[1])+'_walltime-info.csv')
