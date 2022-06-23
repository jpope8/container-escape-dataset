import command_line
import random


class ScenarioDos:
    """
    ScenarioDos
    """

    def __init__(self):
        self._name = 'dos'
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

        # Start the container for unauthorized executing shell on host.
        self.execute( 'docker run -d=true --name=ESCAPE_DOS --rm -it --cap-add=SYS_ADMIN --security-opt apparmor=unconfined ubuntu_escape bash' )

        # Schedule the escape/attack
        attackSecond = random.randint(1, experimentSeconds)
        print( 'SCENARIO ' + self._name + ': Schedule to attack at second ' + str(attackSecond) )
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
        # Container Escape and Attack A (execute host shell from container)
        # Order matters, need annotation to occur before the attack starts
        self._annotationFile.annotateName( self._name )
        # starts attack, note that this initiates socket communication from
        # the docker "client" to the docker server "dockerd", then connects to
        # the containers and executes the shell.  So you will see about a 1/4 second
        # delay from the annotation time to when the shell is executed.
        self.execute( 'docker exec -it ESCAPE_DOS /escape.sh' )
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
        self.execute( 'docker stop ESCAPE_DOS' )

    def execute( self, command ):
        """
        Convenience to call execute and print out results.
        """
        result = command_line.execute( command )
        for line in result:
            print( 'Scenario ' + self._name + ': ' + line)
