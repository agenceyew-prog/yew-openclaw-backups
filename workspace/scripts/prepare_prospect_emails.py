
import urllib.request, os, json, base64
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

MATON_API_KEY = os.environ.get("MATON_API_KEY")
if not MATON_API_KEY:
    print("Erreur: MATON_API_KEY non configurée.")
    exit(1)

SHEET_ID = '1fIaChyoYhRt0RmsBIS7Z4SbSRukkXAwRZ5y01_uIVVQ'
SHEET_NAME = 'Organisateurs Majeurs'
RANGE_HEADERS = f'{SHEET_NAME}!A1:Z1'
RANGE_DATA = f'{SHEET_NAME}!A2:Z'
SENDER_EMAIL = 'contact@agenceyew.fr'
TELEGRAM_BOT_TOKEN = "8755473082:AAHD1ICvFTMMtV0BCSkiaxX7t4r22FhZRiA"
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

def get_sheet_data():
    url_headers = f'https://gateway.maton.ai/google-sheets/v4/spreadsheets/{SHEET_ID}/values/{urllib.parse.quote(RANGE_HEADERS)}'
    headers_response = api_call(url_headers)
    if "error" in headers_response:
        return None, None
    headers = headers_response.get('values', [[]])[0]

    url_data = f'https://gateway.maton.ai/google-sheets/v4/spreadsheets/{SHEET_ID}/values/{urllib.parse.quote(RANGE_DATA)}'
    data_response = api_call(url_data)
    if "error" in data_response:
        return None, None
    data = data_response.get('values', [])
    return headers, data

def create_gmail_draft(to_email, subject, body):
    # Encodage du sujet selon RFC 2047 pour les caractères non-ASCII
    encoded_subject = Header(subject, 'utf-8').encode()

    msg = MIMEText(body, 'html', 'utf-8')
    msg['to'] = to_email
    msg['from'] = formataddr((str(Header('Agence Yew', 'utf-8')), SENDER_EMAIL))
    msg['subject'] = encoded_subject

    raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')

    draft_payload = {
        'message': {
            'raw': raw_message
        }
    }
    url = 'https://gateway.maton.ai/google-mail/gmail/v1/users/me/drafts'
    return api_call(url, method='POST', data=json.dumps(draft_payload).encode('utf-8'))

def update_sheet_status(row_index, status_value):
    # Trouver l'index de la colonne "Statut Contact"
    headers, _ = get_sheet_data()
    if not headers or "Statut Contact" not in headers:
        print("Erreur: Colonne 'Statut Contact' introuvable.")
        return False
    status_col_index = headers.index("Statut Contact")

    update_range = f'{SHEET_NAME}!{chr(ord("A") + status_col_index)}{row_index + 2}' # +2 car 1-indexed et headers

    update_payload = {
        'values': [[status_value]]
    }
    url = f'https://gateway.maton.ai/google-sheets/v4/spreadsheets/{SHEET_ID}/values/{urllib.parse.quote(update_range)}?valueInputOption=RAW'
    response = api_call(url, method='PUT', data=json.dumps(update_payload).encode('utf-8'))
    return "error" not in response

def send_telegram_notification(message_text):
    url = f'https://gateway.maton.ai/telegram/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message_text
    }
    return api_call(url, method='POST', data=json.dumps(payload).encode('utf-8'))

def main():
    headers, data = get_sheet_data()
    if not headers or not data:
        print("Impossible de récupérer les données de la feuille Google Sheets.")
        return

    # Trouver l'index de la colonne "Statut Contact" et "Email"
    try:
        status_col_index = headers.index("Statut Contact")
        email_col_index = headers.index("Email")
        name_col_index = headers.index("Nom")
        pitch_col_index = headers.index("Angle d'attaque (Pitch Yew)")
        contact_key_col_index = headers.index("Contact clé")
        events_col_index = headers.index("Événements sportifs organisés")

    except ValueError as e:
        print(f"Erreur: Colonne essentielle introuvable - {e}. Assurez-vous que 'Statut Contact', 'Email', 'Nom', 'Angle d'attaque (Pitch Yew)', 'Contact clé' et 'Événements sportifs organisés' existent.")
        return

    prospects_to_contact = []
    for i, row in enumerate(data):
        # Assurez-vous que la ligne a suffisamment de colonnes pour éviter les IndexError
        current_status = row[status_col_index] if len(row) > status_col_index else ''
        if current_status == '' or current_status == 'Non contacté':
            if len(prospects_to_contact) < 5:
                # Créer un dictionnaire pour le prospect avec des valeurs par défaut si des colonnes sont manquantes
                prospect_data = {
                    "Nom": row[name_col_index] if len(row) > name_col_index else "",
                    "Email": row[email_col_index] if len(row) > email_col_index else "",
                    "Angle d'attaque (Pitch Yew)": row[pitch_col_index] if len(row) > pitch_col_index else "",
                    "Contact clé": row[contact_key_col_index] if len(row) > contact_key_col_index else "",
                    "Événements sportifs organisés": row[events_col_index] if len(row) > events_col_index else ""
                }
                prospects_to_contact.append({"row_index": i, "data": prospect_data})
            else:
                break
    
    if not prospects_to_contact:
        print("Aucun nouveau prospect à contacter trouvé.")
        send_telegram_notification("Léa: Je n'ai trouvé aucun nouveau prospect à contacter dans la feuille 'Organisateurs Majeurs' ce matin.")
        return

    draft_count = 0
    for prospect in prospects_to_contact:
        to_email = prospect['data']['Email']
        prospect_name = prospect['data']['Nom']
        contact_key = prospect['data']['Contact clé']
        pitch = prospect['data']["Angle d'attaque (Pitch Yew)"]
        events = prospect['data']['Événements sportifs organisés']

        if not to_email:
            print(f"Prospect '{prospect_name}' n'a pas d'email. Ignoré.")
            continue

        subject = f"Proposition de valorisation de vos {events} avec Agence Yew"
        
        # Le contenu du SOUL.md doit être intégré ici pour la personnalisation.
        # Pour l'exemple, je vais utiliser un template générique.
        body = f"""
        Bonjour {contact_key or prospect_name},<br><br>
        En tant que passionnés de sport, nous suivons de près l'énergie que vous insufflez dans l'organisation de vos {events}. Nous comprenons les défis liés à la visibilité et à la valorisation de ces moments clés.<br><br>
        Chez Agence Yew, nous aidons des organisations comme la vôtre à transformer leurs événements en expériences mémorables et captivantes pour le public.<br><br>
        {pitch}<br><br>
        Vous pouvez découvrir nos réalisations ici : <a href="https://www.agenceyew.fr">www.agenceyew.fr</a><br><br>
        Seriez-vous disponible pour un court échange téléphonique sans engagement la semaine prochaine afin d'explorer comment nous pourrions collaborer ?<br><br>
        Cordialement,<br>
        L'équipe Yew
        """

        draft_response = create_gmail_draft(to_email, subject, body)
        if "error" not in draft_response:
            print(f"Brouillon créé pour {prospect_name} ({to_email}).")
            update_sheet_status(prospect['row_index'], 'Brouillon préparé')
            draft_count += 1
        else:
            print(f"Échec de la création du brouillon pour {prospect_name}: {draft_response['error']}")

    notification_message = f"Léa: J'ai préparé {draft_count} brouillon(s) d'emails pour les prospects ce matin. Veuillez vérifier votre boîte Gmail (expéditeur {SENDER_EMAIL}). Le statut dans la feuille 'Organisateurs Majeurs' a été mis à jour."
    send_telegram_notification(notification_message)

if __name__ == "__main__":
    main()
