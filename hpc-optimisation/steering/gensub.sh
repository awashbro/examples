#!/bin/bash

# gensub.sh
# Script to generate HPC submission scripts from common template (athenalaunch.tmpl)

# Command line options
usage() { echo "Usage: $0 [-n NODES] [-e EVENTS] [-c CORES] [-t WALLTIME] [-N JOBNAME] [-S SUBSCRIPTNAME] [-T TESTDIR] [-m EMAIL]" 1>&2; exit 1; }

while getopts ":n:e:c:t:N:S:T:m:" o; do
    case "${o}" in
    n) NODES=${OPTARG};;
    e) EVENTS=${OPTARG};;
    c) CORES=${OPTARG};;
    t) WALLTIME=${OPTARG};;
    N) JOBNAME=${OPTARG};;
    S) SUBSCRIPTNAME=${OPTARG};;
    T) TESTDIR=${OPTARG};;
    m) EMAIL=${OPTARG};;
    *)
    usage
    ;;
    esac
done
shift $((OPTIND-1))

# set defaults where not defined
if [ -z "$NODES" ]; then
    NODES=1
fi
if [ -z "$EVENTS" ]; then
    EVENTS=10
fi
if [ -z "$CORES" ]; then
    CORES=36
fi
if [ -z "$WALLTIME" ]; then
    WALLTIME="2:0:0"
fi
if [ -z "$JOBNAME" ]; then
    JOBNAME="ath-N${NODES}E${EVENTS}C${CORES}"
fi
if [ -z "$SUBSCRIPTNAME" ]; then
    SUBSCRIPTNAME="ath-N${NODES}E${EVENTS}C${CORES}.sub"
fi
if [ -z "$TESTDIR" ]; then
    THISPWD=`pwd`
    TESTDIR=`basename $THISPWD`
fi

# overlay values onto template
sed -e "s/NODES/$NODES/" -e "s/EVENTS/$EVENTS/"  -e "s/CORES/$CORES/"  -e "s/WALLTIME/$WALLTIME/"  -e "s/JOBNAME/$JOBNAME/" -e "s/TESTDIR/$TESTDIR/" athenalaunch.tmpl > $SUBSCRIPTNAME
if [ ! -z "$EMAIL" ]; then
  sed -i -e "s/EMAIL/$EMAIL/" $SUBSCRIPTNAME
else
  sed -i -e "/PBS -M/d" $SUBSCRIPTNAME
fi

exit
