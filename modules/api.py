from modules.config import Config
import json
import requests

# Constants
CONFIG=Config()
CFG_PARAM=CONFIG.params.getProperty("api")

class FenrisApi:
    """ Base class for Fenris API. """
    def __init__(self):
        """ Instance constructor

        :params: config: Configuration parameters for the API (yaml)
        """
#        self.api_headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {0}'.format(self.api_token)}
        self.api_headers = {'Content-Type': 'application/json'}

    @staticmethod
    def _is_json(json_str):
        """ Check if input string is in JSON format. """
        json_str = json.dumps(json_str)
        try:
            json.loads(json_str)
        except ValueError:
            return False
        return True

    def send(self, url, data):
        """ Send to API class. """
        if self._is_json(data):
            req_callback = requests.post(url, headers=self.api_headers, json=data)
            if CFG_PARAM["debug"]:
                print("API CALLBACK:", req_callback)
        else:
            print("FenrisAPI Error: Not a JSON string.")
