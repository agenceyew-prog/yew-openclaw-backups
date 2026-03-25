import urllib.request
import urllib.parse
import os
import json
import traceback

def get_sheet_data():
    sheet_id = '1fIaChyoYhRt0RmsBIS7Z4SbSRukkXAwRZ5y01_uIVVQ'
    range_name = 'Sheet1!A:Z' # Adjust if needed
    
    url = f"https://gateway.maton.ai/google-sheets/v4/spreadsheets/{sheet_id}/values/{range_name}"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {os.environ.get("MATON_API_KEY", "")}')
    try:
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read())
        return data.get('values', [])
    except Exception as e:
        print(f"Error fetching sheet: {e}")
        return []

data = get_sheet_data()
print(f"Rows: {len(data)}")
if data:
    print(f"Header: {data[0]}")
    if len(data) > 1:
        print(f"First row: {data[1]}")
