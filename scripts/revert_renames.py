import json
import os

# Determine project root relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

TASKS_FILE = os.path.join(PROJECT_ROOT, 'data', 'tasks_output.json')
ASSETS_DIR = os.path.join(PROJECT_ROOT, 'assets', 'raw')

def revert_images():
    if not os.path.exists(TASKS_FILE):
        print(f"Error: Tasks file not found at {TASKS_FILE}")
        return

    if not os.path.exists(ASSETS_DIR):
        print(f"Error: Assets directory not found at {ASSETS_DIR}")
        return

    try:
        with open(TASKS_FILE, 'r') as f:
            tasks = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return

    reverted_count = 0
    missing_count = 0
    skipped_count = 0

    print(f"Starting revert process for {len(tasks)} items...")

    for task in tasks:
        matched_filename = task.get('matched_filename') # The original name we want to restore
        expected_filename = task.get('expected_filename') # The current name (incorrectly renamed)

        if not matched_filename:
            skipped_count += 1
            # print(f"Skipping task for '{task.get('card_name')}' (No matched_filename)")
            continue

        if not expected_filename:
             skipped_count += 1
             # print(f"Skipping task for '{task.get('card_name')}' (No expected_filename)")
             continue
        
        # NOTE: logic is swapped compared to rename_images.py
        current_path = os.path.join(ASSETS_DIR, expected_filename)
        original_path = os.path.join(ASSETS_DIR, matched_filename)

        if os.path.exists(current_path):
            try:
                os.rename(current_path, original_path)
                print(f"[REVERTED] {expected_filename} -> {matched_filename}")
                reverted_count += 1
            except OSError as e:
                print(f"[ERROR] Failed to revert {expected_filename}: {e}")
        else:
            # Check if original already exists (maybe already reverted or never renamed)
            if os.path.exists(original_path):
                 print(f"[INFO] Original file already exists (skipping): {matched_filename}")
                 skipped_count += 1
            else:
                print(f"[MISSING] Current file not found: {expected_filename}")
                missing_count += 1

    print("-" * 30)
    print(f"Summary:")
    print(f"Reverted: {reverted_count}")
    print(f"Missing: {missing_count}")
    print(f"Skipped/NoAction: {skipped_count}")
    print("-" * 30)

if __name__ == "__main__":
    revert_images()
