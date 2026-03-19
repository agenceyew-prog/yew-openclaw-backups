import urllib.request
import os
import json

MATON_API_KEY = os.environ.get("MATON_API_KEY")
if not MATON_API_KEY:
    print("Erreur: MATON_API_KEY non configurée.")
    exit(1)

SHEET_ID = '1fIaChyoYhRt0RmsBIS7Z4SbSRukkXAwRZ5y01_uIVVQ'
SHEET_NAME = 'Organisateurs Majeurs'
RANGE_HEADERS = f'{SHEET_NAME}!A1:Z1'
RANGE_DATA = f'{SHEET_NAME}!A2:Z'

TELEGRAM_CHAT_ID = '-5216653116'

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

def get_sheet_data():
    url_headers = f'https://gateway.maton.ai/google-sheets/v4/spreadsheets/{SHEET_ID}/values/{urllib.parse.quote(RANGE_HEADERS)}'
    headers_response = api_call(url_headers)
    if "error" in headers_response:
        print(f"Erreur lors de la récupération des en-têtes: {headers_response['error']}")
        return None, None
    headers = headers_response.get('values', [[]])[0]

    url_data = f'https://gateway.maton.ai/google-sheets/v4/spreadsheets/{SHEET_ID}/values/{urllib.parse.quote(RANGE_DATA)}'
    data_response = api_call(url_data)
    if "error" in data_response:
        print(f"Erreur lors de la récupération des données de la feuille: {data_response['error']}")
        return None, None
    data = data_response.get('values', [])
    return headers, data

def run_heartbeat_checks():
    # 1. Vérification des brouillons d'emails
    drafts_url = 'https://gateway.maton.ai/google-mail/gmail/v1/users/me/drafts'
    drafts_response = api_call(drafts_url)

    draft_count = 0
    if "drafts" in drafts_response:
        draft_count = len(drafts_response["drafts"])

    # 2. Vérification des emails envoyés
    sent_url = 'https://gateway.maton.ai/google-mail/gmail/v1/users/me/messages?q=in:sent'
    sent_response = api_call(sent_url)

    sent_count = 0
    if "messages" in sent_response:
        sent_count = len(sent_response["messages"])

    # 3. Synchronisation CRM - Vérification du statut des prospects
    headers, data = get_sheet_data()
    crm_status_message = "Impossible de vérifier le CRM."
    if headers and data:
        try:
            status_col_index = headers.index("Statut Contact")
            non_contacted_count = 0
            draft_prepared_count = 0
            for row in data:
                current_status = row[status_col_index] if len(row) > status_col_index else ''
                if current_status == 'Non contacté' or current_status == '':
                    non_contacted_count += 1
                elif current_status == 'Brouillon préparé':
                    draft_prepared_count += 1
            crm_status_message = f"{non_contacted_count} prospects 'Non contacté', {draft_prepared_count} prospects 'Brouillon préparé'."
        except ValueError:
            crm_status_message = "Colonne 'Statut Contact' introuvable dans la feuille."
    
    # Prépare le message pour la réponse HEARTBEAT_OK si rien ne nécessite une action immédiate.
    # Sinon, une alerte est renvoyée.
    heartbeat_reply = "HEARTBEAT_OK"
    attention_needed = []

    if draft_count > 0:
        attention_needed.append(f"Il y a {draft_count} brouillon(s) d'emails en attente.")
    if sent_count == 0:
        attention_needed.append("Aucun email envoyé récemment n'a été trouvé.")

    if attention_needed:
        return f"ATTENTION: {' '.join(attention_needed)} {crm_status_message}"
    else:
        return f"HEARTBEAT_OK. {crm_status_message}"

if __name__ == "__main__":
    print(run_heartbeat_checks())
