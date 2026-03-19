import urllib.request, os, json, sys, base64

MATON_API_KEY = os.environ.get("MATON_API_KEY")
if not MATON_API_KEY:
    print("Erreur: MATON_API_KEY manquante.")
    sys.exit(1)

def api_call(url):
    req = urllib.request.Request(url, method='GET')
    req.add_header('Authorization', f'Bearer {MATON_API_KEY}')
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

# Search for the sent email
query = urllib.parse.quote('is:sent basket')
url = f'https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages?q={query}&maxResults=5'
messages = api_call(url).get('messages', [])

if not messages:
    print("Aucun message trouvé.")
    sys.exit(0)

# Fetch the first match
msg_id = messages[0]['id']
msg_url = f'https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages/{msg_id}?format=full'
full_msg = api_call(msg_url)

headers = full_msg['payload'].get('headers', [])
subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
to = next((h['value'] for h in headers if h['name'] == 'To'), 'No To')

# Try to extract the body
body_data = ""
if 'parts' in full_msg['payload']:
    for part in full_msg['payload']['parts']:
        if part['mimeType'] == 'text/plain':
            body_data = part['body'].get('data', '')
            break
else:
    body_data = full_msg['payload']['body'].get('data', '')

if body_data:
    try:
        # Pad base64url if needed
        body_data += "=" * ((4 - len(body_data) % 4) % 4)
        body = base64.urlsafe_b64decode(body_data).decode('utf-8')
    except Exception as e:
        body = f"Erreur de décodage: {e}"
else:
    body = "Corps du message vide ou non text/plain."

print(f"TO: {to}")
print(f"SUBJECT: {subject}")
print("--- BODY ---")
print(body)
