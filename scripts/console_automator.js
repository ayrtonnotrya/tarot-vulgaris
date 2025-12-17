/**
 * GEMINI AUTOMATION SCRIPT
 * 
 * INSTRUÇÕES:
 * 1. Abra o Google Gemini (https://gemini.google.com/) no Chrome.
 * 2. Abra o Console do Desenvolvedor (F12 -> Console).
 * 3. Copie todo o conteúdo deste arquivo.
 * 4. Cole o seu JSON de tarefas na constante `TASKS` abaixo (substitua o array vazio).
 * 5. Verifique e atualize os `SELECTORS` se necessário (use o Inspecionar Elemento).
 * 6. Cole o código atualizado no Console e aperte Enter.
 * 7. Digite `startAutomation()` no Console e aperte Enter para iniciar.
 */

// =================================================================================
// 1. CONFIGURAÇÃO (PREENCHA AQUI)
// =================================================================================

// COLE SEU JSON AQUI DENTRO DOS COLCHETES
const TASKS = [
  
];

// SELETORES CSS (ATUALIZE SE O GEMINI MUDAR A INTERFACE)
// Dica: Clique com o botão direito no elemento -> Inspecionar -> Copiar seletor (ou classe única)
const SELECTORS = {
    // A caixa de texto onde você digita o prompt.
    // Geralmente é uma 'div[contenteditable="true"]' ou 'textarea'.
    // Procure por classes como 'ql-editor' ou atributos como 'aria-label="Digitar prompt"'.
    INPUT_BOX: "div.ql-editor.textarea, textarea, div[role='textbox']", 

    // O botão de enviar (aviãozinho).
    // Fica inativo enquanto gera. Procure por 'button[aria-label*="Enviar"]' ou ícones de envio.
    SEND_BUTTON: "button[aria-label='Enviar'], button[aria-label='Send message'], mat-icon[fonticon='send'], mat-icon[data-mat-icon-name='send']",

    // O container ou elemento da IMAGEM gerada.
    // O Gemini costuma gerar 4 imagens ou 1. Procure a tag <img> dentro da resposta mais recente.
    // Dica: Podemos pegar todas as imagens e filtrar a última adicionada.
    GENERATED_IMAGE: "img[src^='https://generated']", 

    // O botão de download nativo do Gemini (AGORA INCLUI MATERIAL ICONS)
    download_BUTTON_CONTAINER: "button", // auxiliar
    DOWNLOAD_BUTTON: "button[aria-label='Fazer download'], button[aria-label='Download full size'], mat-icon[fonticon='download'], mat-icon[data-mat-icon-name='download'], .mat-mdc-tooltip-trigger[aria-label*='download']",
    
    // Indicador de carregamento (spinner) para saber quando terminou.
    // Se existir na tela, o script espera ele sumir.
    LOADING_SPINNER: "mat-progress-spinner, .typing-indicator" 
};

const CONFIG = {
    TYPE_DELAY_MS: 50,       // Tempo entre cada tecla digitada (simulação humana)
    WAIT_AFTER_SEND: 5000,   // Espera fixa após clicar em enviar antes de verificar resultado
    POLL_INTERVAL: 1000,     // Intervalo de verificação (polling)
    DOWNLOAD_WAIT: 3000,     // Tempo para esperar o download iniciar antes de ir p/ próxima
    MAX_WAIT_TIME: 60000     // Tempo máximo de espera por uma geração (60s)
};

// =================================================================================
// 2. FUNÇÕES AUXILIARES
// =================================================================================

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function log(message, color = "cyan") {
    console.log(`%c[AutoGemini] ${message}`, `color: ${color}; font-weight: bold`);
}

/**
 * Simula a digitação humana para disparar eventos de frameworks (React/Angular).
 */
async function simulateTyping(element, text) {
    element.focus();
    element.click();
    
    // Limpa conteúdo anterior se for contenteditable
    if (element.isContentEditable) {
        element.innerText = "";
    } else {
        element.value = "";
    }

    // Digita caractere por caractere
    for (let i = 0; i < text.length; i++) {
        const char = text[i];
        
        // Insere o caractere
        if (element.isContentEditable) {
            element.innerText += char;
        } else {
            element.value += char;
        }

        // Dispara eventos para enganar o framework
        const events = ["input", "keydown", "keyup", "change"];
        events.forEach(eventType => {
            const event = new Event(eventType, { bubbles: true });
            element.dispatchEvent(event);
        });

        // Pequena pausa aleatória
        await sleep(CONFIG.TYPE_DELAY_MS + Math.random() * 20);
    }
    
    // Evento final de blur
    element.dispatchEvent(new Event('blur', { bubbles: true }));
    await sleep(500);
}

/**
 * Espera até que uma condição seja verdadeira.
 */
async function waitFor(conditionFn, timeout = 30000, description = "condição") {
    const startTime = Date.now();
    while (Date.now() - startTime < timeout) {
        if (conditionFn()) return true;
        await sleep(CONFIG.POLL_INTERVAL);
    }
    log(`Timeout esperando por: ${description}`, "red");
    return false;
}

/**
 * Tenta encontrar um elemento visível usando múltiplos seletores (separados por vírgula).
 */
function findElement(selectorString) {
    const selectors = selectorString.split(",").map(s => s.trim());
    for (const sel of selectors) {
        const el = document.querySelector(sel);
        // Verifica se existe e está visível (básico)
        if (el && el.offsetParent !== null) return el; 
    }
    return null;
}

/**
 * Função para baixar um arquivo a partir de uma URL (se não acharmos botão de download).
 */
/**
 * Função para baixar um arquivo a partir de uma URL (Fetch + Blob)
 * Isso evita que o navegador abra a imagem em nova aba por proteção Cross-Origin.
 */
async function forceDownload(url, filename) {
    try {
        log(`Iniciando download via Fetch: ${filename}...`, "cyan");
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Network response was not ok: ${response.statusText}`);
        
        const blob = await response.blob();
        const blobUrl = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = blobUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        // Limpa a URL do blob para economizar memória
        setTimeout(() => URL.revokeObjectURL(blobUrl), 100);
        log(`Download concluído com sucesso: ${filename}`, "green");
    } catch (error) {
        log(`ERRO no download via Fetch: ${error.message}. Tentando método fallback (link direto)...`, "orange");
        
        // Fallback: Tenta método antigo se o fetch falhar (ex: CORS bloqueou)
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.target = "_blank"; // Se falhar download, pelo menos abre pra salvar manual
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
}

// =================================================================================
// 3. LÓGICA PRINCIPAL
// =================================================================================

/**
 * Conta quantas imagens "candidatas" (grandes) existem na página.
 * Usado para detectar quando uma nova imagem foi gerada.
 */
function countCandidateImages() {
    const images = document.querySelectorAll("img");
    // Filtra imagens pequenas (ícones, avatares)
    return Array.from(images).filter(img => img.width > 300 && img.height > 300).length;
}

async function processTask(task, index) {
    log(`--- Processando ${index + 1}/${TASKS.length}: ${task.expected_filename} ---`, "yellow");

    // 1. Encontrar Input e preparar
    const inputBox = findElement(SELECTORS.INPUT_BOX);
    if (!inputBox) {
        log("ERRO: Caixa de texto não encontrada.", "red");
        return;
    }

    const initialImageCount = countCandidateImages();
    log(`Imagens iniciais: ${initialImageCount}`, "gray");

    // 2. Digitar e Enviar
    log("Digitando prompt...");
    await simulateTyping(inputBox, `${task.prompt} --ar 9:16`);

    const sendButton = findElement(SELECTORS.SEND_BUTTON);
    if (sendButton) {
        sendButton.click();
    } else {
        log("Botão enviar não achado, tentando Enter...", "orange");
        inputBox.dispatchEvent(new KeyboardEvent('keydown', { bubbles: true, keyCode: 13 }));
    }

    // 3. Aguardar Geração
    log("Aguardando nova imagem...");
    const success = await waitFor(() => countCandidateImages() > initialImageCount, CONFIG.MAX_WAIT_TIME, "Nova imagem aparecer");

    if (!success) {
        log("TIMEOUT: Nenhuma imagem nova.", "red");
        return;
    }

    // Pausa para processamento do Gemini
    await sleep(3000);

    // 4. Encontrar a imagem e baixar (NATIVO - Full Resolution)
    const images = document.querySelectorAll("img");
    const candidates = Array.from(images).filter(img => img.width > 300 && img.height > 300);
    
    if (candidates.length > 0) {
        const lastImage = candidates[candidates.length - 1];
        lastImage.scrollIntoView({block: "center"});
        await sleep(500);

        // SIMULA HOVER NA IMAGEM (Para o botão de download aparecer)
        log("Simulando mouse over para revelar botão de download...", "cyan");
        const mouseEvents = ['mouseenter', 'mouseover', 'mousemove'];
        for (let eventType of mouseEvents) {
            lastImage.dispatchEvent(new MouseEvent(eventType, { bubbles: true, cancelable: true, view: window }));
            await sleep(50);
        }
        
        // Tenta achar o botão de download
        let downloadBtn = null;
        
        // Estratégia: O botão geralmente é o último "download" button adicionado ao DOM
        const allDownloadBtns = document.querySelectorAll(SELECTORS.DOWNLOAD_BUTTON);
        if (allDownloadBtns.length > 0) {
             downloadBtn = allDownloadBtns[allDownloadBtns.length - 1];
        }

        if (downloadBtn) {
            log("Botão de download nativo encontrado! Clicando...", "green");
            downloadBtn.click();
            // Dá tempo para o download iniciar
            await sleep(2000); 
        } else {
            log("ERRO CRÍTICO: Botão de download nativo NÃO encontrado após hover.", "red");
            log("O script não baixará a imagem para evitar baixa resolução.", "orange");
        }

    } else {
        log("ERRO: Contagem aumentou, mas imagem não encontrada.", "red");
    }

    await sleep(CONFIG.DOWNLOAD_WAIT);
}

async function startAutomation() {
    if (TASKS.length === 0) {
        log("ALERTA: A lista de TASKS está vazia! Cole seu JSON no script.", "red");
        return;
    }

    log("Iniciando automação...", "green");
    
    for (let i = 0; i < TASKS.length; i++) {
        await processTask(TASKS[i], i);
    }

    log("=== FIM DA EXECUÇÃO ===", "green");
    alert("Automação concluída!");
}

// Expõe a função para ser chamada no console
window.startAutomation = startAutomation;
log("Script carregado! Cole suas tarefas em 'TASKS' e rode 'startAutomation()', ou edite o script antes.", "magenta");
