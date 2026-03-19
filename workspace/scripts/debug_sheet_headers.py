# scripts/debug_sheet_headers.py
import urllib.request
import os
import json
import urllib.parse

MATON_API_KEY = os.environ.get("MATON_API_KEY")
if not MATON_API_KEY:
    print("Erreur: MATON_API_KEY non configurée.")
    exit(1)

SHEET_ID = '1fIaChyoYhRt0RmsBIS7Z4SbSRukkXAwRZ5y01_uIVVQ'
SHEET_NAME = 'Organisateurs Majeurs'
RANGE_HEADERS = f'{SHEET_NAME}!A1:Z1'

def api_call(url, method='GET', data=None):
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f'Bearer {MATON_API_KEY}')
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    try:
        with urllib.request.urlopen(req, data) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"Erreur HTTP: {e.code} - {e.reason}")
        print(f"Réponse d'erreur: {e.read().decode('utf-8')}")
        return {"error": e.read().decode('utf-8')}
    except Exception as e:
        print(f"Erreur: {e}")
        return {"error": str(e)}

def debug_get_headers():
    url_headers = f'https://gateway.maton.ai/google-sheets/v4/spreadsheets/{SHEET_ID}/values/{urllib.parse.quote(RANGE_HEADERS)}'
    print(f"URL de récupération des en-têtes: {url_headers}")
    headers_response = api_call(url_headers)
    print(f"Réponse brute des en-têtes: {headers_response}")
    if "error" in headers_response:
        print(f"Erreur lors de la récupération des en-têtes: {headers_response['error']}")
        return None
    headers = headers_response.get('values', [[]])[0]
    print(f"En-têtes extraits: {headers}")
    return headers

if __name__ == "__main__":
    debug_get_headers()
