# Installation manual

## Prerequisits
* Windows 10
* Python3 installed (PATH environment variables should be checked during install, to make sure that everything works properly)
* Python3 modules installed (see details below)
* Git (nice to have to pull latest code)

## Install Python modules
### Windows
Open Command Prompt with Administrator privileges.
Navigate to the directory where the repository are located.
When in the main directory, type `pip3.exe install -r requirements.txt` into the Command Prompt.
If you have configured Python3 correctly during installation, the command should work in the Command Prompt.

### Linux
This repository are mainly planned used in Windows.
Therefore Linux is not needed, except in cases where you develop in Linux and modules needs to be installed to efficiently develop code.
If you decide to use Linux with that reason (or some else reason), type `pip3 install -r requirements.txt` into the Linux terminal to install the required modules.


## Configuration
The Windows client must be set up with static IP address, and a DNS server pointing towards 127.0.0.1 for the local DNS server script to work.

### TRC server

Install python
Install Firefox (Edge will not work properly for demonstration)
In system variables, the PATH for python must be insterted. These are the following paths for python ver. 3.9. The pathway before appdata varies from computer to computer.
~\appdata\local\Programs\python\python39
~\appdata\local\Programs\python\python39\script

Important: Close all CMD sessions after variable is set in environment
Set static IP and DNS to home address (127.0.0.1)
Alter IP address in the config.yaml. The “dnsserver return_ip” field needs to be changed to the static address set on the computer. 
Run CMD as admin
In CMD, go to the path to where main.py is
If a Windows firewall prompt, press ok and restart CMD
Run CMD again as administrator and run main.py from its directory path
