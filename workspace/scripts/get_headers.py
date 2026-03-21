import urllib.request, os, json

api_key = os.environ.get("MATON_API_KEY")

def get_gmail(url):
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {api_key}")
    try:
        return json.loads(urllib.request.urlopen(req).read())
    except Exception as e:
        return {}

# Drafts
drafts = get_gmail("https://gateway.maton.ai/google-mail/gmail/v1/users/me/drafts?maxResults=10").get("drafts", [])
for d in drafts:
    msg = get_gmail(f"https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages/{d['message']['id']}?format=metadata")
    headers = msg.get("payload", {}).get("headers", [])
    to = next((h["value"] for h in headers if h["name"] == "To"), None)
    subj = next((h["value"] for h in headers if h["name"] == "Subject"), None)
    print("DRAFT:", to, subj)

# Sent
sent = get_gmail("https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages?labelIds=SENT&maxResults=10").get("messages", [])
for m in sent:
    msg = get_gmail(f"https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages/{m['id']}?format=metadata")
    headers = msg.get("payload", {}).get("headers", [])
    to = next((h["value"] for h in headers if h["name"] == "To"), None)
    subj = next((h["value"] for h in headers if h["name"] == "Subject"), None)
    print("SENT:", to, subj)
