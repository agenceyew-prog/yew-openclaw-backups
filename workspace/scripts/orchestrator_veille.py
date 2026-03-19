# scripts/orchestrator_veille.py
import subprocess
import json
import sys
import os

def run_command(cmd, input_data=None):
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate(input=input_data)
    if process.returncode != 0:
        print(f"Error running command {' '.join(cmd)}: {stderr}")
        return None
    return stdout

def main():
    print("--- Starting Veille Orchestration ---")
    
    # Step 1: Generate Search Targets
    print("Step 1: Generating search targets...")
    targets_json = run_command(["python3", "scripts/prospect_veille.py", "generate_search_targets"])
    if not targets_json: return
    targets = json.loads(targets_json)["web_search_queries"]
    print(f"Generated {len(targets)} queries.")

    # Step 2: Web Search (This needs to be handled by the agent, so we output instructions)
    # Actually, a better way is to have the agent run this script and the script tells the agent what to do.
    # But since this script is run via exec, it can't call tools.
    
    # NEW STRATEGY: 
    # The cron job should trigger a prompt that tells the agent to follow the workflow in MEMORY.md.
    # The agent has access to all tools.
    
    print("Orchestrator script is a placeholder. The agent should handle the workflow directly.")

if __name__ == "__main__":
    main()
