import urllib.request, os, json

api_key = os.environ.get("MATON_API_KEY")

def get_gmail(url):
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {api_key}")
    try:
        return json.loads(urllib.request.urlopen(req).read())
    except Exception as e:
        return {}

def get_message_details(msg_id):
    url = f"https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages/{msg_id}?format=metadata&metadataHeaders=To&metadataHeaders=Subject&metadataHeaders=Date"
    return get_gmail(url)

# Drafts
drafts = get_gmail("https://gateway.maton.ai/google-mail/gmail/v1/users/me/drafts?maxResults=5").get("drafts", [])
draft_info = []
for d in drafts:
    msg = get_message_details(d["message"]["id"])
    headers = msg.get("payload", {}).get("headers", [])
    to = next((h["value"] for h in headers if h["name"] == "To"), None)
    subj = next((h["value"] for h in headers if h["name"] == "Subject"), None)
    draft_info.append({"id": d["id"], "to": to, "subject": subj})

print("DRAFTS:", json.dumps(draft_info, indent=2))

# Sent
sent = get_gmail("https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages?labelIds=SENT&maxResults=5").get("messages", [])
sent_info = []
for m in sent:
    msg = get_message_details(m["id"])
    headers = msg.get("payload", {}).get("headers", [])
    to = next((h["value"] for h in headers if h["name"] == "To"), None)
    subj = next((h["value"] for h in headers if h["name"] == "Subject"), None)
    sent_info.append({"id": m["id"], "to": to, "subject": subj})

print("SENT:", json.dumps(sent_info, indent=2))

# Sheet
sheet_id = "1fIaChyoYhRt0RmsBIS7Z4SbSRukkXAwRZ5y01_uIVVQ"
range_name = "Feuille 1!A1:R50" # Not sure of the exact name of the sheet, maybe just "A1:R" works for the first sheet. Wait, let's just get the spreadsheet details first.
url_sheet = f"https://gateway.maton.ai/google-sheets/v4/spreadsheets/{sheet_id}"
req_sheet = urllib.request.Request(url_sheet)
req_sheet.add_header("Authorization", f"Bearer {api_key}")
try:
    sheet_meta = json.loads(urllib.request.urlopen(req_sheet).read())
    sheet_name = sheet_meta["sheets"][0]["properties"]["title"]
    
    url_values = f"https://gateway.maton.ai/google-sheets/v4/spreadsheets/{sheet_id}/values/{urllib.parse.quote(sheet_name)}!A:R"
    req_values = urllib.request.Request(url_values)
    req_values.add_header("Authorization", f"Bearer {api_key}")
    values = json.loads(urllib.request.urlopen(req_values).read()).get("values", [])
    
    print("SHEET ROW COUNT:", len(values))
    if len(values) > 0:
        print("SHEET HEADER:", values[0])
        if len(values) > 1:
            print("SHEET ROW 2:", values[1])
except Exception as e:
    print("SHEET ERROR:", e)

