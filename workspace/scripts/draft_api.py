import urllib.request, os, json, base64, sys
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

MATON_API_KEY = os.environ.get("MATON_API_KEY")
if not MATON_API_KEY:
    print("Erreur: MATON_API_KEY manquante.")
    sys.exit(1)

SHEET_ID = '1fIaChyoYhRt0RmsBIS7Z4SbSRukkXAwRZ5y01_uIVVQ'
SHEET_NAME = 'Organisateurs Majeurs'
SENDER_EMAIL = 'contact@agenceyew.fr'

def api_call(url, method='GET', data=None):
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f'Bearer {MATON_API_KEY}')
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    with urllib.request.urlopen(req, data) as response:
        return json.loads(response.read().decode('utf-8'))

def create_draft(to_email, subject, body):
    encoded_subject = Header(subject, 'utf-8').encode()
    msg = MIMEText(body, 'html', 'utf-8')
    msg['to'] = to_email
    msg['from'] = formataddr((str(Header('Agence Yew', 'utf-8')), SENDER_EMAIL))
    msg['subject'] = encoded_subject
    raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
    draft_payload = {'message': {'raw': raw_message}}
    url = 'https://gateway.maton.ai/google-mail/gmail/v1/users/me/drafts'
    return api_call(url, method='POST', data=json.dumps(draft_payload).encode('utf-8'))

def update_status(row_index, status):
    url_headers = f'https://gateway.maton.ai/google-sheets/v4/spreadsheets/{SHEET_ID}/values/{urllib.parse.quote(f"{SHEET_NAME}!A1:Z1")}'
    headers = api_call(url_headers).get('values', [[]])[0]
    status_col_index = headers.index("Statut Contact")
    update_range = f'{SHEET_NAME}!{chr(ord("A") + status_col_index)}{int(row_index) + 2}'
    update_payload = {'values': [[status]]}
    url = f'https://gateway.maton.ai/google-sheets/v4/spreadsheets/{SHEET_ID}/values/{urllib.parse.quote(update_range)}?valueInputOption=RAW'
    return api_call(url, method='PUT', data=json.dumps(update_payload).encode('utf-8'))

if __name__ == "__main__":
    action = sys.argv[1]
    if action == "draft":
        to_email = sys.argv[2]
        subject = sys.argv[3]
        body = sys.argv[4]
        print(create_draft(to_email, subject, body))
    elif action == "status":
        row_index = sys.argv[2]
        status = sys.argv[3]
        print(update_status(row_index, status))
