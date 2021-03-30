import requests

# Request URL from the user input
url = input("Insert URL: ")

# Set up and make the test ready for print
x = requests.head(url)

# Print the callback
print(x.headers)