#!/usr/bin/env python3
"""
NAME
    calanam.py - Housekeeping concurrent request log & out files

SYNOPSYS
    calanam.py [ARGUMENTS]

ARGUMENTS

    $APPLCSF/log
            Directory containing concurrent requests log/out files.

    Archive Directory
            Archive directory to move old concurrent requests log/out files.
            If directory doesn't exist script will create.

    Threshold
            How old concurrent requests log/out files need to be moved to
            archive directory
            Value need to be a integer and is represented in days.

EXAMPLE
    calanam.py /opt/app/OMSUAT3/apps/comn/tmp/conc/log \
    /opt/app/OMSUAT3/apps/comn/tmp/conc/log_archive 15

    calanam.py
        - Script Name
    /opt/app/OMSUAT3/apps/comn/tmp/conc/log
        - Concurrent requests log location
    /opt/app/OMSUAT3/apps/comn/tmp/conc/log_archive
        - Archive directory to move files
    15
        - 15days old concurrent request log/out files will be moved to
          above archive directory
"""
import os
import sys
import shutil
import datetime
import socket
import time
import re


def usage():
    print('\nUsage: ', sys.argv[0], '<log_directory> <archive_dir> \
    <archival time in days>\n')
    sys.exit(2)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('[ERROR]:Not enough arguments passed...')
        usage()

    currentDT = datetime.datetime.now()
    hostname = socket.gethostname()
    logdir = sys.argv[1]
    logarchdir = sys.argv[2]
    threshold = int(sys.argv[3]) * 86400
    reqslist = os.path.join(os.getcwd(), 'calanam_reqs_' +
                            str(datetime.datetime.now()) + '.txt')
    try:
        freqs = open(reqslist, 'w+')
        freqs.write("List of requests whose log/out files are moved to \
                    archivedir \n")
    except IOError as Err:
        print('[%s]:[%s]:[ERROR]:Unable to create file %s'
              % (datetime.datetime.now(), hostname, reqslist))

    if not os.path.isdir(logdir):
        print('[ERROR]:Invalid directory %s', sys.argv[1])
        sys.exit(2)

    if not os.path.isdir(logarchdir):
        print('[%s]:[%s]:[INFO]:Archive directory %s is missing, creating now'
              % (datetime.datetime.now(), hostname, logarchdir))
        try:
            os.mkdir(sys.argv[2])
        except IOError as Err:
            print('[%s]:[%s]:[ERROR]: Failed to create directory due to %s'
                  % (datetime.datetime.now(), hostname, Err))
    try:
        logfiles = os.listdir(logdir)
        print('[%s]:[%s]:[INFO]:Total number of files %s'
              % (datetime.datetime.now(), hostname, len(logfiles)))
    except IOError as Err:
        print(Err)
        sys.exit(2)

    for logfile in logfiles:
        fulllogname = os.path.join(logdir, logfile)
        # Only concurrent request log & out files are moved to archive dir
        if os.path.isfile(fulllogname) and re.search(r'^l.*req$', logfile) \
           or re.search(r'^o.*out$', logfile):
            tdiff = int(time.time() - os.path.getmtime(fulllogname))
            if tdiff > threshold:
                print('[%s]:[%s]:[INFO]:Moving file %s to %s'
                      % (datetime.datetime.now(), hostname, logfile,
                         logarchdir))
                try:
                    shutil.move(fulllogname, logarchdir)
                    freqs.write(re.sub(r'[a-zA-Z]', '', logfile).strip('.')
                                + '\n')
                except IOError as Err:
                    print('[%s]:[%s]:[ERROR]:Unable to move file due to %s'
                          % (datetime.datetime.now(), hostname, Err))
                    exit()
    freqs.close()
