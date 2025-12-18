
import os
import glob
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURAÇÃO ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_FINAL_DIR = os.path.join(BASE_DIR, 'assets', 'final')
ASSETS_TITLED_DIR = os.path.join(BASE_DIR, 'assets', 'titled')
ARCANOS_MAIORES_DIR = os.path.join(BASE_DIR, 'arcanos-maiores')
ARCANOS_MENORES_DIR = os.path.join(BASE_DIR, 'arcanos-menores')

# Nome da fonte preferencial
FONT_NAME = "IMFellEnglishSC-Regular.ttf" # Nome comum do arquivo da fonte IM Fell English SC
# Tente encontrar a fonte no sistema ou no diretório atual se não achar pelo nome exato
FONT_SEARCH_PATHS = [
    os.path.join(BASE_DIR, FONT_NAME),
    os.path.join(BASE_DIR, 'assets', FONT_NAME),
    "/usr/share/fonts/truetype/" + FONT_NAME,
]

# Configurações da Caixa de Texto (Bounding Box)
# As imagens são 9:16. Vamos assumir uma resolução base para definir porcentagens ou pixels fixos.
# Exemplo: Imagem 1024x1792 (ou similar em proporção)
# A caixa de texto fica na parte inferior.
TEXT_BOX_MARGIN_X = 290  # Margem lateral
TEXT_BOX_HEIGHT_KP = 0.88 # Posição Y inicial (88% da altura)
TEXT_BOX_HEIGHT_MAX_KP = 0.94 # Posição Y final (98% da altura)
TEXT_COLOR = "#1a1a1a" # Quase preto

def find_markdown_file(slug):
    """
    Procura o arquivo markdown correspondente ao slug nos diretórios de arcanos.
    Retorna o caminho completo ou None.
    """
    # Procura recursivamente em arcanos-maiores e arcanos-menores
    search_patterns = [
        os.path.join(ARCANOS_MAIORES_DIR, f"**/{slug}.md"),
        os.path.join(ARCANOS_MENORES_DIR, f"**/{slug}.md")
    ]
    
    for pattern in search_patterns:
        # Usar glob com recursive=True para subpastas (ex: naipe-corre)
        matches = glob.glob(pattern, recursive=True)
        if matches:
            return matches[0]
            
    # Fallback: Tentar encontrar arquivo que contenha o slug no nome (caso haja pequenas diferenças)
    # Isso é perigoso se slugs forem muito parecidos, mas útil se houver prefixos extras.
    # Por enquanto, mantemos a busca exata pelo nome do arquivo.
    return None

def extract_title_from_md(md_path):
    """
    Lê o arquivo markdown e extrai o título.
    Prioridade: Campo 'Título:' (não existe atualmente), Fallback: Header H1 (# Titulo).
    """
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            stripped = line.strip()
            # Se encontrar o campo Título (futuro)
            if stripped.lower().startswith("título:"):
                return stripped.split(":", 1)[1].strip()
            # Se encontrar o Header H1
            if stripped.startswith("# "):
                title = stripped[2:].strip()
                # Remove formatação markdown extra se houver (negrito dentro do titulo etc)
                title = title.replace("**", "").replace("*", "")
                return title
    except Exception as e:
        print(f"Erro ao ler {md_path}: {e}")
    return None

def load_font(font_path, size):
    try:
        return ImageFont.truetype(font_path, size)
    except IOError:
        return ImageFont.load_default()

def get_best_fit_font(draw, text, box_width, box_height, font_path, max_font_size=120):
    """
    Encontra o maior tamanho de fonte que cabe na caixa (largura e altura).
    """
    size = max_font_size
    font = load_font(font_path, size)
    
    while size > 10:
        # getbbox retorna (left, top, right, bottom)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        if text_width <= box_width and text_height <= box_height:
            return font, text_width, text_height
        
        size -= 1
        font = load_font(font_path, size)
        
    return font, 0, 0 # Fallback extremo

def process_images():
    if not os.path.exists(ASSETS_FINAL_DIR):
        print(f"Diretório de assets não encontrado: {ASSETS_FINAL_DIR}")
        return

    if not os.path.exists(ASSETS_TITLED_DIR):
        os.makedirs(ASSETS_TITLED_DIR)

    # Tenta localizar a fonte
    font_file = None
    # Verifica caminhos de busca
    for path in FONT_SEARCH_PATHS:
        if os.path.exists(path):
            font_file = path
            break
            
    if not font_file:
        # Tenta achar qualquer .ttf no root que pareça ser a fonte ou usa padrao
        ttfs = glob.glob(os.path.join(BASE_DIR, "*.ttf"))
        if ttfs:
            font_file = ttfs[0]
            print(f"⚠️ Fonte exata não encontrada. Usando {font_file}.")
        else:
            print("⚠️ Nenhuma fonte .ttf encontrada. Usando fonte padrão do sistema (pode ficar feio).")
            font_file = "arial.ttf" # Tentativa de safe fallback no linux, ou deixará o PIL falhar para default

    files = sorted(glob.glob(os.path.join(ASSETS_FINAL_DIR, "*.png")))
    print(f"Encontradas {len(files)} imagens para processar.")

    for img_path in files:
        filename = os.path.basename(img_path)
        # Extrai slug:  00_o_vira_lata_caramelo_p3.png -> 00_o_vira_lata_caramelo
        # Remove extensão
        name_no_ext = os.path.splitext(filename)[0]
        # Remove sufixo _pX (assumindo que sempre termina assim)
        parts = name_no_ext.split('_')
        if parts[-1].startswith('p') and parts[-1][1:].isdigit():
             slug = "_".join(parts[:-1])
        else:
            slug = name_no_ext # Caso não tenha pX
            
        print(f"Processing: {filename} -> Slug: {slug}")
        
        md_file = find_markdown_file(slug)
        if not md_file:
            print(f"  ❌ Markdown não encontrado para {slug}. Pulando.")
            continue
            
        title = extract_title_from_md(md_file)
        if not title:
            print(f"  ❌ Título não encontrado em {md_file}. Pulando.")
            continue
            
        # Converter para Title Case se estiver tudo maiúsculo
        # O pedido era "Tipografia Correta". O H1 está em CAPS (METRÔ DA SÉ). 
        # IM Fell English SC é Small Caps, então CAPS funciona bem.
        # Se quiser Title Case: title = title.title()
        # Vou manter original do Markdown por enquanto, assumindo que a fonte SC resolve o estilo.
        
        try:
            with Image.open(img_path) as img:
                # Converter para RGBA para garantir canvas limpo
                img = img.convert("RGBA")
                width, height = img.size
                draw = ImageDraw.Draw(img)
                
                # Definir Bounding Box
                box_x_start = TEXT_BOX_MARGIN_X
                box_x_end = width - TEXT_BOX_MARGIN_X
                box_width = box_x_end - box_x_start
                
                box_y_start = int(height * TEXT_BOX_HEIGHT_KP)
                box_y_end = int(height * TEXT_BOX_HEIGHT_MAX_KP)
                box_height = box_y_end - box_y_start
                
                # Debug: Desenhar caixa (comentar na versão final)
                # draw.rectangle([box_x_start, box_y_start, box_x_end, box_y_end], outline="red")
                
                font, text_w, text_h = get_best_fit_font(draw, title, box_width, box_height, font_file)
                
                # Centralizar
                x = box_x_start + (box_width - text_w) / 2
                # Centralizar verticalmente na caixa + um pequeno ajuste ótico se necessário
                y = box_y_start + (box_height - text_h) / 2
                
                # Desenhar texto
                draw.text((x, y), title, font=font, fill=TEXT_COLOR)
                
                save_path = os.path.join(ASSETS_TITLED_DIR, filename)
                img.save(save_path)
                print(f"  ✅ Salvo em {save_path}")
                
        except Exception as e:
            print(f"  ❌ Erro ao processar imagem: {e}")

if __name__ == "__main__":
    process_images()
