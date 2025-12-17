
import os
import re

PROJECT_ROOT = "/home/ayrtondouglas/Projetos/tarot-vulgaris"
MAJORS_DIR = os.path.join(PROJECT_ROOT, "arcanos-maiores")
MINORS_DIR = os.path.join(PROJECT_ROOT, "arcanos-menores")
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets/raw")

def get_markdown_files(root_dir):
    md_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".md") and not file.startswith("_"): # Ignore _intro.md etc if any
                # Store full path and filename without extension
                md_files.append({
                    "path": os.path.join(root, file),
                    "filename": file,
                    "stem": os.path.splitext(file)[0]
                })
    return md_files

def get_image_assets(assets_dir):
    assets = []
    if not os.path.exists(assets_dir):
        return []
        
    for file in os.listdir(assets_dir):
        if file.endswith(".png"):
            # logic: image usually has _pX suffix, e.g., 22_name_p1.png
            # We need to match it to 22_name.md
            # So we check if the asset STARTS with the stem of the markdown
            assets.append(file)
    return assets

def audit():
    print("--- INICIANDO AUDITORIA DE IMAGENS ---")
    
    # 1. Gather Card Definitions
    majors = get_markdown_files(MAJORS_DIR)
    minors = get_markdown_files(MINORS_DIR)
    all_cards = majors + minors
    
    print(f"Total de Cartas Encontradas (Markdown): {len(all_cards)}")
    print(f"  - Arcanos Maiores: {len(majors)}")
    print(f"  - Arcanos Menores: {len(minors)}")
    
    # 2. Gather Assets
    assets = get_image_assets(ASSETS_DIR)
    print(f"Total de Imagens em assets/raw: {len(assets)}")
    
    # 3. Check for matches
    missing = []
    found = []
    
    for card in all_cards:
        card_stem = card['stem']
        # We look for ANY image that starts with the card filename
        # e.g. card "22_as_cnpj_mei" matches "22_as_cnpj_mei_p1.png" or "22_as_cnpj_mei.png"
        match = False
        for asset in assets:
            if asset.startswith(card_stem):
                match = True
                break
        
        if match:
            found.append(card_stem)
        else:
            missing.append(card)

    # 4. Report
    print(f"\n--- RESULTADO ---")
    print(f"Imagens Encontradas: {len(found)}")
    print(f"Imagens Faltantes: {len(missing)}")
    
    if len(missing) > 0:
        print("\nLista de Cartas SEM Imagem em assets/raw:")
        for card in sorted(missing, key=lambda x: x['filename']):
            print(f"  [X] {card['filename']} ({os.path.relpath(card['path'], PROJECT_ROOT)})")
    else:
        print("\n\u2705 Todas as cartas possuem imagens correspondentes!")

if __name__ == "__main__":
    audit()
