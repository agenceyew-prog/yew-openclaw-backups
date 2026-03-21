import urllib.request, os, json, urllib.parse

api_key = os.environ.get("MATON_API_KEY")
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

sheet_meta = api_call(url_sheet)
sheet_name = sheet_meta["sheets"][0]["properties"]["title"]

url_values = f"https://gateway.maton.ai/google-sheets/v4/spreadsheets/{sheet_id}/values/{urllib.parse.quote(sheet_name)}!A:R"
values = api_call(url_values).get("values", [])

draft_emails = [
    "contact@triathlon-hdf.fr",
    "contact@hexagonemma.fr",
    "iledefrance@ffgym.fr",
    "ligue.bretagne@fft.fr",
    "paris@sport-u.com"
]

sent_emails = [
    "communication@bretagne-basketball.org",
    "secretariatgeneral@basketbretagne.com",
    "michael.philibert@live.com",
    "mehomies@meho-mieees.org",
    "contact@mikhaprod.com"
]

header = values[0]
email_col = header.index("Email")
status_col = header.index("Statut Contact")

updates = []
for i, row in enumerate(values):
    if i == 0: continue
    if len(row) <= email_col: continue
    
    email = row[email_col].strip()
    if not email: continue
    
    current_status = row[status_col] if len(row) > status_col else ""
    new_status = None
    
    # Check if sent
    if any(e.lower() in email.lower() for e in sent_emails) and "michael.philibert" not in email.lower() and "mehomies" not in email.lower() and "mikhaprod" not in email.lower():
        if current_status != "Email envoyé":
            new_status = "Email envoyé"
            
    # Check if draft
    elif any(e.lower() in email.lower() for e in draft_emails):
        if current_status != "Brouillon préparé":
            new_status = "Brouillon préparé"
            
    if new_status:
        # Col O is index 14 (A=0, B=1, ... O=14)
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
    print(f"Updated {len(updates)} rows.")
else:
    print("No updates needed.")
