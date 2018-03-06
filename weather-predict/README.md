
# Weather Classification

This code was developed as part of an machine learning assessment exercise. Students were asked to demonstrate the use of machine learning classification techniques to predict the weather type based on a sample of collected ground observations.

Two weeks of observation data from 24th October to 7th November (inclusive) was collected from the [UK Met Office DataPoint
service](https://www.metoffice.gov.uk/datapoint). Observations are made hourly at each of the 126 observation stations.

## Observation data

Each data point consists of the following observations (or *features*):

- Temperature (degrees Celsius)
- Wind direction (16 point compass)
- Wind speed (mph)
- Wind gust (mph)
- Dew Point (degrees Celsius)
- Screen Relative Humidity (\%)
- Visibility (m)
- Pressure (hPa)
- Pressure Tendency (Pa/s)

For more information on the collection of this data see the [Met office specific observations reference](https://www.metoffice.gov.uk/datapoint/product/uk-hourly-site-specific-observations)

The *Weather Type* is also collected at the time of the observation. This is an index of the 30 types of possible weather as described [here](https://www.metoffice.gov.uk/datapoint/support/documentation/code-definitions). It was difficult to apply a machine learning classification to all 30 types. To simplify the problem for this assignment the data has been reorganised into three data sources:

- **Basic**: each data point is labelled as one of 3 Weather Types - Clear, Cloudy} and Precipitation
- **Main**: 11 types - Clear, Partly Cloudy, Mist, Fog, Cloudy, Overcast, Rain, Sleet, Hail, Snow, and Thunder
- **Full**: All 30 types as defined by the Datapoint service

## Assessment

Students were asked to do the following:

- Create suitable training and testing data samples based upon a suitable selection of Features from the data
- Select the *Decision Tree* classification method
- Fit the training data
- Predict the Weather Type using the testing data
- Visualise the classification process
- Evaluate the prediction performance
- Generate secondary features from the observation data with more discrimination power
- Use a selection of different classification methods and compare the relative performance
- Optimise your chosen classifier(s)

## Data Extraction

Source data is pulled from the Datapoint service daily using `curl` with a registered API key (see `get-observeration.sh`)

For the given sampling period the script `source-extract.py` converts the raw XML data into easier to read text format - with one observation entry per line and features single space separated. Three sets of primary data sources were generated (basic, main and full as described above) to allow classification techniques to be evaluated.

## Feature Extraction

The script `feature-extract.py` reads the text-based data and performs the following steps:

- Loads the weather data from file
- Displays information about the dataset
- Recovers any incomplete data with null observations
- Discards any data that cannot be recovered
- Converts the data into an appropriate format for classification
- Appends new features derived from the data
- Selects features to be exported for classification

Once executed the chosen formatted weather data is stored in a `Weather` object and exported to file using `pickle`.

## Feature Classification

A template script was provided to students with step by step instructions on how to run a classification method using [Scikit Learn](http://scikit-learn.org/stable/). A minimal classification and evaluation workflow is shown in `machine-learning.py`

## Jupyter Notebooks

Jupyter Notebooks (*python 2x*) were also provided for the interactive evaluation of the student's chosen classification method. Feature extraction and a minimal classification workflow are available in `notebooks/`

## Functionality testing

As part of a best practices [Continuous Integration tutorial](https://marioa.github.io/2018-02-19-edinburgh/) test scripts were written to test functionality and evaluate machine learn performance. These tests were integrated into a Gitlab project and run as part of the CI/CD process. All tests are available in `testing/`
