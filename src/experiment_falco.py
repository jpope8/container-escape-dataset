"""
Runs an experiment.

Step 1: Initialize scenario.

Step 2: Start logging.
  > sudo service auditd start

Step 3: Start scenario.

Step 4: Wait.  Handle possible events.
  (typically more than 24 hours, depends on amount of data required)

Step 5: Stop Client Workload.

Step 6: Stop logging
  > sudo service auditd stop

Step 7: Destroy scenarios (ie stop containers).

Step 8: Save experiment and cleanup
"""

import subprocess
import os
import stat
import sys
import argparse
import time
import monitor_pid
import command_line
import docker_volume
import random
import fileutil
import threading

import os.path
from os import path

from outstream import OutStream
from instream import InStream

from systemlogger import SystemLogger
from scheduler import Scheduler
from annotationfile import AnnotationFile


def execute( number, command ):
    """
    Convenience to call execute and print out results.
    """
    #print( 'CMD: ' + command )
    result = command_line.execute( command )
    for line in result:
        if( len( line.strip() ) > 0 ):
            print('Step' + str(number) + ': ' + line)


def loadRule( rulesDir, rulesFilename ):
    """
    Loads the given rule file.
    """
    # Load the base config, this erases any previous rules
    loadruleCommand = 'sudo auditctl -R ' + os.path.join( rulesDir, rulesFilename )
    execute( 2, loadruleCommand )


def saveLogs(logpath, experimentpath, rename=False):
    """
    Moves all log files from <logpath> to <experimentpath>.
    If rename is False, files are simply moved.
    If rename is True, all log files are renamed with their modification date.
    """
    for filename in os.listdir(logpath):
        logfile = os.path.join( logpath, filename )

        if( os.path.isfile(logfile) is False ):
            continue

        #Check if the string starts with "audit.log." and ends with any [0-9] digit:
        if( filename.endswith(".log") or filename.endswith(".txt") ):
            #print(entry)
            #archive(auditfile)
            newfile = os.path.join( experimentpath, filename )
            if( rename ):
                newfilename = fileutil.getNameFromDate(logfile)
                newfile = os.path.join( experimentpath, newfilename + '_' + filename )
            #os.rename( logfile, newfile )
            # Sadly have to sudo for the audit directory
            #print('    logfile ' + str(logfile) )
            #print('    newfile ' + str(newfile) )
            execute( 9, 'sudo mv ' + str(logfile) + ' ' + str(newfile) )
    

def configFalco(rulesDir, falcoLog):
    # Setting up the falco.conf file, mainly is about configuring it to write to
    # the experiment folder.
    templateFilename = os.path.join(rulesDir, 'falco.yaml.template')
    falcoconfFilename = os.path.join(rulesDir, 'falco.yaml')

    templateFile = InStream(templateFilename)
    falcoconfFile = OutStream(falcoconfFilename)

    while (templateFile.hasNextLine()):
        line = templateFile.readLine()
        if (line.startswith('  filename:')):
            # print(falcoLog)
            line = '  filename: ' + os.path.abspath(falcoLog)
        falcoconfFile.writeln(line)
    del(templateFile)
    del(falcoconfFile)


class Experiment:
    def __init__(self, seconds, logDir, scenario):
        self._seconds = seconds
        self._logDir  = logDir
        self._scenario= scenario
        
        self._systemDir     = os.path.join(logDir, 'system')
        self._experimentDir = os.path.join(logDir, 'experiment')

        self._falcoLog = None # where logs are stored
        
        self._annotationFile = None # Set later in start
        
        self._experimentpath = None # Set later in start
        
        self._scheduler = None # set later in start
        
        self._statusInterval = 5*60 # how long to wait beofre showing experiment status
        
        # To keep track of how much time has elapsed for status
        self._previousTime = 0 # Set later in start
        self._secondsElapsed = 0 # time elapsed in seconds
        
        delaySeconds = 1
        self._systemLogger = SystemLogger( self._systemDir, delaySeconds )
        
        # Maybe this should be in start???
        if( not path.exists(self._logDir) ):
            e = 'Specified log directory does not exist, please create first: ' + self._logDir
            raise(e)
        if( not path.exists(self._systemDir) ):
            os.mkdir(self._systemDir)
        if( not path.exists(self._experimentDir) ):
            os.mkdir(self._experimentDir)


    def run(self):
        #---------------------------------#
        # Creates a new experiment folder with the scenarioDate
        # in the /storage/logs/experiment/ directory.
        #---------------------------------#
        scenarioTime = time.time()
        scenarioDate = fileutil.formatTime( scenarioTime )
        
        # Check to see if file is too big, if so, archive
        # List all files in a directory using os.listdir
        self._experimentpath = os.path.join(self._experimentDir, scenarioDate)
        # Should not exist, we keep one second granularity
        os.mkdir(self._experimentpath)

        # Create the scheduler
        self._scheduler = Scheduler(time.time, time.sleep)
        # Create/open annotatio nfile
        self._annotationFile = AnnotationFile( os.path.join( self._experimentpath , 'annotated.txt') )
        # Initialize the scenario passing quite a bit of information
        self._scenario.init(self._scheduler, self._seconds, self._annotationFile) # logging not active

        # Load rules and start falco logging
        rulesDir = os.path.abspath( '../rules_falco' )
        self._falcoLog = os.path.join(self._experimentpath, 'events.json')

        # Configure the conf file so its write to the right dir
        configFalco(rulesDir, self._falcoLog)

        #---------------------------------#
        # Step 2: Start system logging
        #---------------------------------#
        self._systemLogger.start(daemon=True) # keeps from possibly hanging

        #---------------------------------#
        # Step 2: Start falco logging
        #---------------------------------#
        # -c, the path where we load the configuration file
        # -r, the path where we load the rules file, can use multiple -r
        # -d, uses falco daemon
        # -P, where to store the pid of the falco daemon, so we can use it to kill the process later
        execute(2, 'sudo falco -c ' + rulesDir + '/falco.yaml -r ' + rulesDir + '/10-procmon.yaml ' + '-d -P ../../falco_logs/falco.pid')

        execute(2, 'ls -la ' + self._falcoLog)

         #---------------------------------#
        #Step 3: Start scenario
        #---------------------------------#
        self._scenario.start() # logging active

        #---------------------------------#
        # Step 4: Wait for duration of experiment
        # fire events if necessary
        #---------------------------------#
        
        # Schedule event to stop the experiment
        self._scheduler.enter( self._seconds, 1, self._stopExperiment )
        # self._scheduler.enter( self._statusInterval, 5, self._status ) # don't think this is triggered anyway

        # Run main schedule loop to let scenarios respond to events.
        # The _stopExperiment is a non-scenario event that will ensure
        # all subsequent events are cancelled to this loop exits.
        # In effec, this loop eventually calls _stopExperiment to clean up.
        # When this loop exits, the experiment is over.
        self._previousTime = time.time()
        self._secondsElapsed = 0
        numevents = 0
        while( not self._scheduler.empty() ):
            result = self._scheduler.run(blocking=True)
            numevents = numevents + 1
        print('main exitting, num events ' + str(numevents) )
    

    def _status(self):
        currentTime = time.time()
        eventTimeElapsed = currentTime - self._previousTime
        self._previousTime = currentTime
        self._secondsElapsed += eventTimeElapsed
        
        auditfile = os.path.join(self._auditDir, 'audit.log')
        execute( 4, 'sudo ls -la ' + auditfile )
        percentComplete = 100.0 * self._secondsElapsed / float(self._seconds)
        print( 'Percent complete {0:.0f} / {1:d} = {2:3.2f}'.format(self._secondsElapsed, self._seconds, percentComplete) )
        # Schedule next status update (may extend beyond experiment but will be canncelled)
        self._scheduler.enter( self._statusInterval, 5, self._status )
    

    def _stopExperiment(self):
        print('STOPPING EXPERIMENT' )
        # Removes eny remaining events from the scheduler
        # each event is tuple ( time, priority, action, arguments, kwargs )
        while( not self._scheduler.empty() ):
            for event in self._scheduler.queue:
                self._scheduler.cancel(event)
                print('Cancelled event: ' + str(event) )
        
        #---------------------------------#
        #Step 5: Stop Scenario
        #---------------------------------#
        self._scenario.stop() # logging active

        #---------------------------------#
        # Step 6: Stop the system and falco logging.
        #---------------------------------#
        # manually kill the process by using the process id we recorded before
        self._systemLogger.stop()
        pid_path = os.path.join(self._logDir, 'falco.pid')
        pid_file = open(pid_path, 'r')
        pid = pid_file.readline()
        execute(6, 'sudo kill ' + pid)

        # Change the permission of the events.json file, weird falco permission requirement
        execute(6, "sudo chmod 644 " + self._falcoLog)

        #---------------------------------#
        #Step 7: Stop Scenario (ie stop containers)
        #---------------------------------#
        self._scenario.destroy() # logging not active
        
        # Can be sure annotationFile can be closed
        self._annotationFile.close()

        #---------------------------------#
        # Step 8: Save off log files and clean up volumes
        #---------------------------------#
        
        # Moves all auditd and system log files to this folder.
        # Save the audit and system logs in the experiment folder
        # saveLogs( self._auditDir,  self._experimentpath, rename=True )
        saveLogs( self._systemDir, self._experimentpath, rename=False )
        
        # Save the loaded rules used in the experiment folder
        # result = command_line.execute( 'sudo auditctl -l' )
        # rulesfilename = os.path.join(self._experimentpath, 'auditrules.txt')
        # output = OutStream(rulesfilename)
        # for line in result:
        #     output.writeln(line)
        # del(output)
        
        # Now remove all docker volumes
        docker_volume.removeAll()


#
# Test main function
#
from scenarioDos import ScenarioDos
from scenarioPrivesc import ScenarioPrivesc
from scenarioGrafana import ScenarioGrafana
from scenarioComposite import ScenarioComposite
def main():
    
    # Create the scenarios that can be chosen from
    scenarios = { 'dos': ScenarioDos(),
                  'privesc': ScenarioPrivesc(),
                  'grafana': ScenarioGrafana(),
                }
    
    if( len(sys.argv) != 5  ):
        print('  Usage: <time in minutes> <directory to place log files> <scenario1> <scenario2>')
        print('Scenarios: ' + str(scenarios.keys()) )
        print('Example: 1 ../../falco_logs grafana dos')
        return

    seconds     = int(sys.argv[1]) * 60
    logDir      = sys.argv[2]
    scenarioOne = sys.argv[3] # expect "A" or "B"
    scenarioTwo = sys.argv[4]
    
    
    scenario = ScenarioComposite()
    scenario.add( scenarios[scenarioOne] )
    scenario.add( scenarios[scenarioTwo] )
        
    #annotationFile = AnnotationFile( os.path.join( logDir , 'annotated.txt') )
    experiment = Experiment( seconds, logDir, scenario )
    experiment.run()

if __name__ == '__main__':
    main()


# There are a few things that I didn't have time to work on and wasn't really a priority at the time.
# Firstly, the systemLogger never works, so the system logs have always been empty on this vm.
# Secondly, I have never tested privilege escalation attack

# Fun little thing to mention, I kinda used a trick to kill the process, another approach is to find that particular pid by using the ps command and go through it.
# Or, I believe python subprocess package has methods to kill processes, using popen if I remember it right.