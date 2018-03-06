#!/usr/bin/python

""" coverity2ES
- Rough and ready glue script to post Coverity software defect results into Elasticsearch
"""

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from xml.etree import ElementTree
from datetime import datetime

# set input defects file
defectsFile = 'alldefects.xml'

# parse XML input data
tree = ElementTree.parse(defectsFile)
root = tree.getroot()

# define defect dictionary
defectData = {}

# parse attributes for each XML entity
for child in root:

    # get attributes
    cid = child.attrib.get('cid')
    defectType = child.attrib.get('type')
    firstDetected = child.attrib.get('firstDetected')
    impact = child.attrib.get('impact')
    status = child.attrib.get('status')
    owner = child.attrib.get('owner')
    severity = child.attrib.get('severity')
    category = child.attrib.get('category')
    defectFile = child.attrib.get('file')
    defectFunction = child.attrib.get('function')

    # get domain specialisation
    grouping = defectFile.split("/")

    # calculate age of software defect
    then = datetime.strptime(firstDetected, '%d/%m/%Y')
    now = datetime.now()
    age = (now - then).days

    # add defect to dictionary
    defectData[cid] = {'_index': 'coverity', '_type': 'all', '_source': \
        {'cid': cid, 'type': defectType, 'impact': impact, 'status': status, 'age': age, \
        'owner': owner, 'severity': severity, 'category': category, \
        'file': defectFile, 'grouping1': grouping[1], 'grouping2': grouping[2], \
        'grouping3': grouping[3], 'function': defectFunction}}

# set Elasticsearch instance
es = Elasticsearch([{'host': 'HOSTNAME', 'port': 9200}])
health = es.cluster.health()

# parse defect data into bulk request
actions = []
for result in defectData:
    actions.append(defectData[result])

# post defects to Elasticsearch instance
helpers.bulk(es, actions)
