# TODOS



modules/webserver.py
---------------
* Add support for different MIME-types (text/plain, application/pdf + common file types)
* Add get method for receiving configuration params from config.yaml

modules/config.py
---------------
* Create method to get parameters from config.yaml

modules/pcap.py
---------------
* Consider to use variables in accordance with [Microsoft docs](https://docs.microsoft.com/en-us/windows/win32/api/psapi/nf-psapi-getprocessimagefilenamew) (compliant with PEP8)
* Restrict traffic (reinject traffic to network stack to localhost:port)
* Reinject the packet into the network stack - localhost:80
* @classmethod

modules/api.py
---------------
* Write API to put pcap to external server


Misc
---------------
