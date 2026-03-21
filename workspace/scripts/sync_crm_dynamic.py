import urllib.request, os, json, urllib.parse

api_key = os.environ.get("MATON_API_KEY")
if not api_key:
    print("Error: MATON_API_KEY is not set.")
    exit(1)

sheet_id = "1fIaChyoYhRt0RmsBIS7Z4SbSRukkXAwRZ5y01_uIVVQ"
url_sheet = f"https://gateway.maton.ai/google-sheets/v4/spreadsheets/{sheet_id}"

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
        print(f"Error {url}:", e)
        return {}

def get_gmail_headers(url):
    data = api_call(url)
    items = data.get("drafts", data.get("messages", []))
    emails = []
    for item in items:
        msg_id = item["message"]["id"] if "message" in item else item["id"]
        msg_url = f"https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages/{msg_id}?format=metadata"
        msg = api_call(msg_url)
        headers = msg.get("payload", {}).get("headers", [])
        to = next((h["value"] for h in headers if h["name"] == "To"), None)
        if to:
            # Extract email address if format is "Name <email@domain.com>"
            import re
            match = re.search(r'[\w\.-]+@[\w\.-]+', to)
            if match:
                emails.append(match.group(0).lower())
            else:
                emails.append(to.lower())
    return emails

print("Fetching drafts...")
draft_emails = get_gmail_headers("https://gateway.maton.ai/google-mail/gmail/v1/users/me/drafts?maxResults=15")
print(f"Drafts found: {len(draft_emails)}")

print("Fetching sent emails...")
sent_emails = get_gmail_headers("https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages?labelIds=SENT&maxResults=15")
print(f"Sent emails found: {len(sent_emails)}")

print("Fetching sheet...")
sheet_meta = api_call(url_sheet)
if not sheet_meta or "sheets" not in sheet_meta:
    print("Error fetching sheet meta")
    exit(1)
    
sheet_name = sheet_meta["sheets"][0]["properties"]["title"]
url_values = f"https://gateway.maton.ai/google-sheets/v4/spreadsheets/{sheet_id}/values/{urllib.parse.quote(sheet_name)}!A:R"
values = api_call(url_values).get("values", [])

if not values:
    print("No data in sheet.")
    exit(1)

header = values[0]
if "Email" not in header or "Statut Contact" not in header:
    print("Missing required columns in sheet.")
    exit(1)
    
email_col = header.index("Email")
status_col = header.index("Statut Contact")

updates = []
for i, row in enumerate(values):
    if i == 0: continue
    if len(row) <= email_col: continue
    
    email = row[email_col].strip().lower()
    if not email: continue
    
    current_status = row[status_col] if len(row) > status_col else ""
    new_status = None
    
    # Check if sent
    if email in sent_emails:
        if current_status != "Email envoyé":
            new_status = "Email envoyé"
            
    # Check if draft
    elif email in draft_emails:
        if current_status != "Brouillon préparé":
            new_status = "Brouillon préparé"
            
    if new_status:
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
        "data": [{"range": u["range"], "values": u["values"]} for u in updates]
    }
    res = api_call(update_url, data=payload, method="POST")
    print(f"Updated {len(updates)} rows in CRM.")
else:
    print("CRM is up to date.")
