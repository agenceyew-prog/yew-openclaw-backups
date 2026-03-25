import urllib.request
import urllib.parse
import os
import json
import time

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

sheet_id = '1fIaChyoYhRt0RmsBIS7Z4SbSRukkXAwRZ5y01_uIVVQ'
range_name = 'Organisateurs Majeurs!A:R'
encoded_range = urllib.parse.quote(range_name)
url = f"https://gateway.maton.ai/google-sheets/v4/spreadsheets/{sheet_id}/values/{encoded_range}"

sheet_data = maton_get(url)
values = sheet_data.get('values', [])

for row_idx, row in enumerate(values[1:], start=2):
    email = row[7].lower().strip() if len(row) > 7 else ""
    if not email: continue
    
    status = row[14] if len(row) > 14 else ""
    print(f"Row {row_idx}: email={email}, status={status}")
    if row_idx > 5: break
