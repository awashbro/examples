
# Performance Optimization of LHC Workload at HPC Facilities

## Background

Experiments on the Large Hadron Collider (LHC) are exploring methods to exploit national-class supercomputing (HPC) facilities as a significant source of computing power. However there are many challenges to overcome for wider adoption such as: limited external connectivity, a specialized software stack, and a completely different job submission model.

One particular issue I felt warranted a more detailed analysis. It was found that the workload performance did not scale adequately on HPC with increasing computing power and limited the effectiveness of the allocated time on the facility. This was primarily thought to be due to the dependence on HPC shared filesystems which tended to perform badly when handling data (and subsequent metadata) for large volumes of small files.

This analysis was used to confirm this suspicion on a candidate HPC site (ARCHER, the UK’s National Supercomputing Facility) with verification from other HPC sites elsewhere. The analysis also allowed performance improvements to be assessed by alternative approaches - such as moving the bulk of file operations into a filesystem residing in compute node memory.

## Steering

A batch job steering framework was introduced as part of this study in order to control the output from thousands of test jobs. For each batch job a unique submission script was created pointing to a distinct input data slice to be processed. Job output had to be then gathered into a consistent structure in order for log analysis to be more efficient at scale. This automation step saved a considerable amount of time over manual submission and verification.

The steering script `steering/gensub.sh` generated a unique batch job script based on the template file `steering/athenalaunch.tmpl`which in turn launched the payload script `steering/athenalaunch.sh`

## Analysis

The analysis step focused on two key areas - *application timing* and *file access*.

Timing information was extracted from the application logs and batch system job output. Although the application logs were unstructured there was enough of a pattern was available to use *regex* methods to extract job walltime and the timing of individual phases of the application (e.g intialisation, main processing loop). Timing values could then be directly compared across tests as the number of concurrent application processes was scaled horizontally across HPC compute nodes.  The extraction process is detailed in the python scripts `analysis/evttiming-hist.py`, `analysis/extract-timing-info.py` and `analysis/walltime-from-output.py`

File access data was collected by using **loggedFS** to trace all file access commands during the lifetime of the application execution. Here, the *frequency* of reads and writes and the *number of files* accessed were of interest. The scale of the issue could be quantified and whether there existed "hot files" that account for the bulk of the metadata operations. The parsing and visualisation of *loggedFS* output is demonstrated in `analysis/file-analysis.py`

## Further reading

Please see [this presentation](https://indico.cern.ch/event/404077/contributions/1849729/attachments/1152847/1655701/ajw-GridPP35-HPC.pdf) for more information on the motivation behind this study.
