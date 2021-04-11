# Installation manual

## Prerequisits

* Python3 installed (PATH environment variables should be checked during install, to make sure that everything works properly).

* Python3 modules installed (see details below)
* Git (nice to have to pull latest code)

## Installation

### Installing Windows
Download image from [Microsoft evaluation center](https://www.microsoft.com/en-us/evalcenter/evaluate-windows-10-enterprise).

**IMPORTANT:** To get the installation working in a virtual environment, remember to deactivate the _"autoinst.flp"_ (floppy drive) in VMware.

During Windows installation it might be good to choose "Domain join" instead of signing on a Microsoft account. You can from here create a local user. The machine needs internett access to download the latest Python, Firefox and Git.

Download and install [Firefox](https://www.mozilla.org/) (we have had issues with Microsoft Edge during the development) and set it as default browser.

Download and install [Git](https://git-scm.com/download/win) (only neccessary if you want to do development on the local machine).


### Installing Python
#### Microsoft store
1. Open Microsoft Store
2. Search for Python
3. Install the newest version
4. Open **Command prompt** with administrator privileges and update pip: `

#### Downloaded executable
1. During the first window, check "Add Python 3.x to PATH"
2. Press "Install Now"
3. Press "Disable path length limit"

External guide, if needed: [Install Python according to guide](https://www.howtogeek.com/197947/how-to-install-python-on-windows/).

**IMPORTANT:** During testing it has shown that installing both have worked differently.

If running the program `python3 main.py` fails, try `python main.py`.

If this also fails, install the other Python that you might not have installed (depends on which Python you installed; Microsoft store or executable).

_During testing, this worked:_ Install executable according to guide above (`python3 main.py` did not return any commands), and installing Microsoft store version after.

### Installing tfcctrl
1. Download the latest code from Git, or extract the code to your local machine.
2. Run **Command Prompt** with Administrator privileges.
3. Navigate to the directory where the code are located.
4. Run `pip3 install -r requirements.txt` to install the required Python modules (you might need to write `pip3.exe` instead of `pip3`).

## Windows Configuration
* Set static IP address
  - Search for "View network connections" in the search bar
  - Rightclick on the network interface, and press "Properties"
  - Choose "Internet Protocol Version 4 (TCP/IPv4)" and press "Properties"
  - Set static IP address (Set an valid IP address, network mask and gateway; in this way we can reach Django)
  - **HINT:** You can use the IP address, network mask and gateway that your DHCP have given you, for a easy proof-of-concept
  - Set the "Preferred DNS server" to "127.0.0.1"
  - **IMPORTANT:** The machine can, but should not, resolve to a FQDN. If you're trying to request a FQDN that resolves to the machine later on, it can occur errors in the software.

## Configuration of tfcctrl
Edit [config.yaml](modules/config.yaml).

### Mandatory parameter changes
The following parameters **MUST** be changed from (example):
```
  api_url: 'http://<Django API IP>:8000/api/http/'
  return_ip: <your IP address>
```
to:
```
  api_url: 'http://192.168.1.2:8000/api/http/'
  return_ip: 192.168.1.2
```
Do not change the end of the URL in `api_url`.

### Non-mandatory parameter changes
The following parameters _can_ be changed according to needs:
```
  debug: True
  api: True
```

These two parameters can be changed to `False`.

The `debug` key defines if you want to view debug data when running the program.

The `api` key defines if you want to push data to the API.
