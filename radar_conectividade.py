import requests
import time

# Lista de portas e rotas alternativas para testar conectividade
ALVOS_TESTE = [
    {"nome": "Priyom HTTPS Padrão", "url": "https://priyom.org/number-stations/russia/the-buzzer", "porta": 443},
    {"nome": "Priyom HTTP Alternativo", "url": "http://priyom.org/number-stations/russia/the-buzzer", "porta": 80},
    {"nome": "WebSDR Twente (Holanda)", "url": "http://websdr.ewi.utwente.nl:8901/", "porta": 8901},
    {"nome": "SDRutah (Servidor SDR)", "url": "http://sdr.hu/", "porta": 80},
]

HEADERS_DISFARCE = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

def disparar_radar():
    print("📡 === RADAR DE SCANNER DE CONECTIVIDADE E PORTAS ===")
    print("🎯 Testando rotas de comunicação para identificar portas abertas e tempos de resposta...\n")

    for alvo in ALVOS_TESTE:
        nome = alvo["nome"]
        url = alvo["url"]
        porta = alvo["porta"]
        
        print(f"🔍 Disparando contra: {nome} | Porta: {porta}")
        inicio = time.time()
        
        try:
            # Teste com timeout de 5 segundos e redirecionamento permitido
            resposta = requests.get(url, headers=HEADERS_DISFARCE, timeout=5, allow_redirects=True)
            tempo_resposta = round((time.time() - inicio) * 1000, 2)
            
            if resposta.status_code == 200:
                print(f"✅ SUCESSO! Porta {porta} aberta | Status: 200 OK | Latência: {tempo_resposta} ms")
                print(f"   --> Conteúdo recebido: {len(resposta.content)} bytes\n")
            else:
                print(f"⚠️ RESPONDEU COM ALERTA | Status: {resposta.status_code} | Latência: {tempo_resposta} ms\n")
                
        except requests.exceptions.Timeout:
            print(f"❌ TIMEOUT na porta {porta}! O servidor não respondeu em 5 segundos.\n")
        except requests.exceptions.ConnectionError as e:
            print(f"❌ BLOQUEIO/RECUSA DE CONEXÃO na porta {porta}.\n")
        except Exception as e:
            print(f"❌ ERRO INESPERADO: {e}\n")

if __name__ == "__main__":
    disparar_radar()