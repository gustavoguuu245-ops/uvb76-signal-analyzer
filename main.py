import requests
import re
from bs4 import BeautifulSoup
import database as db

# Fontes
FONTES_LOGS = [
    {
        "nome": "Priyom.org (Oficial Logs)",
        "url": "https://priyom.org/number-stations/russia/the-buzzer",
        "tipo": "html"
    },
    {
        "nome": "SDRutah Agregador / Mirror",
        "url": "http://sdr.hu/",
        "tipo": "html"
    },
    {
        "nome": "Histórico Real UVB-76 (Mirror JSON)",
        "url": "https://raw.githubusercontent.com/priyom/logs/main/uvb76.json",
        "tipo": "json"
    }
]

# RegEx para capturar a estrutura real da mensagem transmitida:
# [INDICATIVO] [2 DIGITOS] [3 DIGITOS] [PALAVRA] [PAR1] [PAR2] [PAR3] [CHECKSUM]
REGEX_UVB = re.compile(r'([A-Z0-9]{4,5})\s+(\d{2})\s+(\d{3})\s+([A-ZА-Я]+)\s+(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})', re.IGNORECASE)

def extrair_mensagens_reais(html_conteudo):
    """Varre a estrutura de texto/HTML recebida e extrai mensagens reais dinamicamente."""
    soup = BeautifulSoup(html_conteudo, "html.parser")
    mensagens_encontradas = []
    
    # Extrai todo o texto da página limpo
    texto_pagina = soup.get_text()
    
    # Procura por todas as ocorrências que casam com o padrão real
    for match in REGEX_UVB.finditer(texto_pagina):
        mensagem_completa = match.group(0).strip()
        indicativo = match.group(1).upper()
        mensagens_encontradas.append((indicativo, mensagem_completa))
        
    return mensagens_encontradas

def coletar_com_fallback():
    """Conecta nas fontes web dinâmicas e extrai tráfego real."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    for fonte in FONTES_LOGS:
        print(f"📡 Conectando ao vivo em: {fonte['nome']}...")
        try:
            res = requests.get(fonte["url"], headers=headers, timeout=6)
            if res.status_code == 200:
                print(f"✅ Conexão estabelecida com sucesso!")
                mensagens = extrair_mensagens_reais(res.text)
                if mensagens:
                    return fonte["nome"], mensagens
                else:
                    print(f"ℹ️ Conectou, mas não encontrou mensagens no formato padrão nesta rota.")
        except requests.exceptions.RequestException:
            print(f"⚠️ Timeout/Falha na rota {fonte['nome']}. Tentando próxima fonte...")
            
    print("❌ Nenhuma nova transmissão capturada nas fontes atuais.")
    return None, []

def executar_pipeline_coleta():
    db.inicializar_banco()
    
    fonte_ativa, mensagens_reais = coletar_com_fallback()
    
    if mensagens_reais:
        print(f"\n🔍 {len(mensagens_reais)} pacotes reais extraídos via [{fonte_ativa}]. Processando Ingestão...")
        novas_insercoes = 0
        
        for indicativo, msg_raw in mensagens_reais:
            se_salvou = db.salvar_transmissao(indicativo, msg_raw)
            if se_salvou:
                novas_insercoes += 1
                
        if novas_insercoes == 0:
            print("ℹ️ Todas as mensagens reais capturadas nesta execução já existem no banco (bloqueadas pelo Hash SHA-256).")
        else:
            print(f"🎉 Sucesso: {novas_insercoes} novas transmissões reais salvas no SQLite!")
    else:
        print("ℹ️ Aguardando novo tráfego de rede para ingestão.")

    print("\n📊 VISÃO ATUALIZADA DO BANCO DE DADOS (SQLite):")
    df_logs = db.carregar_dados_pandas()
    if not df_logs.empty:
        print(df_logs[["id", "timestamp_utc", "indicativo", "mensagem_raw", "hash_msg"]].head(10))
    else:
        print("Banco de dados vazio.")

if __name__ == "__main__":
    executar_pipeline_coleta()