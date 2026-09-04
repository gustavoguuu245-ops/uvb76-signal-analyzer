import sqlite3
import hashlib
from datetime import datetime, timezone
import pandas as pd

DB_NAME = "uvb76_data.db"

def conectar():
    """Retorna uma conexão ativa com o banco SQLite."""
    return sqlite3.connect(DB_NAME)

def inicializar_banco():
    """Cria a tabela com validação de Hash SHA-256 único para evitar duplicatas."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transmissoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp_utc TEXT NOT NULL,
            frequencia_khz REAL DEFAULT 4625.0,
            indicativo TEXT NOT NULL,
            mensagem_raw TEXT NOT NULL,
            hash_msg TEXT UNIQUE NOT NULL,
            num_palavras INTEGER,
            processado_em TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Banco de dados 'uvb76_data.db' inicializado com suporte a Hash SHA-256!")

def gerar_hash_mensagem(mensagem_raw):
    """Gera uma assinatura SHA-256 do texto limpo da mensagem."""
    return hashlib.sha256(mensagem_raw.strip().encode('utf-8')).hexdigest()

def salvar_transmissao(indicativo, mensagem_raw, frequencia=4625.0):
    """Insere a transmissão no banco e ignora duplicatas reais via Hash SHA-256."""
    timestamp_atual = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    num_palavras = len(mensagem_raw.split())
    processado_em = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    hash_msg = gerar_hash_mensagem(mensagem_raw)
    
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO transmissoes (timestamp_utc, frequencia_khz, indicativo, mensagem_raw, hash_msg, num_palavras, processado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp_atual, frequencia, indicativo, mensagem_raw, hash_msg, num_palavras, processado_em))
        conn.commit()
        print(f"💾 NOVA TRANSMISSÃO SALVA: [{indicativo}] - {mensagem_raw[:35]}...")
        return True
    except sqlite3.IntegrityError:
        # Mensagem com mesmo hash já existe no banco
        return False
    finally:
        conn.close()

def carregar_dados_pandas():
    """Lê todos os registros do SQLite e retorna um DataFrame Pandas."""
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM transmissoes ORDER BY id DESC", conn)
    conn.close()
    return df