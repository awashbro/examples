#!/usr/bin/python

import argparse, gitlab, logging, sys, os
from xml.etree import ElementTree
from gitlab.exceptions import GitlabGetError, GitlabCreateError
from gitlab_mr_helpers import print_collection, list_changed_packages, list_affected_domains
from collections import defaultdict, OrderedDict

def getMRHandle(args):

    # get Gitlab handle
    gl = gitlab.Gitlab(args.url,args.token,api_version=4)

    try:
        # get Gitlab project object
        project = gl.projects.get(args.project_name)
        logging.debug("retrieved Gitlab project handle")

        # get Gitlab merge request object
        mr = project.mergerequests.get(args.mr_id)
        logging.debug("retrieved Gitlab merge request handle")

    except GitlabGetError as e:
        logging.critical("error communication with Gitlab API '%s'" % (e.error_message))
        sys.exit(1)

    # Check Merge request state
    handled_mr_states = ["opened","reopened","merged"]
    if not mr.state in handled_mr_states:
        logging.debug("ignore merge request in '%s' state" % mr.state)
        sys.exit(0)

    return mr

def getDefects(tree):

    logging.debug('getting list of defects')

    # get list of errors
    defects = tree.findall('./errors/error')

    # remove any defects without location data
    defectsNew = []
    for defect in defects:
        if defect.find('location') is not None:
            defectsNew.append(defect)
    defects = defectsNew

    return defects

def getMRFiles(mr):

    # get changed file assoicated with given merge request
    changed_files = set([c[p] for c in mr.changes()['changes'] for p in ['old_path','new_path']])
    logging.debug("changed files:\n" + print_collection(changed_files))
    return list(changed_files)

def getMRpackages(mr):

    # get changed packages assoicated with given merge request
    change_list = filter(None,list_changed_packages(mr))
    logging.debug('modified packages in MR: %s' % change_list)
    return change_list

# TODO: functionality still to be assessed - pass for now
def lineCheck(ref, ci):
    return 1

def compareDefects(CITree, refTree, mr):

    # get list of defects
    CIDefects = getDefects(CITree)
    refDefects = getDefects(refTree)

    # get list of files and packages in MR
    mrFiles = getMRFiles(mr)
    mrPackages = getMRpackages(mr)

    # TODO: cross check mrFiles same as files in CIDefects

    # reduce reference defects by package name match
    # ASSUMPTION - package name is always included in file name otherwise need explicit file list per package
    logging.info('Reducing defect files based on package name')
    logging.debug('Number of defects before reduction %d' % len(refDefects))
    reduceRefDefects = []
    for defect in refDefects:
        location = defect.find('location')
        defectFile = location.attrib.get('file')
        logging.debug('defect file %s' % defectFile)
        if any(x in defectFile for x in mrPackages):
            logging.debug('Matched defect file %s' % defectFile)
            reduceRefDefects.append(defect)
    refDefects = reduceRefDefects
    logging.debug('Number of defects after reduction %d' % len(refDefects))

    # map remaining files to packages
    for defect in refDefects:
        location = defect.find('location')
        defectFile = location.attrib.get('file')
        package = next(x for x in defectFile for x in mrPackages)
        defect.set('package', package)
        logging.debug('defect file %s mapped to package %s' % (defectFile, package))

    # set default state and match data as XML attribute
    for defect in refDefects:
        defect.set('state', 'unknown')
        defect.set('match', 'no')
        defect.set('print', 'no')
    for defect in CIDefects:
        defect.set('state', 'unknown')
        defect.set('match', 'no')
        defect.set('print', 'no')

    # check for matches against CI and and reference defects
    for CIDefect in CIDefects:

        # get location data
        CILocation = CIDefect.find('location')
        CIFile = CILocation.attrib.get('file')

        for refDefect in refDefects:

            # get loaation data
            refLocation = refDefect.find('location')
            refFile = refLocation.attrib.get('file')

            # check if already matched in previous search
            if (refDefect.attrib.get('match') == 'yes'):
                logging.debug('Already matched against ref %s' % refFile)
                continue

            logging.debug('Comparing CI file\n- %s ref file\nagainst\n- %s' % (CIFile, refFile))

            # compare filenames
            if (CIFile == refFile):

                logging.debug('Matched filenames, now compare secondary files')
                if (CILocation.attrib.get('file0') == refLocation.attrib.get('file0')):

                    # compare id and msg
                    logging.debug('Matched all files, now compare id and msg strings')
                    if ((refDefect.attrib.get('id') == CIDefect.attrib.get('id')) and \
                        (refDefect.attrib.get('msg') == CIDefect.attrib.get('msg'))):

                        # lastly compare lines of code adjusting for movement across commits
                        logging.debug('Matched id and msg strings, now perform line check')
                        if (lineCheck(refDefect, CIDefect)):

                            # match implies defect is unresolved by MR
                            logging.debug('Match complete')

                            # check if in affected files or packages
                            if any(refFile == x for x in mrFiles):
                                refDefect.set('state', 'mr-unresolved')
                            else:
                                refDefect.set('state', 'pkg-unresolved')
                            CIDefect.set('match', 'yes')
                            refDefect.set('match', 'yes')

                            break

        # set as introduced if CI defect does not match any reference defect
        if (CIDefect.attrib.get('match') == 'no'):
            logging.debug('No matches - assuming CI defect is introduced')
            CIDefect.set('state', 'introduced')

    return CIDefects, refDefects

def defectString(total):

    # set plural test on numerous defects
    if (total > 1):
        defectStr = 'defects'
    else:
        defectStr = 'defect'

    return defectStr

def orderBySeverity(elem):

    # map severity string to severity code
    severity = elem.attrib.get('severity')
    if (severity.lower() == 'error'):
        sevCode = 2
    elif (severity.lower() == 'warning'):
        sevCode = 1
    else:
        sevCode = 0

    return sevCode

def orderByNrErrors(defects):

    # return number of errors in defect list
    nrErrors = 0
    for defect in defects:
        if (defect.attrib.get('severity').lower() == 'error'):
            nrErrors += 1
    logging.debug('nrErrors %s ' % nrErrors)

    return nrErrors

def listDefects(defects, listMax, charMax):

    grouping = 0

    sevType = ['error', 'warning', 'information']

    # organise defects by group (package or file)
    defectsByGroup = defaultdict(list)
    for defect in defects:
        if (grouping == 1):
            package = defect.find('package')
            defectsByGroup[package].append(defect)
        else:
            location = defect.find('location')
            defectFile = location.attrib.get('file')
            defectsByGroup[defectFile].append(defect)

    # sort grouping by highest number of errors, then total number of defects
    orderedDefects = OrderedDict(sorted(defectsByGroup.viewitems(), key=lambda (k,v):(orderByNrErrors(v),len(v))))

    # define which defects to explictly list
    defectCount = 0
    for sev in sevType:
        for group in orderedDefects:
            for defect in orderedDefects[group]:

                location = defect.find('location')
                affectedFile = os.path.basename(location.attrib.get('file'))

                if (defect.attrib.get('severity').lower() == sev):

                    if (defectCount > listMax):
                        break
                    else:
                        defectCount += 1
                        defect.set('print', 'True')
                        logging.debug('Setting group %s file %s to print true defect count now %d' % (group, affectedFile, defectCount))

    # format print defects
    for group in orderedDefects:

        # add group name
        defectList = '- %s     \n' % group

        # first check if should print table
        printTable = False
        for defect in defects:
            if defect.attrib.get('print'):
                printTable = True
                break

        if printTable:

            # set group summary tally
            groupSummary = defaultdict(int)

            # table header
            defectList += '\n| Severity | Defect | Location |\n| --- | --- | --- |\n'

            excess = False

            for defect in defects:

                # sort defects by severity
                defects = sorted(orderedDefects[group], key=orderBySeverity, reverse=True)

                # get defect severity
                severity = defect.attrib.get('severity')

                if (defect.attrib.get('print') == 'True'):

                    # get full message
                    fullmsg = defect.attrib.get('msg')

                    # truncate message
                    if (charMax > 0):
                        msg = (fullmsg[:charMax] + '..') if len(fullmsg) > charMax else fullmsg

                    # uppercase and emphasise severity string
                    severity = severity.upper()
                    if (severity == 'ERROR'):
                        severity = '**' + severity + '**'

                    # get location information
                    location = defect.find('location')
                    affectedFile = os.path.basename(location.attrib.get('file'))
                    affectedLine = location.attrib.get('line')

                    # TODO - construct URL of file to view within Gitlab
                    url = 'url'

                    # defect string
                    defectList += '| %s | %s | [%s:%s](%s) |\n' % (severity, msg, affectedFile, affectedLine, url)
                    #defectList += '| %s | %s | [%s](%s) |\n' % (severity, msg, affectedLine, url)

                else:

                    excess = True
                    groupSummary[severity] += 1

            # print remainder summary
            if excess:
                defectList += '(and '
                for sev in groupSummary:
                    defectList += '**%d** other defects of type %s, ' % (groupSummary[sev], sev.upper())
                defectList = defectList[:-2] if defectList.endswith(', ') else defectList
                defectList += ')     \n'

        else:

            # tally by severity
            groupSummary = defaultdict(list)
            for defect in defects:
                severity = defect.attrib.get('severity')
                groupSummary[severity] += 1

            defectList += ': '
            for sev in groupSummary:
                defectList += '%d of type %s, ' % (groupSummary[sev], sev)
            defectList = defectList[:-2] if defectList.endswith(', ') else defectListq
            defectList += '\n'

    defectList += '***\n'

    return defectList

def generateReport(refDefects, CIDefects, listMax, charMax):

    logging.info('Generating summary report')

    # get state-ordered dictionary of defects
    defects = {'introduced': [], 'removed': [], 'mr-unresolved': [], 'pkg-unresolved': []}
    for key in defects:
        for defect in (refDefects + CIDefects):
            if (defect.attrib.get('state') == key):
                defects[key].append(defect)

    # report header
    report = '### Cppcheck Results\n\n'

    # show defects introduced by MR
    if (len(defects['introduced']) > 0):

        report += ':negative_squared_cross_mark: **%d** new %s introduced    \n' \
            % (len(defects['introduced']), defectString(len(defects['introduced'])))
        report += listDefects(defects['introduced'], listMax, charMax)

    else:

        report += ':white_check_mark: No new defects were introduced by this merge request    \n'

    # show defects removed by MR
    if (len(defects['removed']) > 0):

        report += ':white_check_mark: **%d** %s removed    \n' \
            % (len(defects['removed']), defectString(len(defects['removed'])))
        report += listDefects(defects['removed'], listMax, charMax)

    else:

        # check if any defects present before MR
        if not (len(refDefects)):
            report += ':information_source: No defects were found in the affected packages before the merge request    \n'

    # check for unresolved defects for files within MR
    if (len(defects['mr-unresolved']) > 0):

        report += ':warning: **%d** %s unresolved in **files** changed by this merge request    \n' \
            % (len(defects['mr-unresolved']), defectString(len(defects['mr-unresolved'])))
        report += listDefects(defects['mr-unresolved'], listMax, charMax)

    else:

        report += ':information_source: No defects were found in any of the modified files before this merge request   \n'

    # check for unresolved defects in the package
    if (len(defects['pkg-unresolved']) > 0):

        if (len(defects['mr-unresolved']) > 0):
            report += ':warning: **%d** other %s remain unresolved in the **packages** affected by this merge request    \n' \
                % (len(defects['pkg-unresolved']), defectString(len(defects['pkg-unresolved'])))
        else:
            report += ':warning: **%d** %s remain unresolved in the **packages** affected by this merge request   \n' \
                % (len(defects['pkg-unresolved']), defectString(len(defects['pkg-unresolved'])))
        report += listDefects(defects['pkg-unresolved'], listMax, charMax)

    if (len(defects['introduced']) > 0) or (len(refDefects) > 0):
        url = 'JENKINSURL'
        report += '\nFurther Details can be found in the [cppcheck Jenkins report](%s)' % url

    logging.debug(report)
    return report

    return

def postToGitlab(mr, report):

    # Post report
    try:
        mr.notes.create({'body':report})
    except GitlabCreateError as e:
        logging.critical("error creating MR comment '%s'" % (e.error_message))
        sys.exit(1)

    return

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-m","--merge-request-id",dest="mr_id",required=True,type=int,help="(unique) ID of merge request (not the project specific IID)")
    parser.add_argument("-p","--project-name",dest="project_name",required=True,help="GitLab project with namespace (e.g. user/my-project)")
    parser.add_argument("-t","--token",required=True,help="private GitLab user token")
    parser.add_argument("-u","--url",default="http://hercules.ph.ed.ac.uk",help="URL of GitLab instance")
    parser.add_argument("-v","--verbose",default="INFO",choices=["DEBUG","INFO","WARNING","ERROR","CRITICAL"],help="verbosity level")
    parser.add_argument("-r","--reference",default="defects_ref.xml",help="Reference cppcheck results file")
    parser.add_argument("-c","--ciresult",default="defects_CI.xml",help="CI cppcheck results file")
    parser.add_argument("--defectmax",required=False,default=3,type=int,help='Limit on defects to report (0 for no limit)')
    parser.add_argument("--charmax",required=False,default=80,type=int,help='Character limit on individual defects (0 for no limit)')

    # parser.add_argument("-c","--ccbin",required=True,help='cppcheck binary location')
    # parser.add_argument("-s","--src",required=True,help='relative source location')
    # parser.add_argument("-f","--filerun",required=False,default=False,help='Run over explicit file list rather than package grouping', action='store_true')

    # get command line arguments
    args = parser.parse_args()

    # set logging
    logging.basicConfig(filename='cppcheck-report.log',filemode='w',level=logging.getLevelName(args.verbose),format='%(asctime)s %(levelname)-10s %(message)s')
    logging.debug("parsed arguments:\n" + repr(args))

    # get merge request handle
    mr = getMRHandle(args)

    # read in defects from CI result
    logging.info('Reading in defects from cppcheck CI result file %s' % args.ciresult)
    CITree = ElementTree.parse(args.ciresult)

    # read in defects from reference result
    logging.info('Reading in defects from cppcheck reference result file %s' % args.reference)
    refTree = ElementTree.parse(args.reference)

    # compare CI and reference lists and tag identical defects
    CIDefects, refDefects = compareDefects(CITree, refTree, mr)

    # generate report
    report = generateReport(refDefects, CIDefects, args.defectmax, args.charmax)

    #sys.exit(0)

    # submit to MR discussion
    postToGitlab(mr, report)

    return

if __name__ == '__main__':
    main()
