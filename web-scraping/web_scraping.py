import requests
from bs4 import BeautifulSoup
import os
import zipfile
import re

def download_file(url, local_filename):
    """
    Faz o download de um arquivo e o salva localmente
    """
    print(f"Baixando arquivo de {url}...")
    
    # Adiciona cabeçalhos para simular um navegador
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Faz o request para baixar o arquivo
    response = requests.get(url, headers=headers, stream=True)
    
    # Verifica se o download foi bem-sucedido
    if response.status_code == 200:
        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Arquivo salvo como '{local_filename}'")
        return True
    else:
        print(f"Falha ao baixar arquivo. Status code: {response.status_code}")
        return False

def create_zip(files, zip_filename):
    """
    Compacta uma lista de arquivos em um único arquivo ZIP
    """
    print(f"Criando arquivo ZIP '{zip_filename}'...")
    
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for file in files:
            if os.path.exists(file):
                zipf.write(file, os.path.basename(file))
                print(f"Adicionado '{file}' ao ZIP")
            else:
                print(f"Arquivo '{file}' não encontrado")
    
    print(f"Arquivo ZIP '{zip_filename}' criado com sucesso!")

def main():
    # URL do site da ANS
    url = "https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos"
    
    # Cria um diretório para salvar os arquivos se não existir
    if not os.path.exists('anexos'):
        os.makedirs('anexos')
    
    # Faz o request para a página
    print(f"Acessando o site: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    
    # Verifica se o request foi bem-sucedido
    if response.status_code != 200:
        print(f"Falha ao acessar o site. Status code: {response.status_code}")
        return
    
    # Faz o parsing do HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Lista para armazenar os caminhos dos arquivos baixados
    downloaded_files = []
    
    # Procura por links que contenham 'Anexo I' ou 'Anexo II' e sejam PDFs
    links = soup.find_all('a', href=True)
    for link in links:
        href = link.get('href')
        text = link.get_text().lower()
        
        # Verifica se o link é para um anexo (I ou II) em formato PDF
        if (('anexo i' in text or 'anexo ii' in text) and href.endswith('.pdf')) or \
           (re.search(r'anexo[_\s-]*i{1,2}\.pdf', href.lower())):
            
            # Extrai o nome do arquivo a partir da URL
            filename = os.path.basename(href)
            
            # Se o nome do arquivo não contiver 'anexo' e um número romano, adiciona um prefixo
            if not re.search(r'anexo[_\s-]*i{1,2}', filename.lower()):
                if 'anexo i' in text:
                    filename = f"Anexo_I_{filename}"
                elif 'anexo ii' in text:
                    filename = f"Anexo_II_{filename}"
            
            # Caminho completo para salvar o arquivo
            filepath = os.path.join('anexos', filename)
            
            # Faz o download do arquivo
            if download_file(href, filepath):
                downloaded_files.append(filepath)
    
    # Verifica se encontrou os dois anexos
    if len(downloaded_files) < 2:
        print("Atenção: Não foi possível encontrar os dois anexos (I e II).")
        print(f"Foram encontrados {len(downloaded_files)} anexos.")
    
    # Compacta os arquivos baixados
    if downloaded_files:
        create_zip(downloaded_files, 'anexos_ans.zip')
    else:
        print("Nenhum arquivo foi baixado para compactar.")

if __name__ == "__main__":
    main()