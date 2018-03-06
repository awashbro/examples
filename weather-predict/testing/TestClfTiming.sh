#!/bin/bash

# PERFORMANCE PARAMETERS
FEMAX=1.0
MLMAX=1.0

# STATUS FLAGS
OKFLAG="\033[92m\033[1m[OK]\033[0m"
FAILFLAG="\033[91m\033[1m[FAILED]\033[0m"

# fail count
fail=0

# check feature extraction time
fe_time=$(cat testing/fe-time.out)

if [ "$(echo $fe_time'<'$FEMAX | bc -l)" -eq "1"  ]; then
  echo -e "$OKFLAG Feature extraction time: ${fe_time}s"
else
  echo -e "$FAILFLAG Feature extraction time: ${fe_time}s (should be less than ${FEMAX}s)"
  fail=$((fail + 1))
fi

# check machine learning time
ml_time=$(cat testing/ml-time.out)

if [ "$(echo $ml_time'<'$MLMAX | bc -l)" -eq "1"  ]; then
  echo -e "$OKFLAG Machine learning time: ${ml_time}s"
else
  echo -e "$FAILFLAG Machine learning time: ${ml_time}s (should be less than ${MLMAX}s)"
  fail=$((fail + 1))
fi

# check failures
if [ $fail != 0 ]; then
  exit 1
else
  exit 0
fi
