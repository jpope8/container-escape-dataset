"""
Saves annotation to file in consistent format.
"""

import time

import fileutil
from outstream import OutStream


class AnnotationFile:
    """
    AnnotationFile for specified file to provide easy way to save annotations.
    """
    def __init__(self, filename):
        # open file once, perhaps better to reduce syscalls if a lot of annotating
        self._filename = filename
        self._file = OutStream( filename, append=True)
        
    
    def annotate(self, annotationKey):
        """
        Saves the annotationKey along with the time.
        param: annotationKey str (usually scenario name)
        """
        scenarioTime = time.time()
        scenarioDate = fileutil.formatTime( scenarioTime )
        # Save annotation
        #annotationFile = OutStream( os.path.join( logDir , 'annotated.txt'), append=True)
        self._file.writef( '%.3f:{"scenario":"%s", "date":"%s"},\n',
                          scenarioTime, annotationKey, scenarioDate )
    

    def close(self):
        """
        Close the stream wrapped by self.
        """
        del(self._file)

#
# Test main function
#
def main():
    if( len(sys.argv) != 4 ):
        print('  Usage: <time in minutes> <directory to place log files> <attack scenario "A" | "B" | "None">')
        print('Example: 1 B')
        return

    seconds  = int(sys.argv[1]) * 60
    secondsPassed = 0
    interval = 1
    attackSecond = random.randint(1, seconds)
    print( 'Attack at second ' + str(attackSecond) )
    while(secondsPassed < seconds):
        ## SIMULATE ATTACK, EXACTLY ONCE
        if( simulateEvent is True and secondsPassed >= attackSecond ):
            scenarioTime = time.time()
            scenario.onEvent()
            annotate(scenario, scenarioTime, logDir)

            percentage = attackSecond/float(seconds)
            print('Event occured %.2f%% into experiment'%(percentage)  )

            simulateEvent = False

        ## VERBOSE TO LET USER KNOW PERCENTAGE COMPLETE
        if( secondsPassed % 60 == 0 ):
            execute( 4, 'sudo ls -la ' + auditfile )
            percentComplete = 100.0 * secondsPassed / float(seconds)
            print( 'Percent complete {0:d} / {1:d} = {2:3.2f}'.format(secondsPassed, seconds, percentComplete) )

        secondsPassed = secondsPassed + interval
        time.sleep(interval)

if __name__ == '__main__':
    main()

