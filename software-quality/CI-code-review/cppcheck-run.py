#!/usr/bin/python

import argparse, gitlab, logging, re, sys, os
from gitlab.exceptions import GitlabGetError
from gitlab_mr_helpers import print_collection, list_changed_packages, list_affected_domains

def list_changed_files(mr):

    # get changed file assoicated with given merge request
    changed_files = set([c[p] for c in mr.changes()['changes'] for p in ['old_path','new_path']])
    logging.debug("changed files:\n" + print_collection(changed_files))

    return list(changed_files)

def get_change_list(args):

    # get GitLab API handler
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

    # get list of affected packages
    change_list = []
    if args.filerun:
        change_list = list_changed_files(mr)
    else:
        change_list = filter(None,list_changed_packages(mr))

    logging.debug('change_list: %s' % change_list)

    return change_list

def run_cppcheck(change_list, args):

    logging.info('Running cppcheck')

    # set default maximum file/package arguments
    if ( (args.max > 0) and (len(change_list) > args.max) ):
        logging.info('Maximum number of arguments to cppcheck exceeded (%s > %s)' % (len(changeList), maxArgs))
        del changeList[maxArgs:]

    # set default cppcheck flags
    flags = {'--enable': 'warning,missingInclude,portability', '--xml-version': 2, '--inline-suppr': None}

    # add cppcheck flags to argument list
    cppcheckArg = ''
    for elem in flags:
        logging.debug('key %s value %s' % (elem, flags[elem]))
    	if (flags[elem]):
            cppcheckArg += '%s=%s ' % (elem, flags[elem])
    	else:
    	    cppcheckArg += '%s ' % elem

    # add files/packages to argument list
    for elem in change_list:
        logging.debug('location: %s' % elem)
        changefile = args.src + '/' + elem
        cppcheckArg += '%s ' % changefile

    # run cppcheck
    logging.debug('Running cppcheck %s with arguments %s ' % (args.ccbin, cppcheckArg))
    returncode = os.system('echo %s %s >cppcheck.log 2>CIresult.xml' % (args.ccbin, cppcheckArg))

    logging.debug('cppcheck completed with exit code %d ' % (returncode))
    if (returncode != 0):
            logging.error('cppcheck returned with exit code %d' % returncode)

    return

def main():

    # get command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-m","--merge-request-id",dest="mr_id",required=True,type=int,help="(unique) ID of merge request (not the project specific IID)")
    parser.add_argument("-p","--project-name",dest="project_name",required=True,help="GitLab project with namespace (e.g. user/my-project)")
    parser.add_argument("-t","--token",required=True,help="private GitLab user token")
    parser.add_argument("-u","--url",default="http://hercules.ph.ed.ac.uk",help="URL of GitLab instance")
    parser.add_argument("-v","--verbose",default="INFO",choices=["DEBUG","INFO","WARNING","ERROR","CRITICAL"],help="verbosity level")
    parser.add_argument("-c","--ccbin",required=True,help='cppcheck binary location')
    parser.add_argument("-s","--src",required=True,help='relative source location')
    parser.add_argument("-f","--filerun",required=False,default=False,help='Run over explicit file list rather than package grouping', action='store_true')
    parser.add_argument("--max",required=False,default=5,help='Limit on file or directory arguments to cppcheck (default is 5, 0 is no limit)')
    args = parser.parse_args()

    # set logging
    logging.basicConfig(filename='cppcheck-run.log',filemode='w',level=logging.getLevelName(args.verbose),format='%(asctime)s %(levelname)-10s %(message)s')
    logging.debug("parsed arguments:\n" + repr(args))

    # run cppcheck with list of files or packages affected
    run_cppcheck(get_change_list(args), args)

    return

if __name__ == '__main__':
    main()
