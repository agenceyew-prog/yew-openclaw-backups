import urllib.request, os, json

api_key = os.environ.get("MATON_API_KEY")

def api_call(url, data=None, method="GET"):
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {api_key}")
    if data:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(data).encode("utf-8")
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except Exception as e:
        return {}

sheet_id = "1fIaChyoYhRt0RmsBIS7Z4SbSRukkXAwRZ5y01_uIVVQ"
sheet_meta = api_call(f"https://gateway.maton.ai/google-sheets/v4/spreadsheets/{sheet_id}")
sheet_name = sheet_meta.get("sheets", [{}])[0].get("properties", {}).get("title", "Feuille 1")

# Fetch recent drafts to report the difference
drafts_resp = api_call("https://gateway.maton.ai/google-mail/gmail/v1/users/me/drafts?maxResults=5")
draft_msgs = drafts_resp.get("drafts", [])
draft_emails = []
for d in draft_msgs:
    msg = api_call(f"https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages/{d['message']['id']}?format=metadata&metadataHeaders=To")
    headers = msg.get("payload", {}).get("headers", [])
    to = next((h["value"] for h in headers if h["name"] == "To"), None)
    if to: draft_emails.append(to.lower())

print("DRAFTS:", draft_emails)

# Fetch recent sent
sent_resp = api_call("https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages?labelIds=SENT&maxResults=5")
sent_msgs = sent_resp.get("messages", [])
sent_emails = []
for m in sent_msgs:
    msg = api_call(f"https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages/{m['id']}?format=metadata&metadataHeaders=To")
    headers = msg.get("payload", {}).get("headers", [])
    to = next((h["value"] for h in headers if h["name"] == "To"), None)
    if to: sent_emails.append(to.lower())

print("SENT:", sent_emails)

