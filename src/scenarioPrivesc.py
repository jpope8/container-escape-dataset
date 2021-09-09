import command_line
import random

class ScenarioPrivesc:

    def __init__(self):
        self._name = 'privesc'
        self._annotationFile = None # Set later in init

    def getName(self):
        """
        Gets the name of the scenario.
        """
        return self._name

    def init(self, scheduler, experimentSeconds, annotationFile):
        """
        Setup any resources for the scenario.
        Logging is not active.
        """
        self._annotationFile = annotationFile
        
        # Start the container for unauthorized writing to host.

        # Clean up any previous attacks
        self.execute( 'sudo rm /etc/sudoers.d/010_testuser-nopasswd' )

        # Start the container
        self.execute( 'docker run -d=true --rm --name ESCAPE_B -v /:/privesc -it alpine_volume_privesc /bin/sh' )
        
        # Schedule the escape/attack
        attackSecond = random.randint(1, experimentSeconds)
        print( 'SCENARIO B: Schedule to attack at second ' + str(attackSecond) )
        scheduler.enter( attackSecond, 1, self.onEvent )

    def start(self):
        """
        May be called multiple times during experiment.
        Logging is active.
        """

    def onEvent(self):
        """
        Event occurred.  For example execute a series of
        commands to carry out an attack.
        """
        # Order matters, need annotation to occur before the attack starts
        self._annotationFile.annotateName( self._name )
        # Container Escape and Attack B (modify files from container)
        #self.execute( 'docker exec -it ESCAPE_B /privesc/escape.sh' )
        self.execute( 'docker exec -it ESCAPE_B /escape.sh' )
        print( 'Scenario ' + self._name + ': Attack started' )

    def stop(self):
        """
        May be called multiple times during experiment.
        Logging is active.
        """

    def destroy(self):
        """
        Tears down the scenario, for example, stop container.
        Logging is not active
        """
        self.execute( 'sudo docker stop ESCAPE_B' )

    def execute( self, command ):
        """
        Convenience to call execute and print out results.
        """
        result = command_line.execute( command )
        for line in result:
            print( 'Scenario ' + self._name + ': ' + line)
