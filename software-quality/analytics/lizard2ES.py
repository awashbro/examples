#!/usr/bin/python

""" lizard2ES
- Glue script to post Lizard software defect results into Elasticsearch
"""

import argparse, logging, json, sys
from collections import defaultdict
from elasticsearch import Elasticsearch
from elasticsearch import helpers

def parseResults(fname):
""" Parse results from Lizard
Args:
    fname (str): file name containing Lizard results
Returns
    fnData (dict): results data for each function
    fileData (dict): results data for each source code file
"""

    # set domains and release branch
    domains = ['function', 'file']
    branch = 'master'

    # read input file
    with open(fname) as f:
        content = f.readlines()
        content = [x.strip() for x in content]

    # strip path from filename and get tag name
    fname = fname.rsplit('/', 1)[1]
    tag = fname.split('.out', 1)[0]
    logging.debug('fname %s tag %s' % (fname, tag))

    # get date information
    year, month, day = tag.split('-')
    day, tod = day.split('T')
    timestamp = year + month + day + tod
    logging.debug('year %s month %s day %s tod %s' % (year, month, day, tod))
    logging.debug('timestamp %s' % timestamp)

    # set defaults before adding content
    fnData = defaultdict(dict)
    fileData = defaultdict(dict)
    domainType = 0
    payload = False

    # parse results file to catch results
    for line in content:

        logging.debug('line: %s' % line)

        # manage line breaks
        if '======' in line:
            domainType += 1
            if (domainType == len(domains)):
                logging.debug('end of data')
                break
            else:
                payload = 0
                logging.debug('section break detected, now in %s domain' % domains[domainType])
                continue

        # mark start of payload
        if '-----' in line:
            payload = True
            continue

        # skip to next line if payload is not detected
        if not payload:
            continue

        # parse results lines
        fields = line.split()
        if (len(fields) == 6):

            logging.debug('fields: %s' % fields)

            # exception - ignore entries with trailing backslash
            if ("\\" in fields[5]):
                continue

            # parse function results
            if (domains[domainType] == 'function'):

                # split fields to defect attributes
                nloc = fields[0]
                ccn = fields[1]
                token = fields[2]
                param = fields[3]
                length = fields[4]
                location = fields[5]

                # split code location details
                locationDetails = location.split('@')
                function = locationDetails[0]
                line = locationDetails[1]
                fname = locationDetails[2]
                logging.debug('location details %s', locationDetails)

        # parse file lines
		if ('./' in fname):

            # get function metadata into JSON format
            fname = fname[2:]
            fnData[function] = {'_index': 'lizard', '_type': 'function', '_source': {'timestamp': timestamp, 'function': function, 'line': line, 'file': fname, 'nloc': nloc, 'ccn': ccn, 'token': token, 'param': param, 'length': length}}
            logging.debug('New function data %s added: %s' % (function, fnData[function]))

            # set file metadata into JSON format
            if (domains[domainType] == 'file'):

                nloc = fields[0]
                avgnloc = fields[1]
                avgccn = fields[2]
                avgtoken = fields[3]
                avgfunction = fields[4]
                fname =  fields[5]
                fileData[fname] = {'_index': 'lizard', '_type': 'file', '_source': {'timestamp': timestamp, 'file': fname, 'nloc': nloc, 'avgnloc': avgnloc, 'avgccn': avgccn, 'avgtoken': avgtoken, 'avgfunction': avgfunction}}
                logging.debug('New file data %s added: %s' % (fname, fileData[fname]))


    logging.debug('function data size %d file data size %d ' % (len(fnData), len(fileData)))

    return (fnData, fileData)

def postToES(results, es, docType):
""" Post results to Elasticsearch
Args:
    results (dict): results data per function or file
    es: Elasticsearch instance
    docType (string): function or file type identifier
"""

    # parse into bulk request
    actions = []
    for result in results:
        actions.append(results[result])

    helpers.bulk(es, actions)
    logging.debug('publshed to ES res: %s' % res)

    return

def main():

    # get command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-v","--verbose",default="INFO",choices=["DEBUG","INFO","WARNING","ERROR","CRITICAL"],help="verbosity level")
    parser.add_argument("-f","--fname",required=True,help="Lizard results file")
    args = parser.parse_args()

    # set logging
    logging.basicConfig(filename='lizard-export.log',filemode='w',level=logging.getLevelName(args.verbose),format='%(asctime)s %(levelname)-10s %(message)s')

    # connect to es instance
    es = Elasticsearch([{'host': 'HOSTNAME', 'port': 9200}])
    health = es.cluster.health()

    # parse results file
    fnData, fileData = parseResults(args.fname)

    # post function data to ES
    postToES(fnData, es, 'function')

    # post file data to ES
    postToES(fileData, es, 'file')

    return

if __name__ == '__main__':
    main()
