import command_line

class ScenarioZ:

    def __init__(self):
        self._name = 'Z'
        self._composeTemplate = None

    def getName(self):
        """
        Gets the name of the scenario.
        """
        return self._name

    def registerEvent(self):
        """
        Returns True if scenario requires event to be called, False otherwise.
        """
        return False

    def init(self):
        """
        Setup any resources for the scenario.
        Logging is not active.
        """
        # Start the container for unauthorized executing shell on host.
        self._composeTemplate = '/home/pi/awesome-compose/apache-php/docker-compose.yaml'

        self.execute( 'sudo docker-compose -f ' + self._composeTemplate +  ' build' )
        self.execute( 'sudo docker-compose -f ' + self._composeTemplate +  ' up --no-start' )
        self.execute( 'sudo docker-compose -f ' + self._composeTemplate +  ' start' )

        print( 'Scenario ' + self.getName() + ': initialized' )

    def start(self):
        """
        May be called multiple times during experiment.
        Logging is active.
        """

    def onEvent(self):
        """
        Event occurred.  Logging is active.
        """


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
        self.execute( 'sudo docker-compose -f ' + self._composeTemplate +  ' stop' )
        self.execute( 'sudo docker-compose -f ' + self._composeTemplate +  ' rm -f' )

    def execute( self, command ):
        """
        Convenience to call execute and print out results.
        """
        result = command_line.execute( command )
        for line in result:
            print( 'Scenario ' + self._name + ': ' + line)
