import json
import os

# Determine project root relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

TASKS_FILE = os.path.join(PROJECT_ROOT, 'data', 'tasks_output.json')
ASSETS_DIR = os.path.join(PROJECT_ROOT, 'assets', 'raw')

def rename_images():
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

    renamed_count = 0
    missing_count = 0
    skipped_count = 0

    print(f"Starting rename process for {len(tasks)} items...")

    for task in tasks:
        matched_filename = task.get('matched_filename')
        expected_filename = task.get('expected_filename')

        if not matched_filename:
            skipped_count += 1
            print(f"Skipping task for '{task.get('card_name')}' (No matched_filename)")
            continue

        if not expected_filename:
             skipped_count += 1
             print(f"Skipping task for '{task.get('card_name')}' (No expected_filename)")
             continue
        
        src_path = os.path.join(ASSETS_DIR, matched_filename)
        dst_path = os.path.join(ASSETS_DIR, expected_filename)

        if os.path.exists(src_path):
            try:
                os.rename(src_path, dst_path)
                print(f"[OK] Renamed: {matched_filename} -> {expected_filename}")
                renamed_count += 1
            except OSError as e:
                print(f"[ERROR] Failed to rename {matched_filename}: {e}")
        else:
            # Check if destination already exists (maybe already renamed)
            if os.path.exists(dst_path):
                 print(f"[INFO] Target already exists (skipping): {expected_filename}")
                 skipped_count += 1
            else:
                print(f"[MISSING] Source file not found: {matched_filename}")
                missing_count += 1

    print("-" * 30)
    print(f"Summary:")
    print(f"Renamed: {renamed_count}")
    print(f"Missing: {missing_count}")
    print(f"Skipped/NoMatch: {skipped_count}")
    print("-" * 30)

if __name__ == "__main__":
    rename_images()
