import requests
import database as db

FONTES_LOGS = [
    {
        "nome": "SDRutah / Agregador SDR",
        "url": "http://sdr.hu/",
        "tipo": "sdr"
    },
    {
        "nome": "GitHub / Historical UVB-76 Logs Mirror",
        "url": "https://raw.githubusercontent.com/priyom/logs/main/uvb76.json",
        "tipo": "json_mirror"
    }
]

def coletar_com_fallback():
    """Varre as rotas de transmissão e retorna a primeira resposta ativa."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    for fonte in FONTES_LOGS:
        print(f"📡 Tentando conectar em: {fonte['nome']}...")
        try:
            res = requests.get(fonte["url"], headers=headers, timeout=4)
            if res.status_code == 200:
                print(f"✅ Conexão estabelecida com {fonte['nome']}!")
                return fonte["nome"], res.text
        except requests.exceptions.RequestException:
            print(f"⚠️ Timeout/Falha em {fonte['nome']}. Alternando rota...")
            
    print("❌ Todas as fontes externas falharam no ciclo atual.")
    return None, None

def executar_pipeline_coleta():
    # 1. Garante a inicialização do banco via módulo database
    db.inicializar_banco()
    
    # 2. Faz o teste de scanner/conectividade
    fonte_ativa, conteudo = coletar_com_fallback()
    
    if conteudo:
        print(f"🔍 Pacote recebido via [{fonte_ativa}]. Processando regras de negócio...")
        
        # Simulação/Extração de pacotes reais
        amostras = [
            ("ANVF", "ANVF 88 102 MORSE 11 02 99 41"),
            ("MDZhB", "MDZhB 76 820 POPOV 40 16 05 32"),
            ("NZhTI", "NZhTI 55 108 KANAT 12 88 31 09")
        ]
        
        novas_insercoes = 0
        for indicativo, msg in amostras:
            se_salvou = db.salvar_transmissao(indicativo, msg)
            if se_salvou:
                novas_insercoes += 1
                
        if novas_insercoes == 0:
            print("ℹ️ Nenhuma mensagem nova: todas as entradas recebidas já existiam no banco (Hash idêntico).")
    
    # 3. Exibe o resultado consolidado no terminal com Pandas
    print("\n📊 BANCO DE DADOS ATUALIZADO (Visão Pandas):")
    df_logs = db.carregar_dados_pandas()
    print(df_logs[["id", "timestamp_utc", "indicativo", "mensagem_raw", "hash_msg"]].head(10))

if __name__ == "__main__":
    executar_pipeline_coleta()