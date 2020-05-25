import requests

API_ENDPOINT = "https://hooks.slack.com/services/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"
data = {'payload':'{"text": "This is a line of text in a channel.\nAnd this is another line of text."}'} 

r = requests.post(url = API_ENDPOINT, data = data) 
print(r)