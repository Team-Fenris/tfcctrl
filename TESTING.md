# Testing methods


1. Run `python3 main.py` to run the program.

This will start a local HTTP-, HTTPS- and DNS-server.

The Pcap capture will also start. A Pcap file will be generated with a timestamp `YYYYMMDDhhmmss.pcap`

2. You can in the [config.yaml](modules/config.yaml) file edit the *debug* parameter, which will give you a lot of debugging information.

In this file you can also deactivate the *api* parameter, which will not run any requests to an external API.

The IP addresses set in the file is dummy IP addresses, which you will need to change to the Django API server.
