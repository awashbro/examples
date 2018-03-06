
import sys
from TestUtils import *

# Track failures
fails = 0

# TEST - import Weather class

try:
    from Weather import *
except ImportError:
    outResult(0,"Import Weather class")
    sys.exit(1)
outResult(1,"Import Weather class")

# TEST - Read sample data file

try:
    weatherFile = 'data/sample.txt'
    fileSlice = 0
    weather = Weather(weatherFile, fileSlice)
except IOError:
    outResult(0,"Reading sample dataset from file")
    sys.exit(1)
outResult(1,"Reading sample dataset from file")

# TEST - check if data format was accepted

if outResult((weather.isLoaded == 0), "Sample dataset format"):
    sys.exit(1)

# TEST - Check number of entries in file == 3114
fails += outResult(int(weather.getNrEntries()) == 3114, "Number of entries")

# TEST - Check number of features == 17
fails += outResult(int(weather.getNrFeatures()) == 17, "Number of features")

# TEST - Check number of stations == 126
fails += outResult(int(weather.getNrStations()) == 126, "Number of stations")

# exit code
if (fails == 0):
    sys.exit(0)
else:
    sys.exit(1)
