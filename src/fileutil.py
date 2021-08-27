import os
import sys
import time
from datetime import datetime

#
# Common utility functions for files.
#

FORMAT = '%Y-%m-%dT%H%M%S'

def makeFilename():
    """
    Creates a new file name based on the current time.
    For example, 2021-07-27T140116
    """
    return datetime.utcnow().strftime(FORMAT)

def getNameFromDate( filepath ):
    """
    Returns a str based on the file's last modified date.
    For example, returns 2021-07-26T161114
    """
    epochtime = modified(filepath)
    d = time.strftime(FORMAT, time.localtime( epochtime ))
    return d

def formatTime( epochTime=None ):
    """
    Returns format compatible to use as a filename.
    If epochTime is None then the current time is used.
    e.g. 2021-07-27T121355
    """
    if(epochTime is None):
        epochTime = time.time()
    return time.strftime(FORMAT, time.localtime( epochTime ))

def modified( filepath ):
    """
    Gets the file's last modified time in seconds since epoch.
    """
    stat = os.stat(filepath)
    return stat.st_mtime


def getFileSize( filepath ):
    """
    Gets the file size in bytes.
    """
    stats = os.stat( filepath )
    return stats.st_size


def main():
    filepath = sys.argv[1]
    date = getNameFromDate(filepath)
    print('modified = ' + date )

if __name__ == '__main__':
    main()
