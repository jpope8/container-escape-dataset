import command_line

class ScenarioA:

    def __init__(self):
        self._name = 'A'

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
        # Start the container for unauthorized executing shell on host.
        self.execute( 'docker run -d=true --name=ESCAPE_A --rm -it --cap-add=SYS_ADMIN --security-opt apparmor=unconfined attack_a bash' )

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
        # Container Escape and Attack A (execute host shell from container)
        self.execute( 'docker exec -it ESCAPE_A /escape.sh' )
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
        self.execute( 'sudo docker stop ESCAPE_A' )

    def execute( self, command ):
        """
        Convenience to call execute and print out results.
        """
        result = command_line.execute( command )
        for line in result:
            print( 'Scenario ' + self._name + ': ' + line)
