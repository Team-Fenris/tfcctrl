import config_with_yaml as config

class Config:
    """ Base class for reading configuration parameters from config file. """

    def __init__(self, filename='modules/config.yaml'):
        """ Instance constructor

        :param filename: configuration file (string)
        """

        # Read config parameters from config file
        self.params = config.load(filename)