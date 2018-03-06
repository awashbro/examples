#!/usr/bin/python

""" source-extract
- Parse XML daily data from UK Met Office Data Point service for pre-defined
observation period
- To simplify assessment data can be reduced to lower dimension feature set using the conv variable
  - 0 for full
  - 1 for main (11 features)
  - 2 for basic (3 features)
- Capture and filter results in STDOUT rather than define file
- Details on the data format are provided at https://www.metoffice.gov.uk/datapoint/support/documentation/code-definitions
"""

import logging
from xml.etree import ElementTree

def extractData(weatherData, conv):
    """ Extract weather data from XML source file
    Args:
        weatherData (str): file name for source data
        conv (int): conversion type (0 = full, 1 = main, 2 = basic)
    Returns:
        0 for success
    """

    # set weather description (full)
    fullWeatherIdx = ['Clear Night', 'Sunny Day', 'Partly cloudy (night)', 'Partly cloudy (day)',\
     'Not used', 'Mist', 'Fog', 'Cloudy', 'Overcast', 'Light rain shower (night)', \
     'Light rain shower (day)', 'Drizzle', 'Light rain', 'Heavy rain shower (night)', \
     'Heavy rain shower (day)', 'Heavy rain', 'Sleet shower (night)', 'Sleet shower (day)', \
     'Sleet', 'Hail shower (night)', 'Hail shower (day)', 'Hail', 'Light snow shower (night)', \
     'Light snow shower (day)', 'Light snow', 'Heavy snow shower (night)', 'Heavy snow shower (day)', \
     'Heavy snow', 'Thunder shower', 'Thunder shower (night)', 'Thunder']

    # set weather description and conversion dict (main)
    mainWeatherIdx = ['Clear', 'Partly Cloudy', 'Mist', 'Fog', 'Cloudy', \
        'Overcast', 'Rain', 'Sleet', 'Hail', 'Snow', 'Thunder']
    conversionMain = { 'Clear Night' : 'Clear', \
        'Sunny Day' : 'Clear', \
        'Partly cloudy (night)' : 'Partly Cloudy', \
        'Partly cloudy (day)' : 'Partly Cloudy', \
        'Mist' : 'Mist', \
        'Fog' : 'Fog', \
        'Cloudy' : 'Cloudy', \
        'Overcast' : 'Overcast', \
        'Light rain shower (night)' : 'Rain', \
        'Light rain shower (day)' : 'Rain', \
        'Drizzle' : 'Rain', \
        'Light rain' : 'Rain', \
        'Heavy rain shower (night)' : 'Rain', \
        'Heavy rain shower (day)' : 'Rain', \
        'Heavy rain' : 'Rain',  \
        'Sleet shower (night)' : 'Sleet', \
        'Sleet shower (day)' : 'Sleet', \
        'Sleet' : 'Sleet', \
        'Hail shower (night)' : 'Hail', \
        'Hail shower (day)' : 'Hail', \
        'Hail' : 'Hail', \
        'Light snow shower (night)' : 'Snow', \
        'Light snow shower (day)' : 'Snow', \
        'Light snow' : 'Snow', \
        'Heavy snow shower (night)' : 'Snow', \
        'Heavy snow shower (day)' : 'Snow', \
        'Heavy snow' : 'Snow', \
        'Thunder shower (night)' : 'Thunder', \
        'Thunder shower (day)' : 'Thunder', \
        'Thunder' : 'Thunder' }

    # set weather description and conversion dict (main)
    basicWeatherIdx = ['Clear', 'Cloudy', 'Precipitation']
    conversionBasic = { 'Clear Night' : 'Clear', \
        'Sunny Day' : 'Clear', \
        'Partly cloudy (night)' : 'Cloudy', \
        'Partly cloudy (day)' : 'Cloudy', \
        'Mist' : 'Cloudy', \
        'Fog' : 'Cloudy', \
        'Cloudy' : 'Cloudy', \
        'Overcast' : 'Cloudy', \
        'Light rain shower (night)' : 'Precipitation', \
        'Light rain shower (day)' : 'Precipitation', \
        'Drizzle' : 'Precipitation', \
        'Light rain' : 'Precipitation', \
        'Heavy rain shower (night)' : 'Precipitation', \
        'Heavy rain shower (day)' : 'Precipitation', \
        'Heavy rain' : 'Precipitation',  \
        'Sleet shower (night)' : 'Precipitation', \
        'Sleet shower (day)' : 'Precipitation', \
        'Sleet' : 'Precipitation', \
        'Hail shower (night)' : 'Precipitation', \
        'Hail shower (day)' : 'Precipitation', \
        'Hail' : 'Precipitation', \
        'Light snow shower (night)' : 'Precipitation', \
        'Light snow shower (day)' : 'Precipitation', \
        'Light snow' : 'Precipitation', \
        'Heavy snow shower (night)' : 'Precipitation', \
        'Heavy snow shower (day)' : 'Precipitation', \
        'Heavy snow' : 'Precipitation', \
        'Thunder shower (night)' : 'Precipitation', \
        'Thunder shower (day)' : 'Precipitation', \
        'Thunder' : 'Precipitation' }

    # get XML root
    root = weatherData.getroot()

    # parse each observation pivoting on "Location" attribute
    for location in root.iter('Location'):

        locationData = []

        # extract location data
        locationData.append(location.attrib.get('i'))
        nameRaw = location.attrib.get('name')
        nameNew = nameRaw.replace(' ', '_')
        locationData.append(nameNew)
        locationData.append(location.attrib.get('elevation'))
        locationData.append(location.attrib.get('lat'))
        locationData.append(location.attrib.get('lon'))

        # skip a data point if location data is missing
        if any(v is None for v in locationData):
            logging.error('Location data element empty!')
            continue

        # extract observations for each time period
        for period in location:

            # extract data sample
            obsDate = period.attrib.get('value')

            # skip if date stamp is missing
            if (obsDate is None):
                logging.warning('Observation date empty!')
                continue

            for obs in period:

                obsData = []

                # extract observations
                obsData.append(obs.attrib.get('G'))
                obsData.append(obs.attrib.get('T'))
                obsData.append(obs.attrib.get('V'))
                obsData.append(obs.attrib.get('D'))
                obsData.append(obs.attrib.get('S'))
                obsData.append(obs.attrib.get('P'))
                obsData.append(obs.attrib.get('Pt'))
                obsData.append(obs.attrib.get('Dp'))
                obsData.append(obs.attrib.get('H'))
                weatherType = obs.attrib.get('W')
                obsTime = obs.text

                # skip if weather type is missing or marked undefined
                if ((weatherType is None) or (weatherType is 'NA')):
                    logging.info('Empty weather type')
                    continue

                # convert weather type
                wType = fullWeatherIdx[int(weatherType)]
                if (conv is 1):
                    newWType = conversionMain[wType]
                    weatherType = str(mainWeatherIdx.index(newWType))
                elif (conv is 2):
                    newWType = conversionBasic[wType]
                    weatherType = str(basicWeatherIdx.index(newWType))

                # set null observations to -99999 default
                if any(v is None for v in obsData):
                    for i in range(len(obsData)):
                        if (obsData[i] is None):
                            obsData[i] = "-99999"
                            logging.info('Empty observation %d' % i)

                # change observation date - remove time zone string ('Z')
                obsDate = obsDate.replace('Z', '')

                # prepare observation string as single space separated line
                dataStr = ''
                for val in locationData:
                    dataStr += val + ' '
                dataStr += obsDate + ' ' + obsTime + ' '
                for val in obsData:
                    dataStr += val + ' '
                dataStr += weatherType

                # print observation string to STDOUT
                print dataStr

    return 0

def main():

    # set conversion level (0 = full, 1 = main, 2 = basic)
    conv = 2

    # set logging
    logging.basicConfig(filename='weatherparse.log',filemode='w',level=logging.getLevelName('INFO'),\
        format='%(asctime)s %(levelname)-10s %(message)s')

    # set data source
    weatherFiles = ['data/24-10-17-1830.xml', 'data/25-10-17-1830.xml', 'data/26-10-17-1830.xml',  \
         'data/27-10-17-1830.xml',  'data/28-10-17-1830.xml', 'data/29-10-17-1830.xml', \
         'data/30-10-17-1830.xml',  'data/31-10-17-1830.xml', 'data/01-11-17-1830.xml', \
         'data/02-11-17-1830.xml',  'data/03-11-17-1830.xml', 'data/04-11-17-1830.xml', \
         'data/05-11-17-1830.xml',  'data/06-11-17-1830.xml', 'data/07-11-17-1830.xml', \
         ]

    # cycle through files
    for wfile in weatherFiles:

        # load in tree
        logging.info('Reading weather file %s' % wfile)
        weatherTree = ElementTree.parse(wfile)

        # get weather data from file
        extractData(weatherTree, conv)

    return

if __name__ == '__main__':
    main()
