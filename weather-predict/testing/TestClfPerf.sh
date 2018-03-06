#!/bin/bash

# PERFORMANCE PARAMETERS
PRECMIN=0.7
RECMIN=0.7
F1MIN=0.7

# STATUS FLAGS
OKFLAG="\033[92m\033[1m[OK]\033[0m"
FAILFLAG="\033[91m\033[1m[FAILED]\033[0m"

# fail count
fail=0

# check precision
precision=$(grep total testing/ml.out | awk '{print $4}')
if [ "$(echo $precision'>'$PRECMIN | bc -l)" -eq "1"  ]; then
  echo -e "$OKFLAG Precision is $precision"
else
  echo -e "$FAILFLAG Precision is $precision (should be more than $PRECMIN)"
  fail=$((fail + 1))
fi

# check recall
recall=$(grep total testing/ml.out | awk '{print $5}')
if [ "$(echo $recall'>'$RECMIN | bc -l)" -eq "1"  ]; then
  echo -e "$OKFLAG Recall is $recall"
else
  echo -e "$FAILFLAG Recall is $recall (should be more than $RECMIN)"
  fail=$((fail + 1))
fi

# check f1score
f1score=$(grep total testing/ml.out | awk '{print $6}')
if [ "$(echo $f1score'>'$F1MIN | bc -l)" -eq "1"  ]; then
  echo -e "$OKFLAG F1score is $f1score"
else
  echo -e "$FAILFLAG F1score is $f1score (should be more than $F1MIN)"
  fail=$((fail + 1))
fi

# check failures
if [ $fail != 0 ]; then
  exit 1
else
  exit 0
fi
