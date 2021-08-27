import re
import os
import sys
import time
import ziputil
import logging

#
# Program intended to be run by cron to archive log files.
# Archive means (possibly rename) and zip files to reduce storage.
# We typically get about 25:1 compression with log files larger than 2MB.
#

def archive( auditFile ):
    """
    Compresses and then deletes the file.  Returns True if successful,
    Returns False if a problem occured (exception is logged).
    """
    try:
        # We do not want the whole path to be compressed, just use base name
        # os.path.basename(auditFile)
        ziputil.compress( auditFile )
        # If no error, delete the original file
        os.remove(auditFile)
        logging.info( 'File ' + auditFile +  ': successfully compressed and deleted' )
        return True

    except IOError as e:
        logging.info( 'File ' + auditFile +  ': exception compressing or deleting file: ' + str(e))
    return False




def main():
    #filepath = sys.argv[1]

    # Check to see if file is too big, if so, archive
    # List all files in a directory using os.listdir
    auditpath = '/storage/logs/audit/'
    for entry in os.listdir(auditpath):
        auditfile = os.path.join( auditpath, entry )
        #Check if the string starts with "audit.log." and ends with any [0-9] digit:
        if os.path.isfile(auditfile) and re.search("^audit.log.\d", entry):
            print(entry)
            archive(auditfile)

    # List all files in a directory using os.listdir
    systempath = '/storage/logs/system/'
    for entry in os.listdir(systempath):
        systemfile = os.path.join(systempath, entry)
        if os.path.isfile(systemfile) and entry.endswith('.log'):
            print(entry)
            archive(systemfile)

if __name__ == '__main__':
    main()
