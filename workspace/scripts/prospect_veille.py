# scripts/prospect_veille.py
import os
import json
import urllib.parse
import urllib.request
import sys
import re
from datetime import datetime

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
        # print(f"Erreur HTTP: {e.code} - {e.reason}")
        # print(f"Réponse d'erreur: {e.read().decode('utf-8')}")
        return {"error": e.read().decode('utf-8')}
    except Exception as e:
        # print(f"Erreur: {e}")
        return {"error": str(e)}

def send_telegram_notification(message_text):
    print(f"TELEGRAM MESSAGE (to Yew Group {TELEGRAM_CHAT_ID}): {message_text}")
    return {"status": "mocked"}

def get_sheet_data():
    url_headers = f'https://gateway.maton.ai/google-sheets/v4/spreadsheets/{SHEET_ID}/values/{urllib.parse.quote(RANGE_HEADERS)}'
    headers_response = api_call(url_headers)
    if "error" in headers_response:
        # print(f"Erreur lors de la récupération des en-têtes: {headers_response['error']}")
        return None, None
    headers = headers_response.get('values', [[]])[0]

    url_data = f'https://gateway.maton.ai/google-sheets/v4/spreadsheets/{SHEET_ID}/values/{urllib.parse.quote(RANGE_DATA)}'
    data_response = api_call(url_data)
    if "error" in data_response:
        # print(f"Erreur lors de la récupération des données de la feuille: {data_response['error']}")
        return None, None
    data = data_response.get('values', [])
    return headers, data

def add_prospect_to_sheet(prospect_data):
    headers, existing_data = get_sheet_data()
    if not headers:
        print("DEBUG: add_prospect_to_sheet - Failed to get headers")
        return False

    required_cols = [
        "Nom", "Type d'organisation", "Événements sportifs organisés", "Récurrences",
        "Réseaux sociaux", "Live déjà proposé", "Contact clé", "Email", "Téléphone",
        "Site web", "Description", "Angle d'attaque (Pitch Yew)", "Intérêt live",
        "Potentiel budget", "Statut Contact", "Secteur d'activité ", "Source", "Complément"
    ]
    for col in required_cols:
        if col not in headers:
            print(f"DEBUG: add_prospect_to_sheet - Erreur: La colonne '{col}' est manquante dans la feuille Google Sheets.")
            return False

    row_to_add = [""] * len(headers)
    for col_name, value in prospect_data.items():
        if col_name in headers:
            col_index = headers.index(col_name)
            row_to_add[col_index] = value
            
    link_col_index = headers.index("Site web") if "Site web" in headers else -1
    name_col_index = headers.index("Nom") if "Nom" in headers else -1

    for row in existing_data:
        if link_col_index != -1 and len(row) > link_col_index and row[link_col_index] == prospect_data.get("Site web", ""):
            print(f"DEBUG: add_prospect_to_sheet - Prospect avec lien {prospect_data.get('Site web')} existe déjà. Ignoré.")
            return False
        if name_col_index != -1 and len(row) > name_col_index and row[name_col_index] == prospect_data.get("Nom", "") and prospect_data.get("Nom", "") != "":
            print(f"DEBUG: add_prospect_to_sheet - Prospect avec nom {prospect_data.get('Nom')} existe déjà. Ignoré.")
            return False

    update_range = f'{SHEET_NAME}!A:Z'
    update_payload = {
        'values': [row_to_add]
    }
    print(f"DEBUG: add_prospect_to_sheet - Sending payload to Maton: {update_payload}")
    url = f'https://gateway.maton.ai/google-sheets/v4/spreadsheets/{SHEET_ID}/values/{urllib.parse.quote(update_range)}:append?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS'
    response = api_call(url, method='POST', data=json.dumps(update_payload).encode('utf-8'))
    print(f"DEBUG: add_prospect_to_sheet - Maton response: {response}")
    return "error" not in response

def determine_sector_from_query(query):
    query_lower = query.lower()
    if any(keyword in query_lower for keyword in ["sportif", "sport", "compétition", "match", "tournoi", "stade", "ligue", "fédération"]):
        return "Sport"
    if any(keyword in query_lower for keyword in ["culturel", "festival", "musique", "art", "spectacle", "théâtre", "danse", "exposition"]):
        return "Culture"
    if any(keyword in query_lower for keyword in ["entreprise", "conférence", "séminaire", "interne", "externe", "corporate", "congrès", "salon professionnel"]):
        return "Entreprise"
    if any(keyword in query_lower for keyword in ["immobilier", "luxe", "prestige", "villa", "château", "propriété"]):
        return "Immo"
    return "" # Laisser vide si non déterminé pour ne pas casser le menu déroulant

def generate_search_targets():
    regions = ["Nord Pas-de-Calais", "Île-de-France", "Bretagne", "Normandie", "Nouvelle-Aquitaine", "Occitanie", "PACA"]
    services_keywords = ["live", "captation multicam", "diffusion écran", "drone", "vidéo d'entreprise", "after movie", "caméra 360", "streaming e-sport", "diffusion séminaire", "couverture régionale"]
    event_types = ["événement sportif", "compétition sportive", "conférence entreprise", "festival culturel", "entité publique", "ligue régionale", "tournoi e-sport", "fédération sportive de taille moyenne", "événement corporate", "compétition sport amateur", "team building sportif", "e-sport émergent", "événement caritatif sportif", "championnat universitaire", "sport extrême", "compétition handisport", "convention d'entreprise", "salon professionnel B2B"]

    queries = []
    for region in regions:
        for event_type in event_types:
            base_queries = [
                f"{event_type} {region} production vidéo",
                f"{event_type} {region} prestation audiovisuelle",
                f"organisateur {event_type} {region}",
                f"appel d'offres {region} audiovisuel",
            ]
            queries.extend(base_queries)
            
            for service_kw in services_keywords:
                queries.append(f"{event_type} {region} {service_kw}")
                queries.append(f"organisation {event_type} {region} {service_kw}")

    queries = list(set(queries)) # Éliminer les doublons de requêtes
    return {"web_search_queries": queries}

def filter_urls_for_agent_browser(web_search_results_list):
    # Nouvelle logique : Liste noire étendue.
    unwanted_domains = [
        "youtube.com", "dailymotion.com", "vimeo.com", "tiktok.com",
        "facebook.com", "twitter.com", "instagram.com", "linkedin.com", "pinterest.com",
        "wikipedia.org", "wiktionary.org", "wikidata.org",
        "lequipe.fr", "rmcsport.bfmtv.com", "eurosport.fr", "francetvinfo.fr", "lefigaro.fr", "lemonde.fr", "leparisien.fr", "liberation.fr", "ouest-france.fr", "lavoixdunord.fr", "paris-normandie.fr", "letelegramme.fr",
        "allocine.fr", "senscritique.com", "telerama.fr",
        "eventbrite.fr", "billetweb.fr", "weezevent.com", "ticketmaster.fr", "fnacspectacles.com", "seetickets.com", "infoconcert.com", "digitick.com",
        "google.com", "bing.com", "yahoo.com", "qwant.com", "duckduckgo.com",
        "pagesjaunes.fr", "tripadvisor.fr", "yelp.fr", "petitfute.com", "routard.com",
        "amazon.fr", "cdiscount.com", "fnac.com", "darty.com", "leboncoin.fr",
        "legifrance.gouv.fr", "service-public.fr", "impots.gouv.fr", "education.gouv.fr",
        "pole-emploi.fr", "francetravail.fr", "apec.fr",
        "doctolib.fr", "ameli.fr",
        "linternaute.com", "sortiraparis.com", "offi.fr", "unidivers.fr", "jds.fr"
    ]

    filtered_urls = []
    unique_filtered_urls = set()

    # web_search_results_list peut être une liste de dicts (résultats plats) 
    # OU une liste de dicts contenant {"query": ..., "results": [...] }
    
    flat_results = []
    for item in web_search_results_list:
        if "results" in item and isinstance(item["results"], list):
            # Structure imbriquée
            for res in item["results"]:
                # On ajoute la query source pour ne pas la perdre
                res["query"] = item.get("query", "")
                flat_results.append(res)
        else:
            # Structure plate
            flat_results.append(item)

    for result in flat_results:
        link = result.get("link")
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        source_query = result.get("query", "")
        
        if not link: continue
        
        try:
            domain = urllib.parse.urlparse(link).netloc.lower()
            if domain.startswith("www."):
                domain = domain[4:] # Normaliser
        except Exception:
            continue
            
        is_unwanted = False
        for un_domain in unwanted_domains:
            if un_domain in domain:
                is_unwanted = True
                break
                
        if not is_unwanted:
            if link not in unique_filtered_urls:
                filtered_urls.append({"url": link, "title": title, "snippet": snippet, "query": source_query})
                unique_filtered_urls.add(link)
                
    return filtered_urls

def add_prospect_to_hubspot(prospect_data):
    url = 'https://gateway.maton.ai/hubspot/crm/v3/objects/contacts'
    properties = {}
    
    if prospect_data.get("Email"):
        properties["email"] = prospect_data["Email"]
        
    properties["lastname"] = prospect_data.get("Nom", "Prospect Inconnu")
    properties["company"] = prospect_data.get("Nom", "")
    
    if prospect_data.get("Téléphone"):
        properties["phone"] = prospect_data["Téléphone"]
        
    if prospect_data.get("Site web"):
        properties["website"] = prospect_data["Site web"]
        
    if prospect_data.get("Secteur d'activité ") and prospect_data.get("Secteur d'activité ") != "À déterminer":
        properties["industry"] = prospect_data["Secteur d'activité "]

    payload = {"properties": properties}
    print(f"DEBUG: add_prospect_to_hubspot - Sending payload: {payload}")
    
    response = api_call(url, method='POST', data=json.dumps(payload).encode('utf-8'))
    
    if "error" in response:
        print(f"DEBUG: add_prospect_to_hubspot - Erreur HubSpot: {response['error']}")
        return False
        
    print(f"DEBUG: add_prospect_to_hubspot - Succès HubSpot.")
    return True

def process_opportunities(raw_opportunities_json):
    print(f"DEBUG: process_opportunities received JSON: {raw_opportunities_json}")
    try:
        raw_opportunities = json.loads(raw_opportunities_json)
    except json.JSONDecodeError:
        print("Erreur: Le JSON des opportunités brutes est invalide.")
        send_telegram_notification("Léa: Erreur lors du traitement des opportunités : JSON invalide.")
        return

    opportunities_added_to_sheet = 0
    
    for opportunity in raw_opportunities:
        link = opportunity.get("link")
        title = opportunity.get("title")
        source_query = opportunity.get("query", "") 
        extracted_content = opportunity.get("extracted_content", "") # Contenu brut renvoyé par l'Explorateur

        # Extraction via Regex des champs standards s'ils existent dans le texte brut
        email_match = re.search(r'[\w\.-]+@[\w\.-]+', extracted_content)
        email = email_match.group(0) if email_match else ""
        
        phone_match = re.search(r'(?:(?:\+|00)33[\s.-]{0,3}(?:\(0\)[\s.-]{0,3})?|0)[1-9](?:(?:[\s.-]?\d{2}){4}|\d{2}(?:[\s.-]?\d{3}){2})', extracted_content)
        phone = phone_match.group(0) if phone_match else ""

        print(f"DEBUG: Processing opportunity: {title} - {link}")
        if link and title: 
            sector = determine_sector_from_query(source_query + " " + title + " " + extracted_content) # Déduit le secteur (ex: "Sport", "Culture")
            
            prospect_data = {
                "Nom": title,
                "Type d'organisation": "",
                "Événements sportifs organisés": "",
                "Récurrences": "",
                "Réseaux sociaux": "",
                "Live déjà proposé": "",
                "Contact clé": "",
                "Email": email, 
                "Téléphone": phone,
                "Site web": link,
                "Description": "",
                "Angle d'attaque (Pitch Yew)": "",
                "Intérêt live": "",
                "Potentiel budget": "",
                "Statut Contact": "Non contacté",
                "Secteur d'activité ": sector, # Menu déroulant mis à jour
                "Source": source_query,
                "Complément": extracted_content # On y déverse tout le texte brut pour analyse humaine !
            }
            print(f"DEBUG: Attempting to add prospect data: {prospect_data}")
            if add_prospect_to_sheet(prospect_data):
                print(f"DEBUG: Prospect added successfully.")
                opportunities_added_to_sheet += 1
            else:
                print(f"DEBUG: Failed to add prospect.")

    if opportunities_added_to_sheet > 0:
        notification_message = f"Léa: J'ai identifié et ajouté {opportunities_added_to_sheet} nouvelles opportunités à la feuille 'Organisateurs Majeurs'. Les secteurs d'activité ont été pré-catégorisés. Veuillez les consulter et les qualifier si besoin."
        send_telegram_notification(notification_message)
        print(notification_message)
    else:
        notification_message = "Léa: Aucune nouvelle opportunité significative trouvée ou ajoutée à la feuille 'Organisateurs Majeurs' lors de la dernière veille."
        send_telegram_notification(notification_message)
        print(notification_message)

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else ""

    if action == "generate_search_targets":
        targets = generate_search_targets()
        print(json.dumps(targets, ensure_ascii=False, indent=2))
    elif action == "filter_urls_for_agent_browser":
        web_search_results_json = sys.stdin.read()
        if not web_search_results_json:
            print(json.dumps([]))
        else:
            try:
                results = json.loads(web_search_results_json)
            except json.JSONDecodeError as e:
                print(f"JSONDecodeError: {e}")
                sys.exit(1)
            filtered = filter_urls_for_agent_browser(results)
            print(json.dumps(filtered, ensure_ascii=False, indent=2))
    elif action == "process_opportunities":
        raw_opportunities_json = sys.stdin.read()
        process_opportunities(raw_opportunities_json)
    else:
        print("Usage: python3 prospect_veille.py [generate_search_targets|filter_urls_for_agent_browser|process_opportunities]")
