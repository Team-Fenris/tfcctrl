import requests

# Set requests to be sent to the server
post_req = { 'testkey': 'testvalue'}

# Request URL from the user input
url = input("Insert URL: ")

# Set up and make the test ready for print
x = requests.post(url, data = post_req)

# Print the callback
print(x.text)