import json

with open("scripts/prospect_veille.py", "r") as f:
    content = f.read()

hubspot_func = """def add_prospect_to_hubspot(prospect_data):
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
        
    if prospect_data.get("Secteur d'activité") and prospect_data.get("Secteur d'activité") != "À déterminer":
        properties["industry"] = prospect_data["Secteur d'activité"]

    payload = {"properties": properties}
    print(f"DEBUG: add_prospect_to_hubspot - Sending payload: {payload}")
    
    response = api_call(url, method='POST', data=json.dumps(payload).encode('utf-8'))
    
    if "error" in response:
        print(f"DEBUG: add_prospect_to_hubspot - Erreur HubSpot: {response['error']}")
        return False
        
    print(f"DEBUG: add_prospect_to_hubspot - Succès HubSpot.")
    return True

def process_opportunities"""

content = content.replace("def process_opportunities", hubspot_func)

old_add_call = """            if add_prospect_to_sheet(prospect_data):
                opportunities_added_to_sheet += 1"""

new_add_call = """            sheet_success = add_prospect_to_sheet(prospect_data)
            hubspot_success = add_prospect_to_hubspot(prospect_data)
            if sheet_success:
                opportunities_added_to_sheet += 1"""

content = content.replace(old_add_call, new_add_call)

with open("scripts/prospect_veille.py", "w") as f:
    f.write(content)
