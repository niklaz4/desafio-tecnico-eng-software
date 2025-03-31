import requests
import pandas as pd
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import io
import zipfile
import os

def download_pdf(pdf_url, filename):
    """Baixa o PDF e salva localmente."""
    response = requests.get(pdf_url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        return filename
    else:
        raise ValueError("Falha no download do PDF.")

def extract_text_from_pdf(pdf_path):
    """Extrai texto do PDF."""
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text("text") for page in doc)
    return text

def parse_text_to_dataframe(text):
    """Converte texto em DataFrame estruturado."""
    lines = text.split("\n")
    data = []
    
    for line in lines:
        if re.search(r'\d{2}/\d{2}/\d{4}', line):  # Se contém data, assume que é uma linha válida
            data.append(line.split())
    
    df = pd.DataFrame(data)
    return df

def extract_legends(text):
    """Extrai legendas do rodapé do PDF."""
    legends = {}
    legend_section = False
    
    for line in text.split("\n"):
        if "LEGENDAS" in line.upper():
            legend_section = True
            continue
        
        if legend_section:
            match = re.match(r'(\S+) - (.+)', line)
            if match:
                legends[match.group(1)] = match.group(2)
    
    return legends

def replace_abbreviations(df, legends):
    """Substitui abreviações nas colunas 'OD' e 'AMB'."""
    for col in ['OD', 'AMB']:
        if col in df.columns:
            df[col] = df[col].map(legends).fillna(df[col])
    return df

def save_csv_and_zip(df, csv_filename, zip_filename):
    """Salva o DataFrame em CSV e compacta em um ZIP."""
    df.to_csv(csv_filename, index=False, sep=';')
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(csv_filename, os.path.basename(csv_filename))
    
    os.remove(csv_filename)  # Remove CSV após compactação

def main():
    pdf_url = "https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos/Anexo_I_Rol_2021RN_465.2021_RN627L.2024.pdf"
    pdf_filename = "Anexo_I.pdf"
    csv_filename = "Teste_Nicollas.csv"
    zip_filename = "Teste_Nicollas.zip"
    
    download_pdf(pdf_url, pdf_filename)
    text = extract_text_from_pdf(pdf_filename)
    data_df = parse_text_to_dataframe(text)
    legends = extract_legends(text)
    data_df = replace_abbreviations(data_df, legends)
    save_csv_and_zip(data_df, csv_filename, zip_filename)
    
    print(f"Arquivo ZIP '{zip_filename}' criado com sucesso!")

if __name__ == "__main__":
    main()
