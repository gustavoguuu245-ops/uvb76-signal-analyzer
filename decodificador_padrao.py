import re
import pandas as pd
import database as db

# RegEx do Padrão Monolith da UVB-76
# Estrutura: [INDICATIVO] [2 DIGITOS] [3 DIGITOS] [PALAVRA] [2 DIGITOS] [2 DIGITOS] [2 DIGITOS] [2 DIGITOS]
PADRAO_MONOLITH = re.compile(r'^([A-Za-z0-9]{4,5})\s+(\d{2})\s+(\d{3})\s+([A-Za-z]+)\s+(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})$')

def analisar_padroes_sintaticos():
    print("🔬 === ANALISADOR DE PADRÃO E SINTAXE RUSSA (MONOLITH) ===")
    df = db.carregar_dados_pandas()
    
    if df.empty:
        print("⚠️ Sem dados para analisar.")
        return

    registros_validos = 0
    
    for idx, row in df.iterrows():
        msg = row['mensagem_raw']
        match = PADRAO_MONOLITH.match(msg.strip())
        
        print(f"\n📡 Registro ID {row['id']}: '{msg}'")
        if match:
            registros_validos += 1
            indicativo, cod_ctrl1, cod_ctrl2, codeword, par1, par2, par3, checksum = match.groups()
            print(f"  ✅ PARECER: Segue o padrão Monolith perfeito!")
            print(f"     • Indicativo: {indicativo}")
            print(f"     • Código de Entrada: {cod_ctrl1}-{cod_ctrl2}")
            print(f"     • Codeword (Instrução): {codeword}")
            print(f"     • Blocos de Ação: {par1} {par2} {par3}")
            print(f"     • Checksum de Validação: {checksum}")
        else:
            print("  ⚠️ PARECER: Mensagem fora do padrão tradicional (Anomalia/Voz livre).")
            
    print("\n" + "="*50)
    print(f"📊 RESULTADO DA ANÁLISE: {registros_validos}/{len(df)} mensagens seguem o padrão sintático rigoroso.")

if __name__ == "__main__":
    analisar_padroes_sintaticos()