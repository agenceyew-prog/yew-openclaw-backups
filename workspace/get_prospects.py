import urllib.request
import urllib.parse
import os
import json
import time
import sys

MATON_API_KEY = os.environ.get("MATON_API_KEY", "")

def maton_get(url):
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {MATON_API_KEY}')
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        return json.loads(resp.read())
    except Exception as e:
        print(f"Error GET {url}: {e}")
        return None

def maton_post(url, data):
    req = urllib.request.Request(url, method='POST', data=json.dumps(data).encode())
    req.add_header('Authorization', f'Bearer {MATON_API_KEY}')
    req.add_header('Content-Type', 'application/json')
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        return json.loads(resp.read())
    except Exception as e:
        print(f"Error POST {url}: {e}")
        return None

sheet_id = '1fIaChyoYhRt0RmsBIS7Z4SbSRukkXAwRZ5y01_uIVVQ'
range_name = 'Organisateurs Majeurs!A:R'
encoded_range = urllib.parse.quote(range_name)
url = f"https://gateway.maton.ai/google-sheets/v4/spreadsheets/{sheet_id}/values/{encoded_range}"

print("Fetching sheet data...")
sys.stdout.flush()

sheet_data = maton_get(url)
if not sheet_data:
    print("Failed to fetch sheet data.")
    sys.exit(1)

values = sheet_data.get('values', [])
updates = []

print(f"Total rows: {len(values)}")
sys.stdout.flush()

for row_idx, row in enumerate(values[1:], start=2):
    email = row[7].lower().strip() if len(row) > 7 else ""
    if not email:
        continue
        
    current_status = row[14] if len(row) > 14 else ""
    
    # We only care if status isn't "Email Envoyé"
    if current_status == "Email Envoyé":
        continue
        
    time.sleep(0.1) # Rate limit
    
    # Check Sent first
    q_sent = f"to:{email} in:sent"
    sent_url = f"https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages?q={urllib.parse.quote(q_sent)}&maxResults=1"
    sent_data = maton_get(sent_url)
    
    new_status = current_status
    if sent_data and sent_data.get('messages'):
        new_status = "Email Envoyé"
    else:
        # Check Drafts
        q_draft = f"to:{email} in:draft"
        draft_url = f"https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages?q={urllib.parse.quote(q_draft)}&maxResults=1"
        draft_data = maton_get(draft_url)
        if draft_data and draft_data.get('messages'):
            new_status = "Brouillon"
            
    if new_status != current_status and new_status != "":
        print(f"Row {row_idx} ({email}): '{current_status}' -> '{new_status}'")
        sys.stdout.flush()
        updates.append({
            "range": f"Organisateurs Majeurs!O{row_idx}",
            "values": [[new_status]]
        })

if updates:
    print(f"Updating {len(updates)} rows...")
    sys.stdout.flush()
    update_url = f"https://gateway.maton.ai/google-sheets/v4/spreadsheets/{sheet_id}/values:batchUpdate"
    body = {
        "valueInputOption": "USER_ENTERED",
        "data": updates
    }
    resp = maton_post(update_url, body)
    print("Update response:", resp)
else:
    print("No updates needed.")
