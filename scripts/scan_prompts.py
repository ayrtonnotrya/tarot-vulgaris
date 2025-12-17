import os
import re
import json
import random

# Configuration
# Configuration
# Determine project root relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

ASSETS_DIR = os.path.join(PROJECT_ROOT, 'assets', 'raw')
SOURCE_DIRS = [os.path.join(PROJECT_ROOT, 'arcanos-maiores'), os.path.join(PROJECT_ROOT, 'arcanos-menores')]

def get_existing_images(basename):
    existing = []
    if not os.path.exists(ASSETS_DIR):
        return existing
    
    # Check for p1, p2, p3 with jpg or png extensions
    for i in range(1, 4):
        for ext in [".png", ".jpg", ".jpeg"]:
            candidate = f"{basename}_p{i}{ext}"
            if os.path.exists(os.path.join(ASSETS_DIR, candidate)):
                existing.append(i)
                break
    return existing

def parse_markdown(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return None


    # Find the visual prompts section
    # matches "## 🎨 Prompts Visuais" followed by anything until a line start with "## " (but not "###") or End of String
    # We use (?m) flag for multiline to let ^ match start of line, but since we read whole content, we just use \n
    
    # Simpler approach: Split by "## " and find the one with "🎨 Prompts Visuais"
    parts = re.split(r'\n## ', content)
    target_part = None
    for part in parts:
        if part.strip().startswith("🎨 Prompts Visuais") or "🎨 Prompts Visuais" in part.split('\n')[0]:
            target_part = part
            break
            
    if not target_part:
        return None
    
    section_text = target_part
    
    # Extract options
    prompts = {}
    
    # Regex to find "Opção X" followed by "**Prompt:** ...text..."
    # We look for "### Opção X" then content until next "###" or end
    
    # Split by "### Opção "
    option_parts = re.split(r'### Opção ', section_text)
    
    for opt_part in option_parts[1:]: # Skip first chunk before first option
        # opt_part starts with number usually
        # "1\n**Prompt:** ... "
        try:
            lines = opt_part.strip().split('\n')
            option_num = int(lines[0].strip())
            
            # Find the prompt text
            # Join lines back to search for **Prompt:**
            full_text = "\n".join(lines[1:])
            
            prompt_match = re.search(r'\*\*Prompt:\*\*\s*(.+)', full_text, re.DOTALL)
            if prompt_match:
                prompts[option_num] = prompt_match.group(1).strip()
        except Exception:
            pass
        
    return prompts


def scan_and_plan():
    tasks = []
    print(f"Scanning directories: {SOURCE_DIRS}")
    
    for source_dir in SOURCE_DIRS:
        if not os.path.exists(source_dir):
            print(f"Directory not found: {source_dir}")
            continue
            
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.endswith(".md") and file != "README.md":
                    filepath = os.path.join(root, file)
                    basename = os.path.splitext(file)[0]
                    
                    # 1. Get existing images
                    existing = get_existing_images(basename)
                    # print(f"Checking {basename}: existing={existing}") # Verbose
                    
                    # If all 3 exist, skip
                    if len(existing) >= 3:
                        # print(f"Skipping {basename}, all images exist.")
                        continue
                        
                    # 2. Parse prompts
                    prompts = parse_markdown(filepath)
                    if not prompts:
                        print(f"Failed to parse prompts for {basename} in {filepath}")
                        # Let's see why - read the file start
                        # with open(filepath, 'r') as f: print(f.read(500)) 
                        continue
                        
                    # 3. Determine missing options
                    missing_options = [k for k in prompts.keys() if k not in existing]
                    
                    if not missing_options:
                        continue
                        
                    # 4. Pick one random missing option
                    selected_option = random.choice(missing_options)
                    selected_prompt = prompts[selected_option]
                    
                    tasks.append({
                        "card_name": basename,
                        "option_selected": selected_option,
                        "prompt": selected_prompt,
                        "expected_filename": f"{basename}_p{selected_option}.png"
                    })
    
    print(f"Total tasks found: {len(tasks)}")
    return tasks

if __name__ == "__main__":
    tasks = scan_and_plan()
    with open(os.path.join(PROJECT_ROOT, 'data', 'tasks.json'), "w") as f:
        json.dump(tasks, f, indent=2)
    print(f"Tasks saved to tasks.json")
