import os
import numpy as np
import pandas as pd
import re
#import csv
import sys
import matplotlib.pyplot as plt

''' evttiming-hist.py
- Get histograms illustrating time per event across all completed HPC jobs
- Extract data from central framwework logging
'''

# get parameters
p = re.search('(?<=-)[a-z]+', str(sys.argv[1]))
parameter_str = str(p.group(0))
num_param = 'no. of ' + parameter_str

filecount = 0
evtparam = []

# create new results file (text)
f = open('evttimes.txt', 'w')

# traverse results directory
for subdir, dirs, files in os.walk('RESULTSDIR'):

    for file in files:
        filepath = subdir + os.sep + file

        if filepath.endswith('AthenaMP.log'):

            filecount = filecount + 1

            # extract lines of interest from log file
            linelist = [ line.rstrip('\n') for line in open(filepath) if 'INFO [evt' in line ]

            # extract CPU time and write to file
            for line in linelist:
                m = re.search('(?<=cpu=)\d+', line)
                cputime = int(m.group(0))/1000.0
                f.write((str(cputime)+'\n'))

print('\nNumber of files scanned: %d\n') % filecount

# write to CSV file
with open('evttimes.csv', 'w') as f:
    for item in evtparam:
        csv.writer(f).writerow([item])

# plot CPU time on histogram
plt.figure
plt.hist(evtparam, bins=np.arange(0, 3000, 100), histtype='step', color='b', label='Time per event')
plt.xlabel('Time interval')
plt.ylabel('No. of events')
plt.legend()
plt.savefig('evttime-all.png')
