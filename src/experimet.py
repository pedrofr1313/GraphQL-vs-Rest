"""
Experimento Controlado: Comparação de Desempenho entre REST e GraphQL
Disciplina: Laboratório de Experimentação de Software
Curso: Engenharia de Software

Este script realiza a coleta automatizada de dados para comparar o desempenho
de APIs REST e GraphQL usando a Rick and Morty API.

Uso:
    python experiment.py --start 1 --end 50 --out experiment_results.csv
"""

import requests
import time
import pandas as pd
import argparse
import random
from typing import Tuple, Optional

# Configurações globais
REST_BASE_URL = "https://rickandmortyapi.com/api/character"
GRAPHQL_URL = "https://rickandmortyapi.com/graphql"

# Query GraphQL solicitando apenas 3 campos específicos
GRAPHQL_QUERY_TEMPLATE = """
query {{
  character(id: {id}) {{
    name
    species
    status
  }}
}}
"""


def make_rest_request(character_id: int) -> Tuple[Optional[float], Optional[int], bool]:
    """
    Realiza requisição REST para obter dados de um personagem.
    
    Args:
        character_id: ID do personagem a ser consultado
        
    Returns:
        Tupla (tempo_ms, tamanho_bytes, sucesso)
        - tempo_ms: Tempo de resposta em milissegundos
        - tamanho_bytes: Tamanho da resposta em bytes
        - sucesso: True se a requisição foi bem-sucedida
    """
    url = f"{REST_BASE_URL}/{character_id}"
    
    try:
        # Medição do tempo
        start_time = time.time()
        response = requests.get(url, timeout=10)
        end_time = time.time()
        
        # Verificar se a requisição foi bem-sucedida
        response.raise_for_status()
        
        # Calcular métricas
        time_ms = (end_time - start_time) * 1000  # Converter para ms
        size_bytes = len(response.content)
        
        return time_ms, size_bytes, True
        
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  Erro na requisição REST (ID {character_id}): {e}")
        return None, None, False


def make_graphql_request(character_id: int) -> Tuple[Optional[float], Optional[int], bool]:
    """
    Realiza requisição GraphQL para obter dados específicos de um personagem.
    
    Args:
        character_id: ID do personagem a ser consultado
        
    Returns:
        Tupla (tempo_ms, tamanho_bytes, sucesso)
        - tempo_ms: Tempo de resposta em milissegundos
        - tamanho_bytes: Tamanho da resposta em bytes
        - sucesso: True se a requisição foi bem-sucedida
    """
    query = GRAPHQL_QUERY_TEMPLATE.format(id=character_id)
    payload = {"query": query}
    
    try:
        # Medição do tempo
        start_time = time.time()
        response = requests.post(GRAPHQL_URL, json=payload, timeout=10)
        end_time = time.time()
        
        # Verificar se a requisição foi bem-sucedida
        response.raise_for_status()
        
        # Calcular métricas
        time_ms = (end_time - start_time) * 1000  # Converter para ms
        size_bytes = len(response.content)
        
        return time_ms, size_bytes, True
        
    except requests.exceptions.RequestException as e:
        print(f"  ⚠️  Erro na requisição GraphQL (ID {character_id}): {e}")
        return None, None, False


def warmup():
    """
    Realiza fase de warm-up para estabilizar conexões TCP/TLS e cache de DNS.
    
    Executa 10 requisições (5 REST + 5 GraphQL) com IDs aleatórios fora da
    amostra experimental. Resultados são descartados.
    """
    print("=" * 70)
    print("FASE DE WARM-UP")
    print("=" * 70)
    print("Executando requisições de aquecimento para estabilizar conexões...")
    print()
    
    # IDs aleatórios fora da amostra experimental (51-100)
    warmup_ids = random.sample(range(51, 101), 5)
    
    # Warm-up REST
    print("Aquecimento REST:")
    for i, char_id in enumerate(warmup_ids, 1):
        time_ms, size_bytes, success = make_rest_request(char_id)
        status = "✓" if success else "✗"
        print(f"  {status} Requisição {i}/5 - ID {char_id}")
    
    print()
    
    # Warm-up GraphQL
    print("Aquecimento GraphQL:")
    for i, char_id in enumerate(warmup_ids, 1):
        time_ms, size_bytes, success = make_graphql_request(char_id)
        status = "✓" if success else "✗"
        print(f"  {status} Requisição {i}/5 - ID {char_id}")
    
    print()
    print("✓ Warm-up concluído. Iniciando coleta experimental...")
    print()


def run_experiment(start_id: int, end_id: int) -> list:
    """
    Executa o experimento principal coletando dados para todos os IDs especificados.
    
    Para cada ID, realiza:
    1. Requisição REST
    2. Requisição GraphQL
    
    Args:
        start_id: ID inicial do intervalo de personagens
        end_id: ID final do intervalo de personagens (inclusivo)
        
    Returns:
        Lista de dicionários com os resultados das medições
    """
    results = []
    total_ids = end_id - start_id + 1
    
    print("=" * 70)
    print("COLETA EXPERIMENTAL")
    print("=" * 70)
    print(f"Coletando dados para {total_ids} personagens (IDs {start_id} a {end_id})")
    print()
    
    for idx, character_id in enumerate(range(start_id, end_id + 1), 1):
        print(f"Processando ID {character_id} ({idx}/{total_ids})...")
        
        # Requisição REST
        time_rest, size_rest, success_rest = make_rest_request(character_id)
        
        if success_rest:
            results.append({
                'id': character_id,
                'type': 'REST',
                'time_ms': time_rest,
                'size_bytes': size_rest
            })
            print(f"  ✓ REST    : {time_rest:.2f} ms, {size_rest} bytes")
        else:
            print(f"  ✗ REST    : Falhou")
        
        # Pequeno delay para evitar rate limiting
        time.sleep(0.1)
        
        # Requisição GraphQL
        time_graphql, size_graphql, success_graphql = make_graphql_request(character_id)
        
        if success_graphql:
            results.append({
                'id': character_id,
                'type': 'GraphQL',
                'time_ms': time_graphql,
                'size_bytes': size_graphql
            })
            print(f"  ✓ GraphQL : {time_graphql:.2f} ms, {size_graphql} bytes")
        else:
            print(f"  ✗ GraphQL : Falhou")
        
        # Delay entre diferentes IDs
        time.sleep(0.1)
        print()
    
    return results


def save_results(results: list, output_file: str):
    """
    Salva os resultados do experimento em arquivo CSV.
    
    Args:
        results: Lista de dicionários com os resultados
        output_file: Nome do arquivo CSV de saída
    """
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False, encoding='utf-8')
    print("=" * 70)
    print("RESULTADOS SALVOS")
    print("=" * 70)
    print(f"✓ Arquivo salvo: {output_file}")
    print(f"✓ Total de registros: {len(df)}")
    print(f"✓ Registros REST: {len(df[df['type']=='REST'])}")
    print(f"✓ Registros GraphQL: {len(df[df['type']=='GraphQL'])}")
    print()


def display_summary(results: list):
    """
    Exibe um resumo estatístico básico dos resultados coletados.
    
    Args:
        results: Lista de dicionários com os resultados
    """
    df = pd.DataFrame(results)
    
    print("=" * 70)
    print("RESUMO ESTATÍSTICO PRELIMINAR")
    print("=" * 70)
    print()
    
    # Separar por tipo
    rest_df = df[df['type'] == 'REST']
    graphql_df = df[df['type'] == 'GraphQL']
    
    # Tempo de resposta
    print("TEMPO DE RESPOSTA (ms)")
    print("-" * 70)
    print(f"REST     - Média: {rest_df['time_ms'].mean():.2f} ms, "
          f"Mediana: {rest_df['time_ms'].median():.2f} ms, "
          f"DP: {rest_df['time_ms'].std():.2f} ms")
    print(f"GraphQL  - Média: {graphql_df['time_ms'].mean():.2f} ms, "
          f"Mediana: {graphql_df['time_ms'].median():.2f} ms, "
          f"DP: {graphql_df['time_ms'].std():.2f} ms")
    print()
    
    # Tamanho da resposta
    print("TAMANHO DA RESPOSTA (bytes)")
    print("-" * 70)
    print(f"REST     - Média: {rest_df['size_bytes'].mean():.0f} bytes, "
          f"Mediana: {rest_df['size_bytes'].median():.0f} bytes, "
          f"DP: {rest_df['size_bytes'].std():.0f} bytes")
    print(f"GraphQL  - Média: {graphql_df['size_bytes'].mean():.0f} bytes, "
          f"Mediana: {graphql_df['size_bytes'].median():.0f} bytes, "
          f"DP: {graphql_df['size_bytes'].std():.0f} bytes")
    print()
    
    # Diferenças
    diff_time = rest_df['time_ms'].mean() - graphql_df['time_ms'].mean()
    diff_size = rest_df['size_bytes'].mean() - graphql_df['size_bytes'].mean()
    reduction_pct = (diff_size / rest_df['size_bytes'].mean()) * 100
    
    print("DIFERENÇAS (REST - GraphQL)")
    print("-" * 70)
    print(f"Tempo médio : {diff_time:+.2f} ms "
          f"({'GraphQL mais rápido' if diff_time > 0 else 'REST mais rápido'})")
    print(f"Tamanho médio : {diff_size:+.0f} bytes ({reduction_pct:.1f}% de redução)")
    print()


def main():
    """
    Função principal que coordena a execução do experimento.
    """
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(
        description='Experimento: Comparação de Desempenho REST vs GraphQL'
    )
    parser.add_argument(
        '--start',
        type=int,
        default=1,
        help='ID inicial do intervalo de personagens (padrão: 1)'
    )
    parser.add_argument(
        '--end',
        type=int,
        default=50,
        help='ID final do intervalo de personagens (padrão: 50)'
    )
    parser.add_argument(
        '--out',
        type=str,
        default='experiment_results.csv',
        help='Nome do arquivo CSV de saída (padrão: experiment_results.csv)'
    )
    parser.add_argument(
        '--skip-warmup',
        action='store_true',
        help='Pular fase de warm-up (não recomendado)'
    )
    
    args = parser.parse_args()
    
    # Validações
    if args.start < 1:
        print("Erro: --start deve ser >= 1")
        return
    if args.end < args.start:
        print("Erro: --end deve ser >= --start")
        return
    if args.end - args.start + 1 > 200:
        print("Aviso: Amostra muito grande pode causar rate limiting")
        response = input("Continuar mesmo assim? (s/n): ")
        if response.lower() != 's':
            return
    
    # Exibir configuração
    print()
    print("=" * 70)
    print("EXPERIMENTO: REST vs GraphQL")
    print("=" * 70)
    print(f"API: Rick and Morty API")
    print(f"Intervalo de IDs: {args.start} a {args.end}")
    print(f"Total de personagens: {args.end - args.start + 1}")
    print(f"Total de requisições: {(args.end - args.start + 1) * 2}")
    print(f"Arquivo de saída: {args.out}")
    print()
    
    # Warm-up
    if not args.skip_warmup:
        warmup()
    else:
        print("⚠️  Warm-up ignorado (não recomendado)")
        print()
    
    # Executar experimento
    start_time = time.time()
    results = run_experiment(args.start, args.end)
    end_time = time.time()
    
    # Verificar se obtivemos resultados
    if not results:
        print("❌ Nenhum resultado coletado. Verifique sua conexão de rede.")
        return
    
    # Salvar resultados
    save_results(results, args.out)
    
    # Exibir resumo
    display_summary(results)
    
    # Estatísticas de execução
    print("=" * 70)
    print("ESTATÍSTICAS DE EXECUÇÃO")
    print("=" * 70)
    print(f"✓ Tempo total de execução: {(end_time - start_time):.2f} segundos")
    print(f"✓ Experimento concluído com sucesso!")
    print()
    print("Próximos passos:")
    print("  1. Validar os dados coletados")
    print("  2. Realizar análise estatística completa")
    print("  3. Gerar visualizações e relatório final")
    print()


if __name__ == "__main__":
    main()