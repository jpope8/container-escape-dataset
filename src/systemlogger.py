#import logging
import sys
import time
import recorder
import logging
import os
import psutil # only for logging version
import threading

import ziputil
import fileutil
#import zipfile_infolist
#from zipfile_infolist import print_info

import recorder
from recorder import Recorder

# modules for logging system information
import cpu

# Maximum file size before archiving
ONE_MB = 2**20 # 2**20 = 1MB
#MAX_LOG_SIZE = 2 * ONE_MB # for development
MAX_LOG_SIZE = 30 * ONE_MB # for production

# Use .txt as extension for file we are logging to
# Then when rolling, rename with .log extension.
# This makes it easier to know which can be archived.
TXT = '_system.txt'
LOG = '.log'



class SystemLogger:

    def __init__(self, systemDir, delaySeconds ):
        self._systemDir = systemDir
        self._delaySeconds = delaySeconds
        self._stop = False

    def _roll( self, file ):
        """
        "Roll" the log file.
        Rename with different extension.
        """
        # "Roll" the log file
        # Rename with different extension
        if( os.path.exists(file) ):
            base, ext = os.path.splitext(file)
            os.rename(file, base + LOG)

    def log(self):
        #--------------------------------------------------------------------------#
        # Derive unique filename from time to log records to
        #--------------------------------------------------------------------------#
        filename = fileutil.makeFilename() + TXT
        rec = Recorder( os.path.join(self._systemDir, filename) )

        #--------------------------------------------------------------------------#
        # Start Logging (if more state necessary, should use a class)
        #--------------------------------------------------------------------------#
        while( self._stop is False ):
            try:
                rec.incrementEventid()
                cpu.execute(rec)

                # Check to see if file is too big, if so, archive
                #print( str(rec.getFileSize()) + ' > ' + str(MAX_LOG_SIZE) + ' ? ' + str(rec.getFileSize() > MAX_LOG_SIZE) )
                if( rec.getFileSize() > MAX_LOG_SIZE ):
                    # "Roll" the log file
                    file = rec.getFile()
                    del( rec )
                    self._roll(file)

                    # Make a new recorder
                    filename = fileutil.makeFilename() + TXT
                    rec = Recorder( os.path.join(self._systemDir, filename) )


            except Exception as e:
                logging.exception( "EXCEPTION: " + str(e) )
            # Wait to achieve sampling rate

            time.sleep(self._delaySeconds)
        # This is only reached is someone calls stop.
        # It may be intended to run until killed, in which
        # case this code never gets excecuted (ie do not depend)

        # "Roll" the log file
        file = rec.getFile()
        del( rec )
        self._roll(file)

    def start(self, daemon=False):
        """
        Start the thread log, to end logging call stop
        """
        # LOGGING FOR PRODUCTION
        #logging.basicConfig( filename='transfer.log', format='%(asctime)s %(message)s', level=logging.DEBUG )
        logging.basicConfig( filename='systemlogger-exceptions.log', format='%(asctime)s %(message)s', level=logging.INFO )
        logging.info('======================================================')

        #
        # Versions matter, latest is 5.8.x
        # My raspian vm is 5.5.1
        # See Timelime at bottom of 'https://psutil.readthedocs.io/en/latest/'
        #
        #print('PSUTIL_VERSION', str(psutil.version_info) )
        logging.info('PSUTIL_VERSION ' + str(psutil.version_info) )
        logging.info('TIME: ' + str( time.time() ) )

        self._stop = False # makes re-entrant
        # Starts timer to periodically reset receiving wearable status
        systemLoggingThread = threading.Thread(target=self.log)
        systemLoggingThread.setDaemon(daemon)
        systemLoggingThread.start()

    def stop(self):
        """
        Sets flag so next time logging thread checks it will exit logging loop.
        """
        self._stop = True


#------------------------------------------------------------------------------#
# Main function (avoid scipts, better to put in this function)
#------------------------------------------------------------------------------#
def main():
    # Get command line, expect just the config filename
    if( len(sys.argv) != 3 ):
        print('  Usage: <system log directory> <delay interval in seconds>')
        print('Example: /storage/logs/system 1')
        return

    systemDir = sys.argv[1]
    delaySeconds = int( sys.argv[2] )

    logger = SystemLogger( systemDir, delaySeconds )
    logger.log()


#------------------------------------------------------------------------------#
# Call main if passed to python interpreter
#------------------------------------------------------------------------------#
if __name__ == '__main__':
    main()
