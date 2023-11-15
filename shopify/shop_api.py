import requests
import json

url = "https://quickstart-1893efc4.myshopify.com/admin/api/2023-07/orders.json"

payload = {}
headers = {
  'Content-Type': 'application/json',
  'X-Shopify-Access-Token': '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'
}

response = requests.request("GET", url, headers=headers, data=payload)
all_data = response.json()['orders']

#print(response.text)
