import os, sys
import numpy as np
import pandas as pd
import re
import itertools
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

''' file-analysis
- Interpret results from file trace from loggedFS
'''

# get log file name based on input argument
filepath = 'RESULTSDIR' + str(sys.argv[1]) + '.log'

# get number of time each file is read
r_linelist = [ line.rstrip('\n') for line in open(filepath) if ('bytes read from' in line) ]
print '\nNumber of times a file is read: %d' % len(r_linelist)

# get number of time each file is written
w_linelist = [ line.rstrip('\n') for line in open(filepath) if ('bytes written to' in line) ]
print 'Number of times a file is written to: %d\n' % len(w_linelist)

# Create a list 'timelist' of the first word (string containing timestamp) for each string in array linelist
r_timelist = [line.split()[0] for line in r_linelist]
w_timelist = [line.split()[0] for line in w_linelist]

# Create list of all files accessed
files_read = []
for line in r_linelist:
    s = re.search('(?<=bytes read from ).+(?= at offset)', line)
    files_read.append(str(s.group(0)))
print 'Number of files read: %d\n' % len(files_read)

counts = Counter(files_read)
freq_list = counts.items()
print freq_list[:10]

# Convert each timestamp string element in the list to its equivalent value in seconds
ftr = [3600,60,1]
r_timelist = map(lambda x: sum([a*b/60 for a,b in zip(ftr, [int(i) for i in x.split(":")])]), r_timelist)
w_timelist = map(lambda x: sum([a*b/60 for a,b in zip(ftr, [int(i) for i in x.split(":")])]), w_timelist)

# Get initial and end times
with open(filepath,'rb') as source:
    if str(sys.argv[1]) == 'cvmfs':
        initial_time = str(source.readline()).split()[0]
    else:
        for i, line in enumerate(source):
            if i == 5:
                initial_time = str(line.rstrip('\n')).split()[0]
            elif i > 25:
                break
    source.seek(-2, 2)
    while source.read(1) != b"\n":
        source.seek(-2, 1)
    end_time = str(source.readline()).split()[0]
initial_time = sum([a*b/60 for a,b in zip(ftr, [int(i) for i in initial_time.split(":")])])
end_time = sum([a*b/60 for a,b in zip(ftr, [int(i) for i in end_time.split(":")])]) - initial_time

# Calculate absolute time from beginning of log file
r_timelist2 = map(lambda x: x - initial_time, r_timelist)
w_timelist2 = map(lambda x: x - initial_time, w_timelist)

# plot files read and written
plt.figure
plt.hist(r_timelist2, bins=np.arange(0, int(end_time)+1, 1), histtype='step', color='b', label='Files read')
if str(sys.argv[1]) == 'filetrace':
    plt.hist(w_timelist2, bins=np.arange(0, int(end_time)+1, 1), histtype='step', color='r', label='Files written')
plt.xlabel('Time interval')
plt.ylabel('No. of file accesses')
plt.legend()
plt.savefig('fileaccess-hist-'+str(sys.argv[1])+'.png')
