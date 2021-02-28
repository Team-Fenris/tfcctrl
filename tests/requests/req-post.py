import requests

# Set requests to be sent to the server
post_req = { 'testkey': 'testvalue'}

# Request URL from the user input
url = input("Insert URL: ")

x = requests.post(url, data = post_req)

print(x.text)