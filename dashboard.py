import streamlit as st
import pandas as pd
import re
import database as db

# Configuração da página
st.set_page_config(
    page_title="UVB-76 Signal & Traffic Analyzer",
    page_icon="📡",
    layout="wide"
)

# Expressão Regular do Padrão Monolith
PADRAO_MONOLITH = re.compile(r'^([A-Za-z0-9]{4,5})\s+(\d{2})\s+(\d{3})\s+([A-Za-z]+)\s+(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})$')

st.title("📡 UVB-76 Signal & Traffic Analyzer")
st.markdown("---")

df = db.carregar_dados_pandas()

if df.empty:
    st.warning("⚠️ Nenhum registro encontrado no banco de dados SQLite.")
else:
    # 1. Métricas Principais (KPIs)
    col1, col2, col3, col4 = st.columns(4)
    
    # Aplica o parser no DataFrame para calcular a conformidade
    mensagens_conformes = df['mensagem_raw'].apply(lambda x: bool(PADRAO_MONOLITH.match(x.strip()))).sum()
    taxa_conformidade = (mensagens_conformes / len(df)) * 100
    
    with col1:
        st.metric(label="Total de Mensagens", value=len(df))
    with col2:
        indicativo_mais_comum = df["indicativo"].mode()[0] if not df.empty else "N/A"
        st.metric(label="Indicativo Dominante", value=indicativo_mais_comum)
    with col3:
        st.metric(label="Média Palavras/Pacote", value=f"{df['num_palavras'].mean():.1f}")
    with col4:
        st.metric(label="Conformidade Monolith", value=f"{taxa_conformidade:.0f}%")

    st.markdown("---")

    # 2. Gráficos de Análise de Tráfego
    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        st.subheader("📊 Frequência por Indicativo")
        st.bar_chart(df["indicativo"].value_counts())

    with col_graf2:
        st.subheader("🔤 Codewords Detectadas")
        todas_palavras = " ".join(df["mensagem_raw"]).split()
        palavras_chave = [
            p for p in todas_palavras 
            if p.isalpha() and len(p) > 3 and p not in df["indicativo"].values
        ]
        if palavras_chave:
            st.bar_chart(pd.Series(palavras_chave).value_counts())
        else:
            st.write("Sem palavras-chave suficientes.")

    st.markdown("---")

    # 3. Tabela com Decodificação do Padrão Monolith
    st.subheader("🔬 Inspeção Sintática de Pacotes (Monolith Parser)")
    
    # Processa os detalhes de cada registro para exibição
    detalhes_sintaxe = []
    for _, row in df.iterrows():
        match = PADRAO_MONOLITH.match(row['mensagem_raw'].strip())
        if match:
            ind, c1, c2, word, p1, p2, p3, chk = match.groups()
            detalhes_sintaxe.append({
                "ID": row['id'],
                "Timestamp UTC": row['timestamp_utc'],
                "Mensagem Raw": row['mensagem_raw'],
                "Status": "✅ Monolith Válido",
                "Codeword": word,
                "Blocos de Ação": f"{p1} {p2} {p3}",
                "Checksum": chk
            })
        else:
            detalhes_sintaxe.append({
                "ID": row['id'],
                "Timestamp UTC": row['timestamp_utc'],
                "Mensagem Raw": row['mensagem_raw'],
                "Status": "⚠️ Fora do Padrão",
                "Codeword": "N/A",
                "Blocos de Ação": "N/A",
                "Checksum": "N/A"
            })
            
    st.dataframe(pd.DataFrame(detalhes_sintaxe), width="stretch")