"""
Saves annotation to file in consistent format.
"""

import time
import json
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
        
    
    def annotateName(self, annotationValue, key='annotationName'):
        """
        Saves the annotationValue using key along with the time.
        param: annotationName str, added to dict along with time, converted to json, then written
        """
        annotationsDictionary = dict()
        
        annotationsDictionary[key] = annotationValue
        self.annotateDict(annotationsDictionary)
        
    def annotateDict(self, annotationsDictionary):
        """
        Saves the annotationDictionary along with the time.
        param: annotationDictionary dict, add time, convert to json, then write to file
        """
        annotationTime = time.time()
        annotationDate = fileutil.formatTime( annotationTime )
        
        annotationsDictionary['annotationTime'] = annotationTime
        annotationsDictionary['annotationDate'] = annotationDate
        # Save annotation
        #annotationFile = OutStream( os.path.join( logDir , 'annotated.txt'), append=True)
        #self._file.writef( '%.3f:{"scenario":"%s", "date":"%s"},\n',
        #                  scenarioTime, annotationKey, scenarioDate )
        self._file.writeln( json.dumps(annotationsDictionary) + ',' )
    

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

