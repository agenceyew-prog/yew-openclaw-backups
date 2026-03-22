import urllib.request, os, json, time

API_KEY = os.environ.get('MATON_API_KEY', '')

def req_api(url):
    req = urllib.request.Request(url)
    req.add_header('Authorization', 'Bearer ' + API_KEY)
    try:
        resp = urllib.request.urlopen(req)
        return json.load(resp)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

print("Fetching Gmail Drafts...")
# Fetch first page of drafts to see latest
drafts_resp = req_api('https://gateway.maton.ai/google-mail/gmail/v1/users/me/drafts?maxResults=50')
draft_ids = [d['message']['id'] for d in drafts_resp.get('drafts', [])] if drafts_resp else []

draft_emails = []
for msg_id in draft_ids[:10]: # Check top 10 drafts to avoid rate limits
    msg = req_api(f'https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages/{msg_id}')
    if msg:
        headers = msg.get('payload', {}).get('headers', [])
        for h in headers:
            if h['name'] == 'To':
                draft_emails.append(h['value'])

print("Fetching Sent Emails...")
sent_resp = req_api('https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages?q=in:sent&maxResults=20')
sent_ids = [m['id'] for m in sent_resp.get('messages', [])] if sent_resp else []
sent_emails = []
for msg_id in sent_ids[:10]:
    msg = req_api(f'https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages/{msg_id}')
    if msg:
        headers = msg.get('payload', {}).get('headers', [])
        for h in headers:
            if h['name'] == 'To':
                sent_emails.append(h['value'])

print("Fetching Google Sheet...")
sheet_data = req_api('https://gateway.maton.ai/google-sheets/v4/spreadsheets/1fIaChyoYhRt0RmsBIS7Z4SbSRukkXAwRZ5y01_uIVVQ/values/Organisateurs%20Majeurs')
rows = sheet_data.get('values', [])
if not rows:
    print("No rows found.")
    exit()

headers = rows[0]
email_idx = headers.index('Email') if 'Email' in headers else 7
status_idx = headers.index('Statut Contact') if 'Statut Contact' in headers else 14

print(f"Draft emails (top 10): {draft_emails}")
print(f"Sent emails (top 10): {sent_emails}")

updates = []
for i, row in enumerate(rows):
    if i == 0: continue
    if len(row) <= email_idx: continue
    email = row[email_idx].strip()
    if not email: continue
    
    current_status = row[status_idx] if len(row) > status_idx else ""
    new_status = current_status
    
    # Check if in sent emails
    if any(email.lower() in se.lower() for se in sent_emails):
        if "Envoyé" not in current_status:
            new_status = "Email Envoyé"
    elif any(email.lower() in de.lower() for de in draft_emails):
        if "Brouillon" not in current_status:
            new_status = "Brouillon prêt"
            
    if new_status != current_status:
        updates.append((i+1, email, current_status, new_status))

print("Proposed updates:", updates)
