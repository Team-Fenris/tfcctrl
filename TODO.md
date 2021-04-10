# TODOS



modules/webserver.py
---------------
:x: Add support for different MIME-types (text/plain, application/pdf + common file types)

:white_check_mark: Add get method for receiving configuration params from config.yaml

:white_check_mark: Change server_name/client

modules/config.py
---------------
:white_check_mark: Create method to get parameters from config.yaml

modules/pcap.py
---------------
:x: Consider to use variables in accordance with [Microsoft docs](https://docs.microsoft.com/en-us/windows/win32/api/psapi/nf-psapi-getprocessimagefilenamew) (compliant with PEP8)

:x: Restrict traffic (reinject traffic to network stack to localhost:port)

:x: Reinject the packet into the network stack - localhost:80

:x: @classmethod

:x: Implement logging

:white_check_mark: Implement config class to read config.yaml

modules/api.py
---------------
:x: Write API to put pcap to external server

:white_check_mark: API for DNS

:white_check_mark: API for HTTP

:white_check_mark: API for HTTPS

Misc
---------------
