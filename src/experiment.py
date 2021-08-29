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

from scenarioA import ScenarioA
from scenarioB import ScenarioB
from scenarioZ import ScenarioZ

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


def configAudit(rulesDir, auditDir):
    """
    Sets up the auditd.conf file and copies to /etc/audit.
    Should be called before running 'sudo service auditd start'.
    Note that the auditd logging directory is set to auditDir
    (versus default of /var/logs/audit).
    """
    #infilename  = os.path.join(rulesDir, 'audit.temp')
    #outfilename = os.path.join(rulesDir, 'audit.conf')
    #infile = InStream('../')
    
    # First check if we have copied original audit.conf as a backup
    if( not path.exists('/etc/audit/audit.backup') ):
        execute( 2, 'sudo cp /etc/audit/auditd.conf /etc/audit/auditd.backup' )
    # Now copy our audit.conf to the etc directory to be used by auditd service
    templateFilename  = os.path.join(rulesDir, 'auditd.conf.template')
    auditconfFilename = os.path.join(rulesDir, 'auditd.conf') # NB git ignores
    
    templateFile  = InStream(templateFilename)
    auditconfFile = OutStream(auditconfFilename)
    while( templateFile.hasNextLine() ):
        line = templateFile.readLine()
        if( line.startswith('log_file = ') ):
            auditfilepath = os.path.join(auditDir, 'audit.log')
            # We need to auditd.conf reference to be absolute instead of relative
            line = 'log_file = ' + os.path.abspath(auditfilepath)
        auditconfFile.writeln( line )
    del(templateFile)
    del(auditconfFile)
    
    execute( 2, 'sudo cp ' + auditconfFilename + ' /etc/audit/auditd.conf' )
    

def annotate( scenario, scenarioTime, logDir ):
    """
    Writes to annotation file the specified scenarioDate.
    """
    #if( scenarioTime is None ):
    #    scenarioTime = time.time()
    scenarioDate = fileutil.formatTime( scenarioTime )
    # Save annotation
    annotationFile = OutStream( os.path.join( logDir , 'annotated.txt'), append=True)
    annotationFile.writef( '%.3f:{"scenario":"%s", "date":"%s"},\n',
                      scenarioTime, scenario.getName(), scenarioDate )
    del( annotationFile )

#
# Test main function
#
def main():
    if( len(sys.argv) != 4 ):
        print('  Usage: <time in minutes> <directory to place log files> <attack scenario "A" | "B" | "None">')
        print('Example: 1 B')
        return

    seconds  = int(sys.argv[1]) * 60
    logDir   = sys.argv[2]
    scenarioName = sys.argv[3] # expect "A" or "B"
    
    # Verify that the log dir exists and we can write to it
    auditDir      = os.path.join(logDir, 'audit')
    systemDir     = os.path.join(logDir, 'system')
    experimentDir = os.path.join(logDir, 'experiment')
    
    if( not path.exists(logDir) ):
        print( 'Specified log directory does not exist, please create first: ' + logDir )
        return
    if( not path.exists(auditDir) ):
        os.mkdir(auditDir)
    if( not path.exists(systemDir) ):
        os.mkdir(systemDir)
    if( not path.exists(experimentDir) ):
        os.mkdir(experimentDir)
    

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
        annotate(scenario, scenarioTime, logDir)

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
    # Make sure ownnership and permissions are correct for rules files
    # sudo chown root:root ../rules/*.rules
    
    rulesDir = os.path.abspath( '../rules/' )
    for entry in os.listdir('../rules/'):
        #if( os.path.isfile(filefolder) and filefolder.endswith('.rules') ):
        rulesfile = os.path.join(rulesDir, entry)
        if( os.path.isfile(rulesfile) and entry.endswith('.rules') ):
            #print( 'File: ' + str(rulesfile) )
            execute( 2, 'sudo chown root:root ' + rulesfile )
            execute( 2, 'sudo chmod 644 ' + rulesfile )
    #execute( 2, 'sudo chown root:root ' + rulesDir + '*.rules' )
    #execute( 2, 'sudo chmod 644 ' + rulesDir + '*.rules' )
    #execute( 2, 'sudo ls -la ' + rulesDir + '*.rules' )
    #execute( 2, 'sudo ls -la ' + rulesDir )
    
    # Make sure the auditd.conf file is setup correctly, use our custom file
    configAudit( rulesDir, auditDir )
    
    #---------------------------------#
    # Step 2: Start system logging
    #---------------------------------#
    delaySeconds = 1
    systemLogger = SystemLogger( systemDir, delaySeconds )
    systemLogger.start(daemon=True) # keeps from possibly hanging
    
    #---------------------------------#
    # Step 2: Start audit logging
    #---------------------------------#
    execute( 2, 'sudo service auditd start' )
    
    # Load the base config, this erases any previous rules
    loadRule( rulesDir, '10-base-config.rules' )

    # Now try to exclude the instrumentation processes
    monitor_pid.exclude('systemlogger.py')
    monitor_pid.exclude('experiment.py')

    # Now load the bulk of the rules
    loadRule( rulesDir, '10-procmon.rules' )
    loadRule( rulesDir, '30-stig.rules' )
    loadRule( rulesDir, '31-privileged.rules' )
    loadRule( rulesDir, '33-docker.rules' )
    loadRule( rulesDir, '41-containers.rules' )
    loadRule( rulesDir, '43-module-load.rules' )
    loadRule( rulesDir, '71-networking.rules' )
    loadRule( rulesDir, '99-finalize.rules' )

    # After starting scenarios so we capture their docker processes
    monitor_pid.monitor( 'docker-proxy' );

    # Sanity check to see auditd logging is working
    auditfile = os.path.join(auditDir, 'audit.log')
    execute( 2, 'sudo ls -la ' + auditfile )
    # Wait until end to save the audit rules used in the experiment

    

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
    
    #Creates a new experiment folder with the scenarioDate
    #in the /storage/logs/experiment/ directory.
    #Moves all auditd and system log files to this folder.
    scenarioDate = fileutil.formatTime( scenarioTime )
    
    # Check to see if file is too big, if so, archive
    # List all files in a directory using os.listdir
    experimentpath = os.path.join(experimentDir, scenarioDate)
    os.mkdir(experimentpath)

    # Save the audit and system logs in the experiment folder
    saveLogs( auditDir,  experimentpath, rename=True )
    saveLogs( systemDir, experimentpath, rename=False )
    
    # Save the loaded rules used in the experiment folder
    result = command_line.execute( 'sudo auditctl -l' )
    rulesfilename = os.path.join(experimentpath, 'auditrules.txt')
    output = OutStream(rulesfilename)
    for line in result:
        output.writeln(line)
    del(output)
    
    # Now remove all docker volumes
    docker_volume.removeAll()


if __name__ == '__main__':
    main()
