# scripts/update_sector_activity.py
import urllib.request
import os
import json
import urllib.parse

# Assurez-vous que MATON_API_KEY est configurée
MATON_API_KEY = os.environ.get("MATON_API_KEY")
if not MATON_API_KEY:
    print("Erreur: MATON_API_KEY non configurée.")
    exit(1)

# Constantes pour Google Sheet
SHEET_ID = '1fIaChyoYhRt0RmsBIS7Z4SbSRukkXAwRZ5y01_uIVVQ'
SHEET_NAME = 'Organisateurs Majeurs'
RANGE_HEADERS = f'{SHEET_NAME}!A1:Z1'
RANGE_DATA = f'{SHEET_NAME}!A2:Z'

TELEGRAM_BOT_TOKEN = "8755473082:AAHD1ICvFTMMV0BCSkiaxX7t4r22FhZRiA"
TELEGRAM_CHAT_ID = '-5216653116' # ID de chat Telegram pour les notifications (groupe Yew)

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

def send_telegram_notification(message_text):
    url = f'https://gateway.maton.ai/telegram/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message_text
    }
    return api_call(url, method='POST', data=json.dumps(payload).encode('utf-8'))

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

def main():
    headers, data = get_sheet_data()
    if not headers or not data:
        print("Impossible de récupérer les données de la feuille Google Sheets.")
        send_telegram_notification("Léa: Échec de la mise à jour des secteurs d'activité : impossible de récupérer les données de la feuille Google Sheets.")
        return

    try:
        sector_col_index = headers.index("Secteur d'activité ")
    except ValueError:
        print("Erreur: La colonne 'Secteur d'activité' est introuvable. Veuillez vous assurer qu'elle existe.")
        send_telegram_notification("Léa: Échec de la mise à jour des secteurs d'activité : la colonne 'Secteur d'activité' est introuvable.")
        return

    updates_count = 0
    for i, row in enumerate(data):
        # +2 car les données commencent à la ligne 2 et sont 0-indexées
        row_number_in_sheet = i + 2 
        
        current_sector_value = row[sector_col_index] if len(row) > sector_col_index else ""

        if not current_sector_value.strip(): # Si la valeur est vide ou ne contient que des espaces
            # Construire la plage pour la cellule spécifique à mettre à jour
            # chr(65 + sector_col_index) convertit l'index de colonne (0-basé) en lettre (ex: 0->A, 1->B)
            cell_range = f'{SHEET_NAME}!{chr(65 + sector_col_index)}{row_number_in_sheet}'
            
            update_payload = {
                'values': [["Sport"]]
            }
            url = f'https://gateway.maton.ai/google-sheets/v4/spreadsheets/{SHEET_ID}/values/{urllib.parse.quote(cell_range)}?valueInputOption=USER_ENTERED'
            response = api_call(url, method='PUT', data=json.dumps(update_payload).encode('utf-8'))
            
            if "error" not in response:
                print(f"Ligne {row_number_in_sheet}: Secteur d'activité mis à jour à 'Sport'.")
                updates_count += 1
            else:
                print(f"Erreur lors de la mise à jour de la ligne {row_number_in_sheet}: {response['error']}")

    if updates_count > 0:
        notification_message = f"Léa: J'ai mis à jour le secteur d'activité de {updates_count} contacts existants à 'Sport' dans la feuille 'Organisateurs Majeurs'."
        send_telegram_notification(notification_message)
        print(notification_message)
    else:
        notification_message = "Léa: Tous les contacts existants avaient déjà un secteur d'activité ou aucun contact n'a été mis à jour."
        send_telegram_notification(notification_message)
        print(notification_message)

if __name__ == "__main__":
    main()
