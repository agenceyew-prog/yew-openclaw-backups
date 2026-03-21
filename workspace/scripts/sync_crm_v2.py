import urllib.request, os, json, urllib.parse

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

# 1. Get drafts
drafts_resp = api_call("https://gateway.maton.ai/google-mail/gmail/v1/users/me/drafts?maxResults=20")
draft_msgs = drafts_resp.get("drafts", [])
draft_emails = []
for d in draft_msgs:
    msg = api_call(f"https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages/{d['message']['id']}?format=metadata&metadataHeaders=To")
    headers = msg.get("payload", {}).get("headers", [])
    to = next((h["value"] for h in headers if h["name"] == "To"), None)
    if to: draft_emails.append(to.lower())

# 2. Get sent
sent_resp = api_call("https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages?labelIds=SENT&maxResults=20")
sent_msgs = sent_resp.get("messages", [])
sent_emails = []
for m in sent_msgs:
    msg = api_call(f"https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages/{m['id']}?format=metadata&metadataHeaders=To")
    headers = msg.get("payload", {}).get("headers", [])
    to = next((h["value"] for h in headers if h["name"] == "To"), None)
    if to: sent_emails.append(to.lower())

# 3. Read Sheet
sheet_id = "1fIaChyoYhRt0RmsBIS7Z4SbSRukkXAwRZ5y01_uIVVQ"
sheet_meta = api_call(f"https://gateway.maton.ai/google-sheets/v4/spreadsheets/{sheet_id}")
sheet_name = sheet_meta.get("sheets", [{}])[0].get("properties", {}).get("title", "Feuille 1")

url_values = f"https://gateway.maton.ai/google-sheets/v4/spreadsheets/{sheet_id}/values/{urllib.parse.quote(sheet_name)}!A:R"
values = api_call(url_values).get("values", [])

if not values:
    print("No sheet data")
    exit(0)

header = values[0]
try:
    email_col = header.index("Email")
    status_col = header.index("Statut Contact")
except ValueError:
    print("Missing required columns in sheet")
    exit(0)

updates = []

def is_in_list(target_email, email_list):
    target_email = target_email.lower().strip()
    for e in email_list:
        if target_email in e: return True
    return False

for i, row in enumerate(values):
    if i == 0: continue
    if len(row) <= email_col: continue
    
    email = row[email_col].strip()
    if not email: continue
    
    current_status = row[status_col] if len(row) > status_col else ""
    new_status = None
    
    if is_in_list(email, sent_emails) and "michael.philibert" not in email.lower() and "test" not in email.lower():
        if current_status != "Email envoyé":
            new_status = "Email envoyé"
    elif is_in_list(email, draft_emails):
        if current_status != "Brouillon préparé":
            new_status = "Brouillon préparé"
            
    if new_status:
        # Check if the row length is enough, if not, we still update the cell
        col_letter = chr(ord('A') + status_col)
        row_num = i + 1
        range_to_update = f"{sheet_name}!{col_letter}{row_num}"
        updates.append({
            "range": range_to_update,
            "values": [[new_status]]
        })

if updates:
    update_url = f"https://gateway.maton.ai/google-sheets/v4/spreadsheets/{sheet_id}/values:batchUpdate"
    payload = {
        "valueInputOption": "USER_ENTERED",
        "data": updates
    }
    res = api_call(update_url, data=payload, method="POST")
    print(f"UPDATED {len(updates)} rows.")
else:
    print("NO_UPDATES")
