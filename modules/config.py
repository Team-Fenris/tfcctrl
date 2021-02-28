import yaml

class Config:
    """ Base class for all configuration parameters. """

    def __init__(self, filename='modules/config.yaml'):
        """ Instance constructor
        :param filename: configuration file (config.yaml)
        """

        # Set the filename for the config file
        self.filename = filename

        # Append each config parameter to an list
        self.readConfigFile()

    def readConfigFile(self):
        """ Read the file and add config parameters to instance. """

        # Open the configuration file and set config parameters
        with open(self.filename, 'r') as yml_file:
            self.config_json = yaml.load(yml_file)

    def getConfigParameter(self, config_section):
        """ Accessor method for displaying configuration parameters as requested.
        :return: parameter (str)
        """

        # Return given config parameters as asked for
        return(self.config_json(config_section))