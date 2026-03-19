import urllib.request, os, json, sys

MATON_API_KEY = os.environ.get("MATON_API_KEY")
SHEET_ID = '1fIaChyoYhRt0RmsBIS7Z4SbSRukkXAwRZ5y01_uIVVQ'
SHEET_NAME = 'Organisateurs Majeurs'

def api_call(url):
    req = urllib.request.Request(url, method='GET')
    req.add_header('Authorization', f'Bearer {MATON_API_KEY}')
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

headers_url = f'https://gateway.maton.ai/google-sheets/v4/spreadsheets/{SHEET_ID}/values/{urllib.parse.quote(f"{SHEET_NAME}!A1:Z1")}'
data_url = f'https://gateway.maton.ai/google-sheets/v4/spreadsheets/{SHEET_ID}/values/{urllib.parse.quote(f"{SHEET_NAME}!A2:Z")}'

headers = api_call(headers_url).get('values', [[]])[0]
data = api_call(data_url).get('values', [])

try:
    status_col = headers.index("Statut Contact")
    email_col = headers.index("Email")
    name_col = headers.index("Nom")
    pitch_col = headers.index("Angle d'attaque (Pitch Yew)")
    contact_col = headers.index("Contact clé")
    events_col = headers.index("Événements sportifs organisés")
    site_col = headers.index("Site Web / Réseaux sociaux") # might not exist, let's find it safely
except ValueError:
    pass

site_col = headers.index("Site Web / Réseaux sociaux") if "Site Web / Réseaux sociaux" in headers else -1

found = []
for i, row in enumerate(data):
    status = row[status_col] if len(row) > status_col else ''
    if status == 'Brouillon préparé':
        found.append({
            "row": i + 2,
            "nom": row[name_col] if len(row) > name_col else "",
            "email": row[email_col] if len(row) > email_col else "",
            "pitch": row[pitch_col] if len(row) > pitch_col else "",
            "contact": row[contact_col] if len(row) > contact_col else "",
            "events": row[events_col] if len(row) > events_col else "",
            "site": row[site_col] if site_col != -1 and len(row) > site_col else ""
        })
        if len(found) >= 5:
            break

print(json.dumps(found, indent=2))
