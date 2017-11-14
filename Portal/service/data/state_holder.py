class StateHolder:
    __instance = None

    @staticmethod
    def get_instance():
        """
        Will return the manager instance.

        :return: The manager instance.
        """
        if StateHolder.__instance is None:
            StateHolder()
        return StateHolder.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if StateHolder.__instance is not None:
            raise Exception("Only one instance of the StateHolder should exist!")
        else:
            StateHolder.__instance = self

        self.state = {}
