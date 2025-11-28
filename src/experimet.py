import requests
import time
import argparse
import csv

REST_URL = "https://rickandmortyapi.com/api/character/{}"
GRAPHQL_URL = "https://rickandmortyapi.com/graphql"

QUERY_TEMPLATE = """
{
  character(id: "%s") {
    name
    species
    status
  }
}
"""

def measure_request(method, url, payload=None, timeout=10):
    start = time.perf_counter()

    if method == "GET":
        response = requests.get(url, timeout=timeout)
    else:
        response = requests.post(url, json={"query": payload}, timeout=timeout)

    elapsed_ms = (time.perf_counter() - start) * 1000
    size_bytes = len(response.content)
    return elapsed_ms, size_bytes


def warmup():
    print("Executando warm-up...")
    for _ in range(5):
        try:
            requests.get(REST_URL.format(1))
            requests.post(GRAPHQL_URL, json={"query": QUERY_TEMPLATE % 1})
        except:
            pass
    print("Warm-up concluído.\n")


def main(start, end, outfile, timeout):
    warmup()

    with open(outfile, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "type", "time_ms", "size_bytes"])

        for character_id in range(start, end + 1):
            # REST
            rest_url = REST_URL.format(character_id)
            t, s = measure_request("GET", rest_url, timeout=timeout)
            writer.writerow([character_id, "REST", round(t, 3), s])

            # GraphQL
            query = QUERY_TEMPLATE % character_id
            t, s = measure_request("POST", GRAPHQL_URL, payload=query, timeout=timeout)
            writer.writerow([character_id, "GraphQL", round(t, 3), s])

            print(f"ID {character_id}: OK")

    print(f"\nColeta concluída. Dados salvos em: {outfile}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Coleta de dados para experimento REST vs GraphQL")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=50)
    parser.add_argument("--out", type=str, default="experiment_results.csv")
    parser.add_argument("--timeout", type=int, default=10)

    args = parser.parse_args()

    main(args.start, args.end, args.out, args.timeout)
