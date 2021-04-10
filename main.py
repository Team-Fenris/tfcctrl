from modules.httpsserver import FenrisHTTPSServer
from modules.config import Config
from modules.httpserver import FenrisHTTPServer
from modules.dnsserver import FenrisDNSServer
from modules.api import FenrisApi
from modules.pcap import Pcap
import time, json

# Start of program
if __name__ == "__main__":

    # Hand over config parameters and start the HTTP server
    http_server = FenrisHTTPServer()
    http_server.start()

    # Hand over config parameters and start the HTTPS server
    https_server = FenrisHTTPSServer()
    https_server.start()

    # Hand over config parameters and start the DNS server
    dns_server = FenrisDNSServer()
    dns_server.start()

    # API settings for use with Pcap later on
    CONFIG=Config()
    CFG_PARAM=CONFIG.params.getProperty("api")
    API_URL=CONFIG.params.getProperty("pcap")["api_url"]
    API=FenrisApi()

    # Capture Pcaps
    try:
        print("FenrisBox: Starting Pcap capturing. Press CTRL + C to cancel.")
        pcap = Pcap()
        pcap.capturePcap()
    except KeyboardInterrupt:
        print("KeyboardInterrupt detected. Exiting program.")
    except PermissionError:
        print("PermissionError detected. Something is wrong.")
    except OSError as e:
        print(f"OSError detected: {e}. Please restart program.")

    if CFG_PARAM["api"]:
        print("FenrisBox: Writing Pcap data to JSON file.")
        pcap.pcap_data = json.dumps(pcap.pcap_data, indent=2)
        with open('pcap.json', "w") as pcap_json_file:
            pcap_json_file.write(pcap.pcap_data)

        print("FenrisBox: Reading Pcap data from JSON file.")
        with open('pcap.json') as json_file:
            data = json.load(json_file)
            print("FenrisAPI: Sending Pcap data to external API. This may take a while, be patient..")
            for pcap_api_data in data:
                API.send(API_URL, pcap_api_data)
                time.sleep(2)
                
                if CFG_PARAM["debug"]:
                    print("API DEBUG DATA (JSON):")
                    print(pcap_api_data)
                    print("------------------------------------------------------------------------------------------------------")