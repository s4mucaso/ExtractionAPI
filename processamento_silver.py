import os
import json
import csv
from datetime import datetime
import glob

# 1. Definir caminhos das pastas do Data Lake
PASTA_BRONZE = "./datalake/bronze/"
PASTA_SILVER = "./datalake/silver/"

# Garantir que a pasta Silver existe
os.makedirs(PASTA_SILVER, exist_ok=True)

def extrair_data_arquivo(nome_arquivo):
    """Extrai a data e hora do nome do arquivo bronze (ex: dados_cep_20260702_142537.json)"""
    try:
        # Pega a parte '20260702_142537'
        partes = os.path.basename(nome_arquivo).replace(".json", "").split("_")
        data_str = f"{partes[2]}_{partes[3]}"
        return datetime.strptime(data_str, "%Y%m%d_%H%M%S")
    except Exception:
        # Se falhar, retorna uma data antiga
        return datetime.min

def limpar_e_padronizar(dados, arquivo_origem, data_extracao):
    """Limpa e padroniza os campos do CEP"""
    # 1. Limpeza do CEP (remover hífen e espaços)
    cep_limpo = dados.get("cep", "").replace("-", "").strip()
    
    # 2. Padronização de campos nulos/vazios (converter "" para None)
    dados_limpos = {}
    for chave, valor in dados.items():
        if isinstance(valor, str):
            valor_limpo = valor.strip()
            dados_limpos[chave] = valor_limpo if valor_limpo != "" else None
        else:
            dados_limpos[chave] = valor

    # Atualiza com o CEP limpo
    dados_limpos["cep"] = cep_limpo
    
    # 3. Adicionar metadados da engenharia de dados (linhagem do dado)
    dados_limpos["metadata_arquivo_origem"] = os.path.basename(arquivo_origem)
    dados_limpos["metadata_data_extracao"] = data_extracao.strftime("%Y-%m-%d %H:%M:%S")
    dados_limpos["metadata_data_processamento"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return dados_limpos

def processar_camada_silver():
    print("Iniciando processamento da Camada Silver...")
    
    # Procurar todos os arquivos JSON na pasta Bronze
    arquivos_bronze = glob.glob(os.path.join(PASTA_BRONZE, "dados_cep_*.json"))
    
    if not arquivos_bronze:
        print("Nenhum arquivo encontrado na camada Bronze para processar.")
        return
        
    print(f"Encontrados {len(arquivos_bronze)} arquivos na camada Bronze.")
    
    # Dicionário para guardar o CEP mais recente (Deduplicação)
    # Chave: CEP, Valor: (dados_processados, data_extracao)
    ceps_unicos = {}
    
    for caminho_arquivo in arquivos_bronze:
        try:
            data_extracao = extrair_data_arquivo(caminho_arquivo)
            
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                dados_brutos = json.load(f)
            
            # Se a resposta do ViaCEP veio com erro (ex: {"erro": "true"}), ignoramos
            if dados_brutos.get("erro") == "true" or dados_brutos.get("erro") is True:
                print(f"Ignorando arquivo {os.path.basename(caminho_arquivo)} pois contém dados de CEP inválido/erro.")
                continue
                
            dados_processados = limpar_e_padronizar(dados_brutos, caminho_arquivo, data_extracao)
            cep = dados_processados["cep"]
            
            # Se o CEP já foi visto, mantemos apenas o mais recente
            if cep in ceps_unicos:
                _, data_anterior = ceps_unicos[cep]
                if data_extracao > data_anterior:
                    ceps_unicos[cep] = (dados_processados, data_extracao)
            else:
                ceps_unicos[cep] = (dados_processados, data_extracao)
                
        except Exception as e:
            print(f"Erro ao processar o arquivo {caminho_arquivo}: {e}")
            
    # Salvar os dados processados na camada Silver
    total_salvos = 0
    lista_consolidada = []
    
    for cep, (dados_limpos, _) in ceps_unicos.items():
        # Salvar arquivo JSON individual por CEP na camada Silver
        nome_arquivo_silver = f"cep_{cep}.json"
        caminho_silver = os.path.join(PASTA_SILVER, nome_arquivo_silver)
        
        with open(caminho_silver, "w", encoding="utf-8") as f:
            json.dump(dados_limpos, f, ensure_ascii=False, indent=4)
            
        lista_consolidada.append(dados_limpos)
        total_salvos += 1
        print(f"CEP {cep} processado e salvo em: {caminho_silver}")

    # Criar arquivo CSV consolidado para fácil análise/leitura
    if lista_consolidada:
        caminho_csv = os.path.join(PASTA_SILVER, "consolidado_ceps.csv")
        # Obter cabeçalhos das chaves do dicionário
        cabecalhos = lista_consolidada[0].keys()
        
        with open(caminho_csv, "w", encoding="utf-8", newline="") as f:
            escritor = csv.DictWriter(f, fieldnames=cabecalhos)
            escritor.writeheader()
            escritor.writerows(lista_consolidada)
            
        print(f"Arquivo CSV consolidado gerado com sucesso em: {caminho_csv}")
        
    print(f"Processamento concluído. {total_salvos} CEP(s) únicos salvos na camada Silver.")

if __name__ == "__main__":
    processar_camada_silver()
