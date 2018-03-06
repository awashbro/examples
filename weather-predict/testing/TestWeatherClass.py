
import sys
from Weather import *
from TestUtils import *

# Track failures
fails = 0

# DATA READ

weatherFile = 'data/sample.txt'
fileSlice = 0
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

### TESTS

# TEST - Station details by Name
# should match ['3166' 'EDINBURGH/GOGARBANK' '55.928' '-3.343']

fails += outResult( \
            np.array_equal( \
                weather.getStationData('EDINBURGH/GOGARBANK'), \
                np.array(['3166', 'EDINBURGH/GOGARBANK', '55.928', '-3.343']) \
            ), \
            "Edinburgh station data")

# TEST - Station details by ID
# should match ['3225' 'SHAP' '54.501' '-2.684']

fails += outResult( \
            np.array_equal( \
                weather.getStationData('3225'), \
                np.array(['3225', 'SHAP', '54.501', '-2.684']) \
            ), \
            "ID 3225 station data")

# TEST - Check average Temperature and Dew point on sample date (25th Oct)
# Compare against verified means [11.376, 8.008]

# get mean observerations
stationId = weather.getStationData('EDINBURGH/GOGARBANK')
features = ['Time since midnight', 'Temperature', 'Dew Point']
obs = weather.getObservations('3166', obsDate='2017-10-25', features=features).astype(float)
means = np.mean(obs, axis=0)[1:3]

fails += outResult( \
            np.array_equal( \
                means, \
                np.array([11.376, 8.008]) \
            ), \
            "Mean temperature and dew points")

# TEST - nearest station observerations
# nearest weather station 100km NW from Edinburgh (ID 3047)

# get nearest stations 100k NW of Edinburgh station (within a 75km threshold)
stationId = weather.getStationData('EDINBURGH/GOGARBANK')
nearestStations = weather.findStations([stationId[2], stationId[3]], ['100', '-45'], maxThreshold=75)

# use nearest station (index 0)
nearStationId = nearestStations[0][0]

fails += outResult((int(nearStationId) == 3047), "Nearest station from Edinburgh")


# exit code
if (fails == 0):
    sys.exit(0)
else:
    sys.exit(1)
