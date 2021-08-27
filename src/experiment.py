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

from outstream import OutStream
from systemlogger import SystemLogger

from scenarioA import ScenarioA
from scenarioB import ScenarioB
from scenarioZ import ScenarioZ

def execute( number, command ):
    """
    Convenience to call execute and print out results.
    """
    result = command_line.execute( command )
    for line in result:
        print('Step' + str(number) + ': ' + line)

#def loadRule( rulefilename ):
#    # Make sure ownnership and permissions are correct, then load
#    uid = 0
#    gid = 0
#    os.chown( rulefilename, uid, gid )
#    os.chmod( rulefilename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
#    execute( 1, 'sudo auditctl -R ' + rulefilename )
def loadRule( rulefilename ):
    # Make sure ownership and permissions are correct, then load
    execute( 1, 'sudo chown root:root ../rules/' + rulefilename )
    execute( 1, 'sudo chmod 644 ../rules/' + rulefilename )
    execute( 1, 'sudo auditctl -R ../rules/' + rulefilename )

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
        if( filename.startswith("audit.log") or filename.endswith(".log") ):
            #print(entry)
            #archive(auditfile)
            newfile = os.path.join( experimentpath, filename )
            if( rename ):
                newfilename = fileutil.getNameFromDate(logfile)
                newfile = os.path.join( experimentpath, newfilename + '_audit.log' )
            #os.rename( logfile, newfile )
            # Sadly have to sudo for the audit directory
            execute( 9, 'sudo mv ' + str(logfile) + ' ' + str(newfile) )

def saveExperiment( scenarioTime ):
    """
    Creates a new experiment folder with the scenarioDate
    in the /storage/logs/experiment/ directory.
    Moves all auditd and system log files to this folder.
    """
    scenarioDate = fileutil.formatTime( scenarioTime )
    # Check to see if file is too big, if so, archive
    # List all files in a directory using os.listdir
    experimentpath = '/storage/logs/experiment/' + scenarioDate
    os.mkdir(experimentpath)

    saveLogs( '/storage/logs/audit/', experimentpath, rename=True )
    saveLogs( '/storage/logs/system/', experimentpath, rename=False )


def annotate( scenario, scenarioTime ):
    """
    Writes to annotation file the specified scenarioDate.
    """
    #if( scenarioTime is None ):
    #    scenarioTime = time.time()
    scenarioDate = fileutil.formatTime( scenarioTime )
    # Save annotation
    annotationFile = OutStream('annotated.txt', append=True)
    annotationFile.writef( '%.3f:{"scenario":"%s", "date":"%s"},\n',
                      scenarioTime, scenario.getName(), scenarioDate )
    del( annotationFile )

#
# Test main function
#
def main():
    if( len(sys.argv) != 3 ):
        print('  Usage: <time in minutes> <attack scenario "A" | "B" | "None">')
        print('Example: 1 B')
        return

    seconds  = int(sys.argv[1]) * 60
    scenarioName = sys.argv[2] # expect "A" or "B"

    #---------------------------------#
    # Step 1: Initialize scenario.
    #---------------------------------#
    scenarioTime = None
    scenario = None
    if( scenarioName == "A" ):
        scenario = ScenarioA()
    elif( scenarioName == "B" ):
        scenario = ScenarioB()
    else:
        # Normal has no event, annotate
        # catelog so similar to other experiments
        scenario = ScenarioZ()
        scenarioTime = time.time()
        annotate(scenario, scenarioTime)

    simulateEvent = scenario.registerEvent()
    scenario.init() # logging not active

    #---------------------------------#
    # Step 2: Load rules and start auditd logging.
    # One approach to use /etc/audit/rules.d/*.rules and augnerules
    # Another approach is to use auditctl -R *.rules
    # We choose auditctl to avoid extra copy.
    # NB: that the first rules file deletes any previous rules
    #execute( 1, 'sudo augenrules --load' )
    # Vital that rules are owned by root and writable by root only
    # Otherwise auditctl -R fails silently and does not apply rules
    # Perhaps use if to ensure requirements are met and only chown/chmod if not
    #---------------------------------#
    execute( 2, 'sudo service auditd start' )
    loadRule( '10-base-config.rules' )

    monitor_pid.exclude('systemlogger.py') # not necessary but safe
    monitor_pid.exclude('experiment.py')

    loadRule( '10-procmon.rules' )
    loadRule( '30-stig.rules' )
    loadRule( '31-privileged.rules' )
    loadRule( '33-docker.rules' )
    loadRule( '41-containers.rules' )
    loadRule( '43-module-load.rules' )
    loadRule( '71-networking.rules' )
    loadRule( '99-finalize.rules' )

    # After starting scenarios so we capture their docker processes
    monitor_pid.monitor( 'docker-proxy' );

    # Sanity check to see auditd logging is working
    execute( 2, 'sudo ls -la /storage/logs/audit/audit.log' )

    #---------------------------------#
    # Step 2: Start system logging
    #---------------------------------#
    systemDir = '/storage/logs/system'
    delaySeconds = 1
    systemLogger = SystemLogger( systemDir, delaySeconds )
    systemLogger.start(daemon=True) # keeps from possibly hanging

    #---------------------------------#
    #Step 3: Start scenario
    #---------------------------------#
    scenario.start() # logging active

    #---------------------------------#
    # Step 4: Wait for duration of experiment
    # fire events if necessary
    #---------------------------------#
    secondsPassed = 0
    interval = 1
    attackSecond = random.randint(1, seconds)
    while(secondsPassed < seconds):
        ## SIMULATE ATTACK, EXACTLY ONCE
        if( simulateEvent is True and secondsPassed >= attackSecond ):
            scenarioTime = time.time()
            scenario.onEvent()
            annotate(scenario, scenarioTime)

            percentage = attackSecond/float(seconds)
            print('Event occured %.2f%% into experiment'%(percentage)  )

            simulateEvent = False

        ## VERBOSE TO LET USER KNOW PERCENTAGE COMPLETE
        if( secondsPassed % 60 == 0 ):
            execute( 4, 'sudo ls -la /storage/logs/audit/audit.log' )
            percentComplete = 100.0 * secondsPassed / float(seconds)
            print( 'Percent complete {0:d} / {1:d} = {2:3.2f}'.format(secondsPassed, seconds, percentComplete) )

        secondsPassed = secondsPassed + interval
        time.sleep(interval)

    #---------------------------------#
    #Step 5: Stop Scenario
    #---------------------------------#
    scenario.stop() # logging active

    #---------------------------------#
    # Step 6: Stop the system and auditd logging.
    #---------------------------------#
    systemLogger.stop()
    execute( 6, 'sudo service auditd stop' )

    #---------------------------------#
    #Step 7: Stop Scenario (ie stop containers)
    #---------------------------------#
    scenario.destroy() # logging not active

    #---------------------------------#
    # Step 8: Save off log files and clean up volumes
    #---------------------------------#
    saveExperiment( scenarioTime )
    docker_volume.removeAll()


if __name__ == '__main__':
    main()
