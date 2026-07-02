import requests
import json
import os
from datetime import datetime

# 1. Definimos quem vamos atacar (A URL da API Pública do ViaCEP)
# No mundo real, aqui estaria a URL: http://api.seap.rj.gov.br/presos
url_api = "https://viacep.com.br/ws/01001000/json/"

# 2. Criamos a pasta 'Bronze' no seu computador (Simulando o Data Lake)
pasta_bronze = "./datalake/bronze/"
os.makedirs(pasta_bronze, exist_ok=True) # Cria a pasta se ela não existir

print("Iniciando extração da API...")

# 3. O nosso Garçom (O verbo GET) batendo na porta da API
resposta = requests.get(url_api)

# 4. Verificamos se deu certo (Status 200 = Sucesso na internet)
if resposta.status_code == 200:
    # Transformamos o texto que voltou da internet num dicionário Python (JSON)
    dados_extraidos = resposta.json()
    
    # 5. Criamos um nome de arquivo com a data e hora de agora
    # Engenheiro de dados sempre "carimba" a hora da extração para não sobrepor arquivos
    data_extracao = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"dados_cep_{data_extracao}.json"
    caminho_completo = os.path.join(pasta_bronze, nome_arquivo)
    
    # 6. Salvamos o arquivo bruto no nosso Data Lake local (Camada Bronze)
    with open(caminho_completo, "w", encoding="utf-8") as arquivo:
        json.dump(dados_extraidos, arquivo, ensure_ascii=False, indent=4)
            
    print(f"SUCESSO! Arquivo bruto salvo em: {caminho_completo}")

else:
    # Se a API cair ou negar acesso, o script grita.
    print(f"ERRO! A API retornou o status: {resposta.status_code}")
