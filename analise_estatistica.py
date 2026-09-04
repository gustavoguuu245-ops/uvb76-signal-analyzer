import sqlite3
import pandas as pd

DB_NAME = "uvb76_data.db"

def analisar_banco_uvb76():
    print("📊 === PAINEL DE ANÁLISE E METADADOS - UVB-76 ===")
    
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM transmissoes", conn)
    conn.close()
    
    if df.empty:
        print("⚠️ Nenhum dado encontrado no banco para análise.")
        return

    print(f"📈 Total de registros acumulados no banco: {len(df)}")
    print("-" * 50)
    
    # 1. Distribuição de Indicativos
    print("\n1. FREQUÊNCIA DE INDICATIVOS DA ESTAÇÃO:")
    distribuicao_indicativos = df["indicativo"].value_counts()
    print(distribuicao_indicativos)
    
    # 2. Extração de Palavras de Código (Codewords)
    print("\n2. PALAVRAS DE CÓDIGO MAIS FREQUENTES:")
    # Extrai palavras com mais de 3 letras alfabéticas das mensagens
    todas_palavras = " ".join(df["mensagem_raw"]).split()
    palavras_chave = [p for p in todas_palavras if p.isalpha() and len(p) > 3 and p not in df["indicativo"].values]
    
    df_palavras = pd.Series(palavras_chave).value_counts()
    print(df_palavras)
    
    # 3. Métricas de Tamanho de Mensagem
    print("\n3. MÉTRICAS DE ESTRUTURA:")
    print(f"Média de palavras por mensagem: {df['num_palavras'].mean():.2f}")
    print("-" * 50)

if __name__ == "__main__":
    analisar_banco_uvb76()