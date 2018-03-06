#!/bin/bash

# STATUS FLAGS
OKFLAG="\033[92m\033[1m[OK]\033[0m"
FAILFLAG="\033[91m\033[1m[FAILED]\033[0m"

# fail count
fail=0

# run feature extraction and get timing
/usr/bin/time -f "%e" -o "testing/fe-time.out" python FeatureExtract.py | tee testing/fe.out

# check exit code
if [ $? != 0 ]; then
  echo -e "$FAILFLAG Run feature extraction"
  exit 1
fi
echo -e "$OKFLAG Run feature extraction"

# run classification step and get timing
/usr/bin/time -f "%e" -o "testing/ml-time.out" python MachineLearning.py | tee testing/ml.out

# check exit code
if [ $? != 0 ]; then
  echo -e "$FAILFLAG Run classification"
  exit 1
fi
echo -e "$OKFLAG Run classification"

exit 0
