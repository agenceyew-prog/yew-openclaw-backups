import urllib.request
import urllib.parse
import os
import json
import re

MATON_API_KEY = os.environ.get("MATON_API_KEY", "")

def maton_get(url):
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {MATON_API_KEY}')
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

def get_emails_from_messages(query):
    # Search messages
    search_url = f"https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages?q={urllib.parse.quote(query)}&maxResults=100"
    data = maton_get(search_url)
    messages = data.get('messages', [])
    emails = set()
    
    for msg in messages:
        msg_id = msg['id']
        try:
            msg_url = f"https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages/{msg_id}?format=metadata&metadataHeaders=To"
            msg_data = maton_get(msg_url)
            headers = msg_data.get('payload', {}).get('headers', [])
            for h in headers:
                if h['name'] == 'To':
                    val = h['value']
                    # extract email address like "name <email@domain.com>" -> "email@domain.com"
                    match = re.search(r'<([^>]+)>', val)
                    if match:
                        emails.add(match.group(1).lower().strip())
                    else:
                        emails.add(val.lower().strip())
        except Exception as e:
            print(f"Error fetching msg {msg_id}: {e}")
            
    return emails

def main():
    print("Fetching drafts...")
    draft_emails = get_emails_from_messages("in:draft")
    print(f"Found {len(draft_emails)} drafts: {draft_emails}")
    
    print("Fetching sent emails...")
    sent_emails = get_emails_from_messages("in:sent")
    print(f"Found {len(sent_emails)} sent emails: {sent_emails}")
    
    sheet_id = '1fIaChyoYhRt0RmsBIS7Z4SbSRukkXAwRZ5y01_uIVVQ'
    range_name = 'Organisateurs Majeurs!A:R'
    encoded_range = urllib.parse.quote(range_name)
    url = f"https://gateway.maton.ai/google-sheets/v4/spreadsheets/{sheet_id}/values/{encoded_range}"
    
    print("Fetching sheet...")
    sheet_data = maton_get(url)
    values = sheet_data.get('values', [])
    
    updates = []
    
    if len(values) > 0:
        headers = values[0]
        # Make sure column 14 (O) exists
        for row_idx, row in enumerate(values[1:], start=2): # +2 because 0-indexed + 1 for header + 1 for Google Sheets 1-indexing
            email = ""
            if len(row) > 7:
                email = row[7].lower().strip()
                
            if not email:
                continue
                
            current_status = row[14] if len(row) > 14 else ""
            new_status = current_status
            
            if email in sent_emails:
                new_status = "Email Envoyé"
            elif email in draft_emails:
                new_status = "Brouillon"
                
            if new_status != current_status and new_status != "":
                print(f"Row {row_idx} ({email}): {current_status} -> {new_status}")
                # We need to update cell O{row_idx}
                updates.append({
                    "range": f"Organisateurs Majeurs!O{row_idx}",
                    "values": [[new_status]]
                })
                
    if updates:
        print(f"Updating {len(updates)} rows...")
        update_url = f"https://gateway.maton.ai/google-sheets/v4/spreadsheets/{sheet_id}/values:batchUpdate"
        body = {
            "valueInputOption": "USER_ENTERED",
            "data": updates
        }
        
        req = urllib.request.Request(update_url, method='POST', data=json.dumps(body).encode())
        req.add_header('Authorization', f'Bearer {MATON_API_KEY}')
        req.add_header('Content-Type', 'application/json')
        
        try:
            resp = urllib.request.urlopen(req)
            print("Update response:", resp.read().decode())
        except Exception as e:
            print("Update failed:", e)
    else:
        print("No updates needed.")

if __name__ == "__main__":
    main()
