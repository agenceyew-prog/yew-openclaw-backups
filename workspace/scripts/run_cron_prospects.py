import urllib.request, os, json, base64
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

MATON_API_KEY = os.environ.get("MATON_API_KEY")
SHEET_ID = '1fIaChyoYhRt0RmsBIS7Z4SbSRukkXAwRZ5y01_uIVVQ'
SHEET_NAME = 'Organisateurs Majeurs'
SENDER_EMAIL = 'contact@agenceyew.fr'
TELEGRAM_BOT_TOKEN = "8755473082:AAHD1ICvFTMMtV0BCSkiaxX7t4r22FhZRiA"
TELEGRAM_CHAT_ID = '-5216653116'

def api_call(url, method='GET', data=None):
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f'Bearer {MATON_API_KEY}')
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    try:
        with urllib.request.urlopen(req, data) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return {"error": str(e)}

def get_sheet_data():
    url_headers = f'https://gateway.maton.ai/google-sheets/v4/spreadsheets/{SHEET_ID}/values/{urllib.parse.quote(SHEET_NAME+"!A1:Z1")}'
    headers = api_call(url_headers).get('values', [[]])[0]
    url_data = f'https://gateway.maton.ai/google-sheets/v4/spreadsheets/{SHEET_ID}/values/{urllib.parse.quote(SHEET_NAME+"!A2:Z")}'
    data = api_call(url_data).get('values', [])
    return headers, data

def create_gmail_draft(to_email, subject, body):
    msg = MIMEText(body, 'html', 'utf-8')
    msg['to'] = to_email
    msg['from'] = formataddr((str(Header('Agence Yew', 'utf-8')), SENDER_EMAIL))
    msg['subject'] = Header(subject, 'utf-8').encode()
    raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
    url = 'https://gateway.maton.ai/google-mail/gmail/v1/users/me/drafts'
    return api_call(url, method='POST', data=json.dumps({'message': {'raw': raw_message}}).encode('utf-8'))

def update_sheet_status(row_index, status_col_index):
    update_range = f'{SHEET_NAME}!{chr(ord("A") + status_col_index)}{row_index + 2}'
    url = f'https://gateway.maton.ai/google-sheets/v4/spreadsheets/{SHEET_ID}/values/{urllib.parse.quote(update_range)}?valueInputOption=RAW'
    api_call(url, method='PUT', data=json.dumps({'values': [['Brouillon préparé']]}).encode('utf-8'))

def send_telegram(msg):
    url = f'https://gateway.maton.ai/telegram/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    api_call(url, method='POST', data=json.dumps({'chat_id': TELEGRAM_CHAT_ID, 'text': msg}).encode('utf-8'))

def main():
    headers, data = get_sheet_data()
    if not headers or not data: return
    
    try:
        status_col = headers.index("Statut Contact")
        email_col = headers.index("Email")
        name_col = headers.index("Nom")
        contact_col = headers.index("Contact clé")
        events_col = headers.index("Événements sportifs organisés")
    except ValueError: return

    count = 0
    for i, row in enumerate(data):
        status = row[status_col] if len(row) > status_col else ''
        if status in ['', 'Non contacté']:
            email = row[email_col] if len(row) > email_col else ''
            nom = row[name_col] if len(row) > name_col else ''
            contact = row[contact_col] if len(row) > contact_col else nom
            events = row[events_col] if len(row) > events_col else 'vos événements'
            
            if not email: continue
            
            subject = f"Proposition pour {events}"
            body = f"""Bonjour {contact},<br><br>Je me présente, Michael de l'Agence Yew. Je me permets de vous contacter à propos de {events}, car je pense pouvoir vous apporter une aide précieuse sur ce genre d’événement !<br><br>En regardant vos précédentes éditions, je sens une volonté de proposer la meilleure expérience à votre public. J’ai aussi remarqué qu'il y a un potentiel inexploité pour la diffusion en direct et la création de contenus dynamiques.<br><br>Je pense que nous pourrions aller plus loin ensemble afin d'offrir une expérience mémorable (ralentis sur écran géant, diffusion fluide, etc.). Chez Yew, nous accompagnons justement des organismes comme le vôtre dans la captation d’événements sportifs.<br><br>L'idée serait d'offrir :<br>- Plusieurs angles de vue<br>- Micros/caméras dédiés<br>- Habillage visuel intégrant votre charte<br>- Co-diffusion<br><br>C'est un excellent levier pour valoriser vos partenaires et votre audience. N'hésitez pas à jeter un œil à ce que nous produisons sur <a href="https://www.agenceyew.fr">www.agenceyew.fr</a>.<br><br>Nous pourrions convenir d’un appel afin d’en discuter et voir si cette approche résonne avec vos projets.<br><br>Cordialement,<br>Michael<br>Agence Yew"""
            
            create_gmail_draft(email, subject, body)
            update_sheet_status(i, status_col)
            count += 1
            if count >= 5: break

    send_telegram(f"Léa: J'ai préparé {count} brouillons hyper-personnalisés (Golden Template Ligue de Bretagne) dans Gmail et mis à jour le Google Sheet.")
    print(f"Processed {count} drafts")

main()
