#!/bin/bash

# get-observeration.sh
# observation dataset pulled daily (6.30pm) in XML and JSON format
# cron: 30 18 * * *

curl 'http://datapoint.metoffice.gov.uk/public/data/val/wxobs/all/xml/all?res=hourly&key=MYKEY' > weatherdata/$(date +"%d-%m-%y-1830").xml
curl 'http://datapoint.metoffice.gov.uk/public/data/val/wxobs/all/json/all?res=hourly&key=MYKEY' > weatherdata/$(date +"%d-%m-%y-1830").json
