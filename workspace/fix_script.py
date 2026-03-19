with open("scripts/prospect_veille.py", "r") as f:
    content = f.read()

import re
# Regex to replace the whole function definition
content = re.sub(
    r'def filter_urls_for_agent_browser.*?return filtered_urls',
    r'''def filter_urls_for_agent_browser(web_search_results_list):
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

    for result in web_search_results_list:
        link = result.get("link")
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        
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
                filtered_urls.append({"url": link, "title": title, "snippet": snippet})
                unique_filtered_urls.add(link)
                
    return filtered_urls''',
    content,
    flags=re.DOTALL
)

with open("scripts/prospect_veille.py", "w") as f:
    f.write(content)
