import requests
from urllib.parse import urljoin

def post_to_api(url, url_download, bucket_name, output_file_prefix):
    endpoint = urljoin(url, '/download_combustivel')  # Substitua '/your/api/endpoint' pelo caminho real da API

    payload = {
        "bucket_name": bucket_name,
        "output_file_prefix": output_file_prefix,
        "url": url_download
    }

    try:
        response = requests.post(endpoint, json=payload)
        if response.status_code == 200:
            print("POST request successful.")
        else:
            print(f"Failed to make POST request. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error making POST request: {e}")

# Exemplo de uso
url = "https://stack-gcp-data-pipeline-pgku6pxwlq-uc.a.run.app/"
url_download = "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/arquivos/shpc/dsas/glp/glp-2005-01.csv"
bucket_name = "data-pipelines-combustiveis-br-raw"
output_file_prefix = "combustiveis-brasil/2019/02/ca-2005-01.csv"
post_to_api(url, url_download, bucket_name, output_file_prefix)
