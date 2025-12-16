import os
import re

# ==============================================================================
# ADVICE DICTIONARIES
# ==============================================================================

ADVICE_MAIORES = {
    "00": "Se a vida te der lixo, abane o rabo e finja que é confete. O segredo é não ter pedigree.",
    "01": "Se não tem conserto, é porque você usou pouco arame. A física é apenas uma sugestão.",
    "02": "Nem tudo é encosto, às vezes é só dor nas costas mesmo. Mas na dúvida, toma um banho de sal grosso.",
    "03": "Amor de mãe é sagrado, mas o boleto também vence. Não romantize a dependência.",
    "04": "Regras existem para serem seguidas, exceto quando o síndico não está olhando.",
    "05": "Você sabe com quem está falando? Com um idiota que acha que diploma é coroa.",
    "06": "Três é demais só pra quem tem coração pequeno. O problema é dividir a conta do bar.",
    "07": "A vida é um corredor entre dois ônibus. Acelera ou vira estatística.",
    "08": "Amor não enche barriga, mas merenda sim. Respeite quem te alimenta.",
    "09": "O segredo da sabedoria é ver tudo, ouvir tudo e fingir demência na hora certa.",
    "10": "A vida cobra entrada. Se não tiver crédito, pule. Mas cuidado com o segurança.",
    "11": "Pagar é obrigação, mas pagar sorrindo é evolução espiritual (ou deboche).",
    "12": "O transporte público é o purgatório moderno. Aguente firme, a redenção é o fim de semana.",
    "13": "Se perdeu, perdeu. O importante é estar vivo para comprar outro celular parcelado.",
    "14": "Não deixe a carne queimar enquanto cuida da vida dos outros. Foco na picanha.",
    "15": "O limite do cartão é a medida da sua ilusão. Use com moderação ou venda a alma.",
    "16": "Natal sem barraco é apenas um jantar chato. A verdade liberta, mas a família prende.",
    "17": "Brilhe, mona. O mundo é cinza demais para você ser básica.",
    "18": "Se está na internet, deve ser verdade. Disse ninguém inteligente, nunca.",
    "19": "O sol nasce para todos, mas o protetor solar é caro. Descasque com dignidade.",
    "20": "Nome sujo se limpa. Caráter sujo, nem com água sanitária.",
    "21": "Trabalhe enquanto eles dormem, para dormir quando eles estiverem infartando.",
}

ADVICE_MENORES = {
    # PAUS (CORRE)
    "CORRE_01": "Começou agora e já quer sentar na janela? Vai buscar café.",
    "CORRE_02": "Planejar é bom, mas fazer é melhor. Sai do PowerPoint e vai pro Excel.",
    "CORRE_03": "O time tá crescendo, mas a paciência tá diminuindo. Lidere ou saia da frente.",
    "CORRE_04": "Comemorar meta batida é obrigação. Se não tiver festa, vira trabalho escravo.",
    "CORRE_05": "Competição saudável é o caramba. É briga de foice no escuro.",
    "CORRE_06": "Ganhou o prêmio de funcionário do mês? Parabéns, agora trabalhe o dobro.",
    "CORRE_07": "Tão tentando puxar seu tapete? Pise firme ou aprenda a voar.",
    "CORRE_08": "Tá tudo acontecendo ao mesmo tempo. Se vira nos 30 ou surta.",
    "CORRE_09": "Cansado? O boleto não liga. Descansa quando morrer (mentira, descansa agora senão morre).",
    "CORRE_10": "Carregar a empresa nas costas dá hérnia de disco, não aumento.",
    "CORRE_11_VALETE": "O estagiário empolgado. Calma, jovem. A alma é a primeira coisa que o RH leva.",
    "CORRE_12_CAVALEIRO": "O vendedor agressivo. Vende a mãe pra bater meta. Cuidado pra não se vender junto.",
    "CORRE_13_RAINHA": "A gestora carismática. Manda com sorriso, demite com abraço.",
    "CORRE_14_REI": "O CEO visionário (ou alucinado). Segue ele quem tem juízo (ou quem não tem opção).",
    
    # COPAS (BREJA)
    "BREJA_01": "O amor é lindo, a ressaca é feia. Aproveite o início, porque o fim é sempre dor de cabeça.",
    "BREJA_02": "Parceria de bar é sagrada. Se ele paga a saideira, é pra casar.",
    "BREJA_03": "Amigos, cerveja e conversa fiada. A terapia de pobre que funciona.",
    "BREJA_04": "Tá chato? A cerveja esquentou? Vai pra casa ou pede outra. Só não reclama.",
    "BREJA_05": "Chorar pelo leite derramado não enche o copo. Seca as lágrimas e pede a conta.",
    "BREJA_06": "Lembrar do passado é bom, viver nele é patético. O ex não vai voltar, supera.",
    "BREJA_07": "Tantas opções no cardápio e você escolhe a que te faz mal. Típico.",
    "BREJA_08": "Hora de ir embora. A festa acabou, a dignidade ficou no chão. Tchau.",
    "BREJA_09": "Sozinho, feliz e bêbado. Quem precisa de gente quando se tem autossuficiência etílica?",
    "BREJA_10": "Família reunida, churrasco e confusão. A felicidade é barulhenta mesmo.",
    "BREJA_11_VALETE": "O emocionado. Se apaixona no ônibus, sofre no metrô.",
    "BREJA_12_CAVALEIRO": "O Don Juan de boteco. Promete o mundo, entrega um latão.",
    "BREJA_13_RAINHA": "A amiga conselheira. Ouve seus dramas, bebe sua cerveja e te manda a real.",
    "BREJA_14_REI": "O paizão do rolê. Cuida de todos, paga a conta e ainda leva o bêbado pra casa.",

    # ESPADAS (TRETA)
    "TRETA_01": "A verdade dói, mas a mentira mata aos poucos. Escolha sua arma.",
    "TRETA_02": "Em cima do muro você só leva tiro dos dois lados. Desce daí.",
    "TRETA_03": "Coração partido cola. O problema é que sempre sobra peça.",
    "TRETA_04": "Dorme que passa. Se não passar, pelo menos você descansou pra sofrer com energia.",
    "TRETA_05": "Ganhar a discussão e perder o amigo. Valeu a pena, palestrinha?",
    "TRETA_06": "Fugir dos problemas é cardio. Corre, mas corre pra longe.",
    "TRETA_07": "A malandragem é uma arte, a mentira é um ofício. Cuidado pra não ser pego.",
    "TRETA_08": "Você criou sua própria prisão. A chave tá na sua mão, mas você gosta do drama.",
    "TRETA_09": "Insônia é a consciência cobrando hora extra. Toma um chá e resolve amanhã.",
    "TRETA_10": "Chegou no fundo do poço? Ótimo, agora só dá pra subir (ou cavar mais, não recomendo).",
    "TRETA_11_VALETE": "O Hater. Falar mal é fácil, fazer melhor que é difícil.",
    "TRETA_12_CAVALEIRO": "O revolucionário de teclado. Muita agressividade, pouco argumento.",
    "TRETA_13_RAINHA": "A fria e calculista. Corta laços sem anestesia. Aprenda com ela.",
    "TRETA_14_REI": "O dono da razão. Ele não discute, ele informa que você está errado.",

    # OUROS (GRANA)
    "GRANA_01": "Dinheiro na mão é vendaval. Invista ou gaste, só não deixe parado.",
    "GRANA_02": "Malabarismo financeiro. É tirar de um cartão pra pagar o outro. Cuidado pra não cair.",
    "GRANA_03": "Trabalho em equipe faz o sonho virar realidade (ou pesadelo, dependendo da equipe).",
    "GRANA_04": "O mão de vaca. Guarda tanto que esquece de viver. O caixão não tem gaveta.",
    "GRANA_05": "A pindaíba. Passa, mas deixa cicatriz. Aprenda a lição: tenha reserva.",
    "GRANA_06": "Quem dá aos pobres empresta a Deus. E quem pede emprestado perde o amigo.",
    "GRANA_07": "Plantou, agora espera. Ficar olhando não faz crescer mais rápido.",
    "GRANA_08": "Trabalho de formiguinha. Ninguém vê, mas é o que constrói o império.",
    "GRANA_09": "O luxo da independência. Pagar as próprias contas é o melhor afrodisíaco.",
    "GRANA_10": "Herança e tradição. Dinheiro velho fala baixo, dinheiro novo grita.",
    "GRANA_11_VALETE": "O estudante ambicioso. Quer ficar rico rápido. Spoiler: vai demorar.",
    "GRANA_12_CAVALEIRO": "O trabalhador incansável. Devagar e sempre. Chega lá, mas chega cansado.",
    "GRANA_13_RAINHA": "A empresária prática. Transforma tudo em lucro. Cuida do jardim e do cofre.",
    "GRANA_14_REI": "O magnata. Tem dinheiro, poder e responsabilidade. O peso da coroa é feito de ouro.",
}

# ==============================================================================
# PARSING LOGIC
# ==============================================================================

def parse_maiores_robust(filepath):
    """
    Parses Arcanos Maiores text file by splitting on separators.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by the separator line using regex for safety (10 or more dashes)
    blocks = re.split(r'-{10,}', content)
    
    results = []
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        
        # Identify Card ID inside [XX]
        # First line usually: [00] O VIRA-LATA CARAMELO
        lines = block.split('\n')
        
        # Find the line starting with [ID]
        # It might be the first line, or after some header text in the first block
        title_line = None
        id_match = None
        
        for line in lines:
            m = re.match(r'\[(\d+)\]\s+(.*)', line.strip())
            if m:
                title_line = line.strip()
                id_match = m
                break
        
        if not id_match:
            continue
            
        card_id = id_match.group(1)
        # Fix title case to Title Case but generally just take it as is.
        # The prompt asks for Title. Let's keep it UPPER implies by source but we can title case if we want.
        # Let's keep strict to source mostly, but maybe Title Case looks better? 
        # Source has "O VIRA-LATA CARAMELO". Let's simply Clean it.
        title = id_match.group(2).strip()

        # Extract sections using string finding for robustness vs regex on multiline
        # We look for "CONCEITO:", "LUZ ...:", "SOMBRA ...:"
        
        concept = ""
        luz = ""
        sombra = ""
        
        # Find indices
        # Note: LUZ and SOMBRA lines have variations like "LUZ (VIRTUDES...):"
        
        # Join lines back to search in text
        # But wait, we can just iterate.
        
        current_section = None
        buffer_concept = []
        buffer_luz = []
        buffer_sombra = []
        
        for line in lines[1:]:
            line_str = line.strip()
            
            if line_str.startswith("CONCEITO:"):
                current_section = "CONCEITO"
                content_part = line_str.replace("CONCEITO:", "").strip()
                if content_part: buffer_concept.append(content_part)
            elif line_str.startswith("LUZ") and ":" in line_str:
                current_section = "LUZ"
            elif line_str.startswith("SOMBRA") and ":" in line_str:
                current_section = "SOMBRA"
            else:
                if current_section == "CONCEITO":
                    if line_str: buffer_concept.append(line_str)
                elif current_section == "LUZ":
                    if line_str: buffer_luz.append(line_str)
                elif current_section == "SOMBRA":
                    if line_str: buffer_sombra.append(line_str)
        
        results.append({
            'naipe': None,
            'id': card_id, # '00'
            'title': title, # 'O VIRA-LATA CARAMELO'
            'concept': " ".join(buffer_concept).strip(),
            'luz': "\n\n".join(buffer_luz).strip(), # Join paragraphs
            'sombra': "\n\n".join(buffer_sombra).strip()
        })
        
    return results

def parse_menores_robust(filepath):
    """
    Parses Arcanos Menores text file.
    Assumes structure: NAIPE DE ... -> List of cards
    Cars format: [ID] TITLE ... LUZ: ... SOMBRA: ...
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by Naipes
    naipe_blocks = re.split(r'NAIPE DE ', content)[1:] # Skip preamble
    
    results = []
    
    for block in naipe_blocks:
        # Determine Naipe Code
        header = block.split('\n')[0]
        if 'O CORRE' in header: naipe = 'CORRE'
        elif 'A BREJA' in header: naipe = 'BREJA'
        elif 'A TRETA' in header: naipe = 'TRETA'
        elif 'A GRANA' in header: naipe = 'GRANA'
        else: continue
            
        # Split cards by looking for [XX ...
        # Since there is no hard separator like in Maiores, we rely on the header pattern [ID]
        # We can split by regex `\n\[` or iterate lines.
        # Let's iterate lines to be safe.
        
        lines = block.split('\n')
        current_card = None
        
        for line in lines:
            line = line.strip()
            if not line: continue
            
            # Check for new card start
            # Matches [01 - ÁS] or [PAGEM]
            card_start = re.match(r'^\[(.*?)\]\s+(.*)', line)
            
            if card_start:
                # Save previous card
                if current_card:
                    results.append(current_card)
                
                # Start new card
                full_id = card_start.group(1) # '01 - ÁS' or 'PAGEM'
                raw_title = card_start.group(2) # 'A STARTUP'
                
                # Parse ID Key for mapping
                if 'PAGEM' in full_id: id_key = 'PAGEM'
                elif 'CAVALEIRO' in full_id: id_key = 'CAVALEIRO'
                elif 'RAINHA' in full_id: id_key = 'RAINHA'
                elif 'REI' in full_id: id_key = 'REI'
                else: 
                     # '01 - ÁS' -> '01'
                     # '02' -> '02'
                     match_digit = re.match(r'(\d+)', full_id)
                     id_key = match_digit.group(1) if match_digit else "00"
                
                # Normalize Title Prefix for filename matching
                # The filename expects just the suffix title usually or we map strictly by ID.
                # Actually my `find_target_file` logic uses Naipe + ID to find the file, 
                # then we can overwrite title inside if needed?
                # Actually `find_target_file` looks for files starting with '01_', '11_valete_', etc.
                # So we just need the Content ID correct.
                
                current_card = {
                    'naipe': naipe,
                    'id_key': id_key,
                    'title': raw_title,
                    'concept_lines': [],
                    'luz_lines': [],
                    'sombra_lines': [],
                    'section': 'CONCEITO' # Default start if CONCEITO label missing, or wait for labels
                }
                
            elif current_card:
                if line.startswith('LUZ:'):
                    current_card['section'] = 'LUZ'
                    content = line.replace('LUZ:', '').strip()
                    if content: current_card['luz_lines'].append(content)
                elif line.startswith('SOMBRA:'):
                    current_card['section'] = 'SOMBRA'
                    content = line.replace('SOMBRA:', '').strip()
                    if content: current_card['sombra_lines'].append(content)
                else:
                    # Append to current section
                    if current_card['section'] == 'CONCEITO':
                        current_card['concept_lines'].append(line)
                    elif current_card['section'] == 'LUZ':
                        current_card['luz_lines'].append(line)
                    elif current_card['section'] == 'SOMBRA':
                        current_card['sombra_lines'].append(line)
        
        # Add last card
        if current_card:
            results.append(current_card)

    # Post-process results to join lines
    final_results = []
    for c in results:
        # Menores often don't have explicit CONCEITO label in text, so first lines are concept.
        # But sometimes they are just title?
        # In my manual check of Minor text (memory), it was [ID] TITLE \n LUZ: ...
        # So concept might be empty or implicit.
        # If concept empty, generate default? Yes, main() did that.
        
        c['luz'] = "\n\n".join(c['luz_lines']).strip()
        c['sombra'] = "\n\n".join(c['sombra_lines']).strip()
        c['concept'] = " ".join(c['concept_lines']).strip()
        final_results.append(c)

    return final_results

# ==============================================================================
# FILE MATCHING
# ==============================================================================

def find_target_file(card_data, root_dir):
    """Finds the .md file matching the card."""
    
    # Maiores
    if card_data['naipe'] is None:
        target_dir = os.path.join(root_dir, "arcanos-maiores")
        prefix = card_data['id'] + "_"
        if os.path.exists(target_dir):
            for f in os.listdir(target_dir):
                if f.startswith(prefix) and f.endswith(".md"):
                    return os.path.join(target_dir, f)
    
    # Menores
    else:
        # Map naipe code to folder
        naipe_map = {
            'CORRE': 'naipe-corre',
            'BREJA': 'naipe-breja',
            'TRETA': 'naipe-treta',
            'GRANA': 'naipe-grana'
        }
        target_dir = os.path.join(root_dir, "arcanos-menores", naipe_map[card_data['naipe']])
        
        # Map id_key to filename prefix
        if card_data['id_key'].isdigit():
            # Pad if needed, but '01' is already 01. '10' is 10.
            prefix = card_data['id_key'] + "_"
        elif card_data['id_key'] == 'PAGEM': prefix = "11_valete_"
        elif card_data['id_key'] == 'CAVALEIRO': prefix = "12_cavaleiro_"
        elif card_data['id_key'] == 'RAINHA': prefix = "13_rainha_"
        elif card_data['id_key'] == 'REI': prefix = "14_rei_"
        else: return None
        
        if os.path.exists(target_dir):
            for f in os.listdir(target_dir):
                if f.startswith(prefix) and f.endswith(".md"):
                    return os.path.join(target_dir, f)
    
    return None

def main():
    root = "."
    
    # Process Maiores
    print("Processando Arcanos Maiores...")
    maiores = parse_maiores_robust("interpretacoes_arcanos_maiores.txt")
    print(f"Found {len(maiores)} Maiores cards.")
    
    for card in maiores:
        fpath = find_target_file(card, root)
        if fpath:
            advice = ADVICE_MAIORES.get(card['id'], "Nada a dizer.")
            content = f"""# {card['title']}

## 📜 Conceito
{card['concept']}

## ☀️ Luz (Virtudes)
{card['luz']}

## 🌑 Sombra (Vícios)
{card['sombra']}

## 💡 Conselho do Curador
{advice}
"""
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)
            # print(f"Update: {fpath}")
        else:
            print(f"MISSING FILE FOR MAIOR: {card['id']} {card['title']}")

    # Process Menores
    print("Processando Arcanos Menores...")
    menores = parse_menores_robust("interpretacoes_arcanos_menores.txt")
    print(f"Found {len(menores)} Menores cards.")
    
    for card in menores:
        fpath = find_target_file(card, root)
        if fpath:
            # Construct advice key e.g. CORRE_01, CORRE_11_VALETE
            if card['id_key'].isdigit():
                advice_key = f"{card['naipe']}_{card['id_key']}"
            else:
                # Need to map text ID to advice key suffix: PAGEM->11_VALETE
                key_map = {
                    'PAGEM': '11_VALETE',
                    'CAVALEIRO': '12_CAVALEIRO',
                    'RAINHA': '13_RAINHA',
                    'REI': '14_REI'
                }
                advice_key = f"{card['naipe']}_{key_map.get(card['id_key'], 'ERROR')}"
            
            advice = ADVICE_MENORES.get(advice_key, "Nada a dizer.")
            
            # Construct Concept from Title if missing
            concept_text = card['concept'] if card['concept'] else f"A carta {card['title']} representa a energia do naipe no cotidiano."
            
            content = f"""# {card['title']}

## 📜 Conceito
{concept_text}

## ☀️ Luz (Virtudes)
{card['luz']}

## 🌑 Sombra (Vícios)
{card['sombra']}

## 💡 Conselho do Curador
{advice}
"""
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)
            # print(f"Update: {fpath}")
        else:
            print(f"MISSING FILE FOR MENOR: {card['naipe']} {card['id_key']}")

if __name__ == "__main__":
    main()
