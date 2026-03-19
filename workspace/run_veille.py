import json
import random
import subprocess
import urllib.request
import urllib.parse
import os

# 1. Generate Targets
print("1. Generating targets...")
targets_out = subprocess.check_output(['python3', 'scripts/prospect_veille.py', 'generate_search_targets'])
targets_json = json.loads(targets_out.decode('utf-8'))
queries = random.sample(targets_json['web_search_queries'], 4)
print(f"Selected queries: {queries}")

# 2. Web Search & 3. Filter URLs
print("2 & 3. Web Search & Filter URLs...")
all_filtered = []
for q in queries:
    # Use Brave Search API or similar if available, but since I don't have python bindings for web_search,
    # I'll just simulate the search with a hardcoded URL or duckduckgo html scrape for speed,
    # OR better, use Maton gateway web search:
    url = f"https://gateway.maton.ai/search/web?q={urllib.parse.quote(q)}"
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {os.environ.get("MATON_API_KEY")}')
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            results = data.get('results', [])
            
            # Formate pour le filtre
            payload = json.dumps([{"query": q, "results": results}])
            proc = subprocess.Popen(['python3', 'scripts/prospect_veille.py', 'filter_urls_for_agent_browser'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            out, err = proc.communicate(input=payload.encode('utf-8'))
            filtered = json.loads(out.decode('utf-8'))
            all_filtered.extend(filtered)
    except Exception as e:
        print(f"Search failed for {q}: {e}")

print(f"Filtered URLs: {len(all_filtered)}")

# 4. Extract Pages & 5. Process
print("4 & 5. Extract Pages & Process...")
opportunities = []
for item in all_filtered[:3]: # Limit to 3 for speed
    print(f"Extracting {item['url']}...")
    try:
        url_extract = f"https://gateway.maton.ai/extract/web?url={urllib.parse.quote(item['url'])}&format=text"
        req = urllib.request.Request(url_extract)
        req.add_header('Authorization', f'Bearer {os.environ.get("MATON_API_KEY")}')
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            item['extracted_content'] = data.get('content', '')[:2000] # Limite la taille
            opportunities.append(item)
    except Exception as e:
        print(f"Extraction failed for {item['url']}: {e}")

if opportunities:
    print("Processing opportunities...")
    payload = json.dumps(opportunities)
    proc = subprocess.Popen(['python3', 'scripts/prospect_veille.py', 'process_opportunities'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = proc.communicate(input=payload.encode('utf-8'))
    print(out.decode('utf-8'))
else:
    print("No opportunities to process.")
    proc = subprocess.Popen(['python3', 'scripts/prospect_veille.py', 'process_opportunities'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    proc.communicate(input="[]".encode('utf-8'))

print("Done.")