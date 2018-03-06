#!/usr/bin/python

""" feature-extract
- Template file to show how to perform basic machine learning classification on weather observation data using Scikit Learn
"""

import pickle
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split, GridSearchCV

# Load the weather data you created by FeatureExtraction.py
weather = pickle.load(open('data/mldata.p'))

# Define the training and testing sample
train_data, test_data, train_target, test_target = train_test_split(
    weather.data, weather.target, test_size=0.5, random_state=0)

# Define the classification method
clf = DecisionTreeClassifier(max_depth=3)

# Fit the training data
clf.fit(train_data, train_target)

# Define the expected and predicted datasets
expected = test_target
predicted = clf.predict(test_data)

# Prediction Evaluation
print("Classification report for classifier %s:\n%s\n"
      % (clf, classification_report(expected, predicted)))
print("Confusion matrix:\n%s" % confusion_matrix(expected, predicted))
