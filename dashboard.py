import streamlit as st
import pandas as pd
import database as db

# Configuração da página do Streamlit
st.set_page_config(
    page_title="UVB-76 Signal & Traffic Analyzer",
    page_icon="📡",
    layout="wide"
)

st.title("📡 UVB-76 Signal & Traffic Analyzer")
st.markdown("---")

# Carrega os dados do banco SQLite através do módulo database
df = db.carregar_dados_pandas()

if df.empty:
    st.warning("⚠️ Nenhum registro encontrado no banco de dados SQLite.")
else:
    # 1. Métricas Principais (KPIs)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Total de Mensagens Capturadas", value=len(df))
    with col2:
        indicativo_mais_comum = df["indicativo"].mode()[0] if not df.empty else "N/A"
        st.metric(label="Indicativo Predominante", value=indicativo_mais_comum)
    with col3:
        st.metric(label="Média de Palavras/Pacote", value=f"{df['num_palavras'].mean():.1f}")

    st.markdown("---")

    # 2. Gráficos de Análise de Tráfego
    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        st.subheader("📊 Frequência por Indicativo")
        contagem_indicativos = df["indicativo"].value_counts()
        st.bar_chart(contagem_indicativos)

    with col_graf2:
        st.subheader("🔤 Palavras de Código Mais Frequentes")
        todas_palavras = " ".join(df["mensagem_raw"]).split()
        palavras_chave = [
            p for p in todas_palavras 
            if p.isalpha() and len(p) > 3 and p not in df["indicativo"].values
        ]
        if palavras_chave:
            df_palavras = pd.Series(palavras_chave).value_counts()
            st.bar_chart(df_palavras)
        else:
            st.write("Sem palavras-chave suficientes para análise.")

    st.markdown("---")

    # 3. Tabela de Registros do Banco
    st.subheader("📋 Registros do Banco de Dados (SQLite)")
    st.dataframe(df[["id", "timestamp_utc", "indicativo", "mensagem_raw", "hash_msg"]], width="stretch")