import os
import json
import csv
from datetime import datetime

# 1. Definir caminhos das pastas do Data Lake
PASTA_SILVER = "./datalake/silver/"
PASTA_GOLD = "./datalake/gold/"

# Garantir que a pasta Gold existe
os.makedirs(PASTA_GOLD, exist_ok=True)

def calcular_distribuicao(dados, chave):
    """Calcula a distribuição (contagem) de uma determinada chave nos dados"""
    distribuicao = {}
    for item in dados:
        valor = item.get(chave)
        if valor:
            distribuicao[valor] = distribuicao.get(valor, 0) + 1
        else:
            distribuicao["Não Informado"] = distribuicao.get("Não Informado", 0) + 1
    
    # Ordenar por contagem decrescente
    return dict(sorted(distribuicao.items(), key=lambda x: x[1], reverse=True))

def processar_camada_gold():
    print("Iniciando processamento da Camada Gold...")
    
    caminho_csv_silver = os.path.join(PASTA_SILVER, "consolidado_ceps.csv")
    
    if not os.path.exists(caminho_csv_silver):
        print(f"Erro: Arquivo consolidado da camada Silver não encontrado em: {caminho_csv_silver}")
        print("Certifique-se de executar o script 'processamento_silver.py' primeiro.")
        return
        
    # Ler os dados consolidados da Silver
    dados_silver = []
    with open(caminho_csv_silver, "r", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            dados_silver.append(linha)
            
    if not dados_silver:
        print("Nenhum dado encontrado no arquivo consolidado da camada Silver.")
        return
        
    total_ceps = len(dados_silver)
    print(f"Processando métricas sobre {total_ceps} CEP(s) cadastrados.")
    
    # 2. Calcular agregados de negócio
    dist_regiao = calcular_distribuicao(dados_silver, "regiao")
    dist_uf = calcular_distribuicao(dados_silver, "uf")
    dist_cidade = calcular_distribuicao(dados_silver, "localidade")
    dist_ddd = calcular_distribuicao(dados_silver, "ddd")
    
    # 3. Montar o relatório consolidado de métricas (Gold standard)
    relatorio_gold = {
        "metadata": {
            "data_geracao_relatorio": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fonte_dados": "datalake/silver/consolidado_ceps.csv",
            "total_registros_analisados": total_ceps
        },
        "metricas": {
            "distribuicao_por_regiao": dist_regiao,
            "distribuicao_por_estado": dist_uf,
            "distribuicao_por_cidade": dist_cidade,
            "distribuicao_por_ddd": dist_ddd
        }
    }
    
    # 4. Salvar arquivos de saída na camada Gold
    # Salvar relatório consolidado completo
    caminho_relatorio = os.path.join(PASTA_GOLD, "relatorio_metricas.json")
    with open(caminho_relatorio, "w", encoding="utf-8") as f:
        json.dump(relatorio_gold, f, ensure_ascii=False, indent=4)
    print(f"Relatório completo salvo em: {caminho_relatorio}")
    
    # Salvar métricas separadas em arquivos específicos para consumo rápido de APIs ou dashboards
    arquivos_metricas = {
        "distribuicao_regiao.json": dist_regiao,
        "distribuicao_uf.json": dist_uf,
        "distribuicao_cidade.json": dist_cidade,
        "distribuicao_ddd.json": dist_ddd
    }
    
    for nome_arquivo, dados_metrica in arquivos_metricas.items():
        caminho_arquivo = os.path.join(PASTA_GOLD, nome_arquivo)
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(dados_metrica, f, ensure_ascii=False, indent=4)
        print(f"Métrica salva em: {caminho_arquivo}")
        
    print("\n--- RESUMO DOS DADOS (GOLD) ---")
    print(f"Total de CEPs Processados: {total_ceps}")
    print("\nDistribuição por Região:")
    for reg, qtd in dist_regiao.items():
        print(f" - {reg}: {qtd} ({qtd/total_ceps*100:.1f}%)")
    print("\nDistribuição por Estado:")
    for uf, qtd in dist_uf.items():
        print(f" - {uf}: {qtd} ({qtd/total_ceps*100:.1f}%)")
    print("--------------------------------\n")
    print("Processamento da Camada Gold finalizado com sucesso!")

if __name__ == "__main__":
    processar_camada_gold()
