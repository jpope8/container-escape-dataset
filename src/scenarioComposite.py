
class ScenarioComposite:
    """
    ScenarioComposite
    """

    def __init__(self):
        self._name = 'Composite'
        self._scenarios = list()


    def add( self, scenario ):
        """
        Adds scenario to the composite list
        """
        self._scenarios.append(scenario)

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
        for scenario in self._scenarios:
            print('Scenario ' + scenario.getName() )
            scenario.init(scheduler, experimentSeconds, annotationFile)


    def start(self):
        """
        May be called multiple times during experiment.
        Logging is active.
        """
        for scenario in self._scenarios:
            scenario.start()

    def stop(self):
        """
        May be called multiple times during experiment.
        Logging is active.
        """
        for scenario in self._scenarios:
            scenario.stop()

    def destroy(self):
        """
        Tears down the scenario, for example, stop container.
        Logging is not active
        """
        for scenario in self._scenarios:
            scenario.destroy()

