import requests

# Set requests to be sent to the server
get_req = { 'testkey': 'testvalue' }

# Request URL from the user input
url = input("Insert URL: ")

# Set up and make the test ready for print
x = requests.get(url, params=get_req)

# Print the callback
print(x.text)