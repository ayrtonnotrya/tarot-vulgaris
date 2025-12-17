import json
import os
import sys

# Determine project root relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

TASKS_FILE = os.path.join(PROJECT_ROOT, 'data', 'tasks.json')
ASSETS_DIR = os.path.join(PROJECT_ROOT, 'assets', 'raw')

def get_next():
    if not os.path.exists(TASKS_FILE):
        print("tasks.json not found")
        sys.exit(1)
        
    with open(TASKS_FILE, 'r') as f:
        tasks = json.load(f)
        
    for task in tasks:
        filename = task["expected_filename"]
        path = os.path.join(ASSETS_DIR, filename)
        
        if not os.path.exists(path):
            print(json.dumps(task))
            return
            
    print("DONE")

if __name__ == "__main__":
    get_next()
