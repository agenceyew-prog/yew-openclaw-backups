import os
import json

status_file = "/data/.openclaw/workspace/memory/heartbeat-state.json"
state = {}
if os.path.exists(status_file):
    with open(status_file, "r") as f:
        try:
            state = json.load(f)
        except:
            pass

if "lastChecks" not in state:
    state["lastChecks"] = {}

import time
current_time = int(time.time())
state["lastChecks"]["email_drafts"] = current_time
state["lastChecks"]["email_sent"] = current_time
state["lastChecks"]["crm_sync"] = current_time

with open(status_file, "w") as f:
    json.dump(state, f, indent=2)
