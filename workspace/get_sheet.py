import urllib.request
import os
import json

sheet_id = '1fIaChyoYhRt0RmsBIS7Z4SbSRukkXAwRZ5y01_uIVVQ'
url = f"https://gateway.maton.ai/google-sheets/v4/spreadsheets/{sheet_id}"
req = urllib.request.Request(url)
req.add_header('Authorization', f'Bearer {os.environ.get("MATON_API_KEY", "")}')

try:
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    sheets = data.get('sheets', [])
    for s in sheets:
        title = s.get('properties', {}).get('title')
        print(f"Sheet: {title}")
except Exception as e:
    print(f"Error: {e}")
