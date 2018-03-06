#!/usr/bin/python

""" feature-extract
- Template file to show methods on how to sanitise primary data in preparation for machine learning classification
- Example routines to add new secondary features to the observation list
"""

# Weather data is accessed through an instantation of the provided `Weather` class.
from Weather import *

# Create a new object (e.g. `weather`) of type `Weather`.
#
# As part of the instantiation provide:
# - weatherFile: The filename (either basic.txt or advanced.txt)
# - fileSlice: The number of lines to read from the chosen input file (0 is all)
#
# Use the fileSlice to limit the sample size for early evaluation
weatherFile = 'data/sample.txt'
fileSlice = 0
weather = Weather(weatherFile, fileSlice)

# Recovering Incomplete Data
#
# Some of the observation values have a value of `-99999`
# This is a default value I inserted to indicate that the feature data was either not collected
# at the time of the observation or had a null value.
#
# Any data points that contain null observations need to be corrected to avoid problems
# with subsequent filtering and modifications.
#
# In some cases null values can either be interpolated or set to a default value.
#
# The large majority of null data is from the `Gust` measurement.
# Here I assume than no observation is the same as a zero value

# zero any null gust measurements
newG = ['0' if g == '-99999' else g for g in weather.getFeatureData('Gust')]
weather.modify('Gust', newG)

# After recovering any data ensure you run the `discard()` method to
# remove any data with remaining null observations.
weather.discard()

# Some of the features have observation values that will be difficult for a machine learning estimator
# to interpret correctly (e.g. Wind Direction).
# You should ensure that all the features selected for a machine learning classification have a numeric value.
# In example 1 the pressure trend is changed from Falling, Static, Rising to -1,0,1
# In example 2 the Wind Direction is changed to a 16 point index starting from direction NNE.
# **Important**: Due to the limitations with the `Weather` class ensure that any observation data
# remains type `string` (e.g store '1' **not** 1).
# The `export()` method will convert all the values from `string` to `float` just before the export.

# Example 1 - Enumerate Pressure Trend (-1 falling, 0 static, 1 rising)

# define types
pTType = ['F', 'S', 'R']

# generate new pressure trend values
newPT = [str(pTType.index(p) - 1) for p in weather.getFeatureData('Pressure Trend') ]

# modify dataset
weather.modify('Pressure Trend', newPT)

#print 'Pressure Trend: %s' % (weather.getFeatureData('Pressure Trend'))

# Example 2 - Enumerate Wind direction (use 16 point compass index)

# define types
compassRose = ['NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW', 'N']

# generate and modify Wind direction
weather.modify('Wind Direction', [str(compassRose.index(w)) for w in weather.getFeatureData('Wind Direction')])

# You may get better insights into underlying patterns in the observations
# by extacting the provided data to generate new features.
#
# An example using the wind direction is shown below.
# The direction *relative* to the North and to the West is generated and appended to the dataset.

# set relative direction (assume 16 points)
# scores based on start NNE around clockwise
northScore = ['7', '6', '5', '4', '3', '2', '1', '0', '1', '2', '3', '4', '5', '6', '7', '8']
westScore = ['3', '2', '1', '0', '1', '2', '3', '4', '5', '6', '7', '8', '7', '6', '5', '4']
north = [northScore[int(w)] for w in weather.getFeatureData('Wind Direction')]
west = [westScore[int(w)] for w in weather.getFeatureData('Wind Direction')]

# append to dataset
weather.append('Wind Relative North', north)
weather.append('Wind Relative West', west)

# To finish create an array of strings containing a subset of the features
# you feel will perform best in the classification. Call the select() method to filter the data

features = ['Temperature', 'Visibility', 'Pressure', 'Pressure Trend', 'Humidity']
weather.select(features)

# Run the `export()` method to write the data of your selected features to file as a `pickle` object.

# This will move the target data ('Weather Type') into a new variable (`target`).

# **Note**: It is assumed that the *Station ID*  and *Station Name* will not be used
# as features for classification and are automatically stripped. The `export()` method
# will also strip out incomplete data before exporting to file.

weather.export('data/mldata.p')
