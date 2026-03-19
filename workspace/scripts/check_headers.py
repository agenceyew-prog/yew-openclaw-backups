import urllib.request, os, json, urllib.parse
MATON_API_KEY = os.environ.get("MATON_API_KEY")
SHEET_ID = "1fIaChyoYhRt0RmsBIS7Z4SbSRukkXAwRZ5y01_uIVVQ"
url = f"https://gateway.maton.ai/google-sheets/v4/spreadsheets/{SHEET_ID}/values/{urllib.parse.quote('Organisateurs Majeurs!A1:Z1')}"
req = urllib.request.Request(url, method="GET")
req.add_header("Authorization", f"Bearer {MATON_API_KEY}")
res = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
print(res.get("values", [[]])[0])
