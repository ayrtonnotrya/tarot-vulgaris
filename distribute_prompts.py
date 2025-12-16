import os
import re
import glob
import unicodedata

# 1. Setup & Helper Functions
def normalize(text):
    """Normalize text: lowercase, remove accents, remove special chars."""
    text = text.lower()
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text.strip()

def get_target_files(root_dir):
    """Recursively find all .md files in arcanos directories."""
    files = []
    # Using specific paths to avoid matching README or others
    patterns = [
        os.path.join(root_dir, "arcanos-maiores", "*.md"),
        os.path.join(root_dir, "arcanos-menores", "**", "*.md")
    ]
    for pattern in patterns:
        files.extend(glob.glob(pattern, recursive=True))
    return files

def parse_prompts_file(filepath):
    """Parse the prompts_cards.txt file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into card blocks. 
    # Blocks start with ### [ID] NAME
    # We use a lookahead to split but keep the delimiter, or just regex finditer.
    # Regex for header: ### \[(.*?)\] (.*)
    
    card_regex = re.compile(r'### \[(.*?)\] (.*?)\n(.*?)(?=\n### |$)', re.DOTALL)
    matches = card_regex.findall(content)
    
    cards_data = []
    for m in matches:
        card_id_raw = m[0].strip()
        card_name_raw = m[1].strip()
        body = m[2].strip()
        
        # Extract prompts
        p1 = re.search(r'\*\*Prompt 1:\*\* (.*?)(\n|$)', body)
        p2 = re.search(r'\*\*Prompt 2:\*\* (.*?)(\n|$)', body)
        p3 = re.search(r'\*\*Prompt 3:\*\* (.*?)(\n|$)', body)
        
        if p1 and p2 and p3:
            cards_data.append({
                'id_raw': card_id_raw,
                'name_raw': card_name_raw,
                'prompts': [p1.group(1).strip(), p2.group(1).strip(), p3.group(1).strip()]
            })
        else:
            print(f"Warning: Could not find all 3 prompts for {card_name_raw}")
            
    return cards_data

def find_matching_file(card_data, file_list):
    """Find the specific markdown file for a card."""
    id_raw = card_data['id_raw']
    name_normalized = normalize(card_data['name_raw'])
    
    # Determine search criteria based on ID
    search_terms = []
    
    # Check for court cards first
    if "PAGEM" in id_raw.upper():
        search_terms.append("11_valete") # Primary convention
        search_terms.append("valete")    # Fallback
    elif "CAVALEIRO" in id_raw.upper():
        search_terms.append("12_cavaleiro")
        search_terms.append("cavaleiro")
    elif "RAINHA" in id_raw.upper():
        search_terms.append("13_rainha")
        search_terms.append("rainha")
    elif "REI" in id_raw.upper():
        search_terms.append("14_rei")
        search_terms.append("rei")
    else:
        # Numeric case: [00], [01], [01 - ÁS]
        # Extract the number
        num_match = re.search(r'\d+', id_raw)
        if num_match:
            number = num_match.group(0).zfill(2) # Ensure 01, 00, etc.
            search_terms.append(f"{number}_") # Look for prefix like 00_ or 20_
        else:
            print(f"Warning: Could not parse ID {id_raw}")
            return None

    # Name keywords (exclude short stopwords if needed, but simple contains usually works)
    # Strategy: Filter files that match the "Rank/Number" criteria, then fuzzy match name.
    
    candidates = []
    for f in file_list:
        fname = os.path.basename(f)
        f_norm = normalize(fname)
        
        # Check constraints
        matches_constraint = False
        for term in search_terms:
            if term in fname: # Use raw fname for number/rank matching just to be safe (case usually lower)
                matches_constraint = True
                break
        
        if matches_constraint:
            candidates.append(f)
    
    # Now narrow down by name
    # We check if significant parts of the name are in the filename
    name_tokens = name_normalized.split()
    # Filter out very common words if they might cause ambiguity, but usually fine to keep all
    # Exception: "O", "A", "DE", "DA", "DO" might be missing in filename shortcuts
    filtered_tokens = [t for t in name_tokens if t not in ['o', 'a', 'os', 'as', 'de', 'da', 'do', 'em', 'no', 'na']]
    
    best_match = None
    max_matches = 0
    
    if not filtered_tokens: 
        # If name was just "O A", fall back to original
        filtered_tokens = name_tokens

    for cand in candidates:
        fname_norm = normalize(os.path.basename(cand))
        matches = 0
        for token in filtered_tokens:
            if token in fname_norm:
                matches += 1
        
        # We need a strong match. At least distinct tokens should match.
        if matches == len(filtered_tokens):
             return cand # Perfect match
        
        if matches > max_matches:
            max_matches = matches
            best_match = cand
            
    # If we have a decent partial match (e.g. most tokens)
    if best_match and max_matches >= max(1, len(filtered_tokens) - 1):
        return best_match
        
    return None

def update_file_content(filepath, prompts):
    """Append or update the prompts section in the file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove existing section if present (to update it)
    # Searching for the specific header we are about to add
    header = "## 🎨 Prompts Visuais (Nano Banana)"
    
    # Simple logic: If header exists, truncate from there. If not, append.
    if header in content:
        # Find the start of the header
        idx = content.find(header)
        # Check if there is a '---' before it that we should also remove/reuse? 
        # The instructions say "Adicione uma linha separadora horizontal (---) antes da nova seção".
        # Let's see if we can find existing block and replace it carefully.
        # To be safe, let's cut off everything from `---` before that matched header if it exists nearby.
        
        # Look backwards from idx for '---'
        pre_header_chunk = content[:idx]
        last_dash_idx = pre_header_chunk.rfind('---')
        
        # If '---' is found and is reasonably close (whitespace only in between), cut from there.
        if last_dash_idx != -1 and not pre_header_chunk[last_dash_idx+3:].strip():
            content = content[:last_dash_idx].rstrip()
        else:
            content = content[:idx].rstrip()
    
    # Construct new section
    new_section = f"\n\n---\n\n{header}\n\n"
    new_section += f"### Opção 1\n**Prompt:** {prompts[0]}\n\n"
    new_section += f"### Opção 2\n**Prompt:** {prompts[1]}\n\n"
    new_section += f"### Opção 3\n**Prompt:** {prompts[2]}\n"
    
    final_content = content + new_section
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(final_content)
    return True

# 2. Main Logic
def main():
    root_dir = "/home/ayrtondouglas/Projetos/tarot-vulgaris"
    prompts_file = os.path.join(root_dir, "prompts_cards.txt")
    
    print("Parsing prompts file...")
    cards = parse_prompts_file(prompts_file)
    print(f"Found {len(cards)} card entries.")
    
    print("Locating markdown files...")
    md_files = get_target_files(root_dir)
    print(f"Found {len(md_files)} markdown files.")
    
    updates = 0
    errors = []
    
    for card in cards:
        match = find_matching_file(card, md_files)
        if match:
            # print(f"Matching '{card['name_raw']}' -> {os.path.basename(match)}")
            update_file_content(match, card['prompts'])
            updates += 1
        else:
            msg = f"Arquivo não encontrado para: {card['name_raw']} ({card['id_raw']})"
            print(msg)
            errors.append(msg)
            
    print(f"\nCompleted. Updated {updates} files.")
    if errors:
        print("\nErrors:")
        for e in errors:
            print(e)

if __name__ == "__main__":
    main()
