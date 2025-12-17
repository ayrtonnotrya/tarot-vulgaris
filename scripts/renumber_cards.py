import os
import re
import json
import shutil

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCANOS_MENORES_DIR = os.path.join(PROJECT_ROOT, 'arcanos-menores')
ASSETS_RAW_DIR = os.path.join(PROJECT_ROOT, 'assets', 'raw')
ASSETS_OPT_DIR = os.path.join(PROJECT_ROOT, 'assets', 'optimized')
ASSETS_DRAFT_DIR = os.path.join(PROJECT_ROOT, 'assets', 'draft')
DATA_TASKS_JSON = os.path.join(PROJECT_ROOT, 'data', 'tasks.json')
DATA_TASKS_REPAROS_JSON = os.path.join(PROJECT_ROOT, 'data', 'tasks_reparos.json')

# Mapping Strategy
# 00-21: Majors (Unchanged)
# 22-35: naipe-corre (Wands) -> +21
# 36-49: naipe-breja (Cups) -> +35
# 50-63: naipe-treta (Swords) -> +49
# 64-77: naipe-grana (Pentacles) -> +63

SUIT_OFFSETS = {
    'naipe-corre': 21,
    'naipe-breja': 35,
    'naipe-treta': 49,
    'naipe-grana': 63
}

def get_new_number(suit_dir, current_number):
    if suit_dir not in SUIT_OFFSETS:
        return None
    try:
        num = int(current_number)
        return num + SUIT_OFFSETS[suit_dir]
    except ValueError:
        return None

def rename_file(old_path, new_path):
    if os.path.exists(new_path):
        print(f"WARNING: Target {new_path} already exists! Skipping {old_path}")
        return False
    print(f"Renaming: {os.path.basename(old_path)} -> {os.path.basename(new_path)}")
    os.rename(old_path, new_path)
    return True

def process_markdown_files():
    renamed_map = {} # old_name_base -> new_name_base

    for suit_dir in SUIT_OFFSETS.keys():
        dir_path = os.path.join(ARCANOS_MENORES_DIR, suit_dir)
        if not os.path.exists(dir_path):
            continue
        
        for filename in os.listdir(dir_path):
            if not filename.endswith('.md'):
                continue
            
            # Match strict pattern: 01_something.md
            match = re.match(r'^(\d{2})_(.+)\.md$', filename)
            if match:
                current_num_str = match.group(1)
                name_suffix = match.group(2)
                
                new_num = get_new_number(suit_dir, current_num_str)
                if new_num is not None:
                    new_num_str = f"{new_num:02d}"
                    new_filename = f"{new_num_str}_{name_suffix}.md"
                    
                    old_path = os.path.join(dir_path, filename)
                    new_path = os.path.join(dir_path, new_filename)
                    
                    if rename_file(old_path, new_path):
                        old_base = f"{current_num_str}_{name_suffix}"
                        new_base = f"{new_num_str}_{name_suffix}"
                        renamed_map[old_base] = new_base
    
    return renamed_map

def process_assets(renamed_map):
    asset_dirs = [ASSETS_RAW_DIR, ASSETS_OPT_DIR, ASSETS_DRAFT_DIR]
    
    for dir_path in asset_dirs:
        if not os.path.exists(dir_path):
            continue
            
        print(f"\nProcessing assets in {os.path.basename(dir_path)}...")
        for filename in os.listdir(dir_path):
            # Check if file starts with any old key in renamed_map
            # Pattern expected: old_base + "_pX.png" or just old_base + extension?
            # Usually: 01_name_p1.png
            
            valid_rename = False
            for old_base, new_base in renamed_map.items():
                if filename.startswith(old_base):
                    # verify it is followed by something reasonable (underscore, dot, or p)
                    # to avoid matching 01_foo with 01_foobar
                    suffix = filename[len(old_base):]
                    new_filename = new_base + suffix
                    
                    old_path = os.path.join(dir_path, filename)
                    new_path = os.path.join(dir_path, new_filename)
                    rename_file(old_path, new_path)
                    valid_rename = True
                    break

def update_json_tasks(json_path, renamed_map):
    if not os.path.exists(json_path):
        return

    print(f"\nUpdating {os.path.basename(json_path)}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        tasks = json.load(f)
    
    updated_count = 0
    for task in tasks:
        card_name = task.get('card_name')
        if card_name in renamed_map:
            new_name = renamed_map[card_name]
            task['card_name'] = new_name
            
            # Update expected_filename if present
            expected = task.get('expected_filename')
            if expected and expected.startswith(card_name):
                # Replace start
                task['expected_filename'] = expected.replace(card_name, new_name, 1)
            
            updated_count += 1
            
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)
    print(f"Updated {updated_count} entries.")

def main():
    print("--- Starting Renumbering Process ---")
    
    # 1. Rename Markdown Files & Build Map
    renamed_map = process_markdown_files()
    print(f"\nRenamed {len(renamed_map)} markdown files.")
    
    if not renamed_map:
        print("No files renamed. Exiting.")
        return

    # 2. Rename Assets
    process_assets(renamed_map)
    
    # 3. Update JSONs
    update_json_tasks(DATA_TASKS_JSON, renamed_map)
    update_json_tasks(DATA_TASKS_REPAROS_JSON, renamed_map)
    
    print("\n--- Renumbering Complete ---")

if __name__ == "__main__":
    main()
