import requests

url = "https://api.brevo.com/v3/smtp/email"
headers = {
    "accept": "application/json",
    "content-type": "application/json"
}
data = {
   "sender": {"name": "Sender Alex", "email": "hareemshaikh666@gmail.com"},
   "to": [{"email": "hareemshaikh2006@gmail.com", "name": "John Doe"}],
   "subject": "Hello world",
   "htmlContent": "<html><body><p>Hello, This is my first transactional email sent from Brevo.</p></body></html>"
}

response = requests.post(url, headers=headers, json=data)
print(response.status_code)
print(response.json())
