
import os
import re
import json

PROJECT_ROOT = "/home/ayrtondouglas/Projetos/tarot-vulgaris"
MAJORS_DIR = os.path.join(PROJECT_ROOT, "arcanos-maiores")
MINORS_DIR = os.path.join(PROJECT_ROOT, "arcanos-menores")
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "data/tasks_missing.json")

# Missing cards identified in audit
MISSING_CARDS = [
    "20_o_serasa",
    "32_valete_o_estagiario",
    "60_valete_o_hater",
    "62_rainha_a_atendente_de_cartorio",
    "64_as_o_13_salario",
    "65_o_cunhado_folgado",
    "71_o_bico",
    "73_a_casa_propria_quitada",
    "74_valete_o_vendedor_de_bala",
    "76_rainha_a_perua_do_shopping"
]

def find_card_path(card_name):
    # Check majors
    p = os.path.join(MAJORS_DIR, f"{card_name}.md")
    if os.path.exists(p): return p
    # Check minors (recursive)
    for root, _, files in os.walk(MINORS_DIR):
        if f"{card_name}.md" in files:
            return os.path.join(root, f"{card_name}.md")
    return None

def extract_prompt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Try to find "Opção 1" prompt using regex
    # Pattern looks for "### Opção 1" followed by "**Prompt:**" or just the text
    # This regex attempts to capture the text after **Prompt:** until the next newline or section
    pattern = r"\*\*Prompt:\*\*\s*(.*?)(?=\n\n|\n###|$)"
    
    # First, narrow down to Opção 1 if possible
    op1_match = re.search(r"### Opção 1(.*?)(### Opção 2|$)", content, re.DOTALL)
    if op1_match:
        section_content = op1_match.group(1)
        prompt_match = re.search(pattern, section_content, re.DOTALL)
        if prompt_match:
            return prompt_match.group(1).strip()
    
    # Fallback: search anywhere
    prompt_match = re.search(pattern, content, re.DOTALL)
    if prompt_match:
        return prompt_match.group(1).strip()
        
    return "PROMPT NOT FOUND"

def main():
    tasks = []
    
    print(f"Generating tasks for {len(MISSING_CARDS)} missing cards...")
    
    for card in MISSING_CARDS:
        path = find_card_path(card)
        if not path:
            print(f"WARNING: Could not find file for {card}")
            continue
            
        prompt = extract_prompt(path)
        
        task = {
            "card_name": card,
            "option_selected": 1,
            "prompt": prompt,
            "expected_filename": f"{card}_p1.png"
        }
        tasks.append(task)
        print(f"Processed {card}")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully wrote {len(tasks)} tasks to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
