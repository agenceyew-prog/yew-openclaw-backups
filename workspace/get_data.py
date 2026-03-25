import urllib.request
import urllib.parse
import os
import json

sheet_id = '1fIaChyoYhRt0RmsBIS7Z4SbSRukkXAwRZ5y01_uIVVQ'
range_name = urllib.parse.quote('Organisateurs Majeurs!A:R')
url = f"https://gateway.maton.ai/google-sheets/v4/spreadsheets/{sheet_id}/values/{range_name}"

req = urllib.request.Request(url)
req.add_header('Authorization', f'Bearer {os.environ.get("MATON_API_KEY", "")}')

try:
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    values = data.get('values', [])
    print(f"Rows: {len(values)}")
    if values:
        print(f"Headers: {values[0]}")
        if len(values) > 1:
            print(f"Row 1: {values[1]}")
            print(f"Row 2: {values[2]}")
            print(f"Row 3: {values[3]}")
except Exception as e:
    print(f"Error: {e}")
