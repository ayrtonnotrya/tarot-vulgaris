import json
import re
import os

# Determine project root relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

INPUT_FILE = os.path.join(PROJECT_ROOT, 'data', 'tasks.json')
OUTPUT_FILE = os.path.join(PROJECT_ROOT, 'data', 'tasks_subjects.json')

def extract_subjects():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    try:
        with open(INPUT_FILE, 'r') as f:
            tasks = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return

    simplified_tasks = []
    
    print(f"Processing {len(tasks)} tasks...")

    for task in tasks:
        prompt = task.get('prompt', '')
        expected_filename = task.get('expected_filename')
        
        # Regex to find text between SUBJECT: and NEGATIVE PROMPT:
        # We use non-greedy matching .*? 
        match = re.search(r'SUBJECT:\s*(.*?)\s*(?:NEGATIVE PROMPT:|$)', prompt, re.IGNORECASE | re.DOTALL)
        
        if match:
            subject = match.group(1).strip()
        else:
            # Fallback: if no tags found, use the whole prompt but warn
            print(f"[WARN] No SUBJECT tag found for {expected_filename}. Using full prompt.")
            subject = prompt.strip()

        simplified_tasks.append({
            "expected_filename": expected_filename,
            "subject_description": subject
        })

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(simplified_tasks, f, indent=2, ensure_ascii=False)

    print(f"Successfully created {OUTPUT_FILE}")
    print(f"Total items: {len(simplified_tasks)}")

if __name__ == "__main__":
    extract_subjects()
