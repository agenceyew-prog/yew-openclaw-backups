import urllib.request, os, json

api_key = os.environ.get("MATON_API_KEY")
if not api_key:
    print("No MATON_API_KEY found")
    exit(1)

def get_emails(url):
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {api_key}")
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

# 1. Drafts
drafts = get_emails("https://gateway.maton.ai/google-mail/gmail/v1/users/me/drafts?maxResults=10")
print("DRAFTS:")
print(json.dumps(drafts, indent=2))

# 2. Sent
sent = get_emails("https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages?labelIds=SENT&maxResults=10")
print("SENT:")
print(json.dumps(sent, indent=2))
