
import sys
import pickle
from Weather import *
from TestUtils import *

# Track failures
fails = 0

# DATA READ

# Take first 100 entries for testing
weatherFile = 'data/sample.txt'
fileSlice = 100
weather = Weather(weatherFile, fileSlice)

# DATA TREATMENT

# zero any null gust measurements
newG = ['0' if g == '-99999' else g for g in weather.getFeatureData('Gust')]
weather.modify('Gust', newG)

# remove any data with remaining null observations.
weather.discard()

# generate new pressure trend values
pTType = ['F', 'S', 'R']
newPT = [str(pTType.index(p) - 1) for p in weather.getFeatureData('Pressure Trend') ]
weather.modify('Pressure Trend', newPT)

# generate and modify Wind direction
compassRose = ['NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW', 'N']
weather.modify('Wind Direction', [str(compassRose.index(w)) for w in weather.getFeatureData('Wind Direction')])

## TESTS

# TEST - export to file

try:
    weather.export('testexport.p')
except ImportError:
    outResult(0,"Exporting to file")
    sys.exit(1)
outResult(1,"Exporting to file")

# TEST - read back in

try:
    weatherRead = pickle.load(open('testexport.p'))
except IOError:
    outResult(0,"Reading from file")
    sys.exit(1)
outResult(1,"Reading from file")

# TEST - check number of entries == 100
fails += outResult(int(weatherRead.getNrEntries()) == 100, "Number of entries")

# exit code
if (fails == 0):
    sys.exit(0)
else:
    sys.exit(1)

#
# if (int(weatherRead.getNrEntries()) != 100):
#     print "\033[91m\033[1m[FAILED]\033[0m " + "number of entries"
#     sys.exit(1)
# print "\033[92m\033[1m[OK]\033[0m " + "number of entries"
