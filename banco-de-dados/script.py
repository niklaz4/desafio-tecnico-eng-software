import os
import re
import csv
import requests
import zipfile
import pandas as pd
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime
from io import BytesIO
import shutil
import urllib.parse

# Diretório onde serão salvos os arquivos
DATA_DIR = './ans_data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Arquivo SQLite
DB_FILE = os.path.join(DATA_DIR, 'ans_database.db')

# Função para baixar os arquivos das demonstrações contábeis dos últimos 2 anos
def download_demonstracoes_contabeis():
    print("Baixando arquivos de demonstrações contábeis...")
    base_url = "https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/"
    
    # Obter lista de arquivos disponíveis na página
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extrair todos os links de arquivos
    anos_atuais = [str(datetime.now().year - i) for i in range(3)]  # Ano atual e os 2 anos anteriores
    
    # Filtrar links que contêm os anos desejados
    links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and any(ano in href for ano in anos_atuais) and href.endswith('.zip'):
            links.append(href)
    
    # Baixar os arquivos encontrados
    arquivos_baixados = []
    for link in links:
        arquivo_url = urllib.parse.urljoin(base_url, link)
        arquivo_path = os.path.join(DATA_DIR, link)
        
        print(f"Baixando {arquivo_url}...")
        try:
            response = requests.get(arquivo_url)
            
            if response.status_code == 200:
                with open(arquivo_path, 'wb') as f:
                    f.write(response.content)
                
                # Extrair o conteúdo do arquivo zip
                with zipfile.ZipFile(arquivo_path, 'r') as zip_ref:
                    zip_ref.extractall(os.path.join(DATA_DIR, os.path.splitext(link)[0]))
                
                arquivos_baixados.append(arquivo_path)
                print(f"Arquivo {link} baixado e extraído com sucesso.")
            else:
                print(f"Erro ao baixar o arquivo {link}. Status code: {response.status_code}")
        except Exception as e:
            print(f"Erro ao processar o arquivo {link}: {str(e)}")
    
    return arquivos_baixados

# Função para baixar os dados cadastrais das operadoras ativas
def download_operadoras_ativas():
    print("Baixando dados cadastrais das operadoras ativas...")
    url = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/"
    
    # Obter lista de arquivos disponíveis na página
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Encontrar o link do arquivo CSV mais recente
    csv_link = None
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and href.endswith('.csv'):
            csv_link = href
            break
    
    if not csv_link:
        print("Não foi encontrado nenhum arquivo CSV.")
        return None
    
    # Baixar o arquivo CSV
    csv_url = urllib.parse.urljoin(url, csv_link)
    csv_path = os.path.join(DATA_DIR, csv_link)
    
    print(f"Baixando {csv_url}...")
    try:
        response = requests.get(csv_url)
        
        if response.status_code == 200:
            with open(csv_path, 'wb') as f:
                f.write(response.content)
            print(f"Arquivo {csv_link} baixado com sucesso.")
            return csv_path
        else:
            print(f"Erro ao baixar o arquivo {csv_link}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Erro ao baixar o arquivo {csv_link}: {str(e)}")
        return None

# Função para criar banco de dados e tabelas (usando SQLite)
def create_database_and_tables():
    print("Criando banco de dados e tabelas (SQLite)...")
    
    # Conectar ao banco de dados SQLite (será criado se não existir)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Criar tabela para operadoras
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS operadoras (
        registro_ans VARCHAR(20) PRIMARY KEY,
        cnpj VARCHAR(20),
        razao_social VARCHAR(255),
        nome_fantasia VARCHAR(255),
        modalidade VARCHAR(100),
        logradouro VARCHAR(255),
        numero VARCHAR(20),
        complemento VARCHAR(100),
        bairro VARCHAR(100),
        cidade VARCHAR(100),
        uf VARCHAR(2),
        cep VARCHAR(10),
        ddd VARCHAR(5),
        telefone VARCHAR(20),
        fax VARCHAR(20),
        email VARCHAR(100),
        representante VARCHAR(255),
        cargo_representante VARCHAR(100),
        data_registro_ans DATE
    )
    """)
    
    # Criar tabela para demonstrações contábeis
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS demonstracoes_contabeis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        registro_ans VARCHAR(20),
        data_trimestre DATE,
        trimestre VARCHAR(10),
        codigo_conta VARCHAR(50),
        descricao_conta VARCHAR(255),
        valor DECIMAL(20, 2),
        FOREIGN KEY (registro_ans) REFERENCES operadoras(registro_ans)
    )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("Banco de dados e tabelas SQLite criados com sucesso.")

# Função para importar dados das operadoras
def import_operadoras_data(csv_path):
    print("Importando dados das operadoras...")
    
    if not csv_path or not os.path.exists(csv_path):
        print("Arquivo CSV das operadoras não encontrado.")
        return
    
    # Ler o arquivo CSV com o pandas
    try:
        # Tentar diferentes encodings
        encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(csv_path, encoding=encoding, sep=';', quotechar='"', on_bad_lines='skip')
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            print("Não foi possível ler o arquivo CSV com nenhum dos encodings tentados.")
            return
        
        # Mostrar as colunas existentes
        print(f"Colunas encontradas no arquivo CSV: {df.columns.tolist()}")
        
        # Renomear colunas para corresponder à estrutura da tabela
        colunas_mapeadas = {
            'Registro ANS': 'registro_ans',
            'CNPJ': 'cnpj',
            'Razão Social': 'razao_social',
            'Nome Fantasia': 'nome_fantasia',
            'Modalidade': 'modalidade',
            'Logradouro': 'logradouro',
            'Número': 'numero',
            'Complemento': 'complemento',
            'Bairro': 'bairro',
            'Cidade': 'cidade',
            'UF': 'uf',
            'CEP': 'cep',
            'DDD': 'ddd',
            'Telefone': 'telefone',
            'Fax': 'fax',
            'Endereço eletrônico': 'email',
            'Representante': 'representante',
            'Cargo Representante': 'cargo_representante',
            'Data Registro ANS': 'data_registro_ans'
        }
        
        # Verificar quais colunas existem no DataFrame
        colunas_existentes = {}
        for col_original, col_nova in colunas_mapeadas.items():
            if col_original in df.columns:
                colunas_existentes[col_original] = col_nova
        
        # Renomear apenas as colunas que existem
        df = df.rename(columns=colunas_existentes)
        
        # Obter lista de colunas existentes na tabela após renomeação
        colunas_tabela = [col for col in colunas_mapeadas.values() if col in df.columns]
        
        # Conectar ao banco de dados
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Inserir dados na tabela 'operadoras'
        for _, row in df.iterrows():
            valores = []
            placeholders = []
            colunas_validas = []
            
            for col in colunas_tabela:
                if col in df.columns:
                    valor = row[col]
                    valores.append(str(valor) if pd.notna(valor) else None)
                    placeholders.append('?')
                    colunas_validas.append(col)
            
            query = f"""
            INSERT OR IGNORE INTO operadoras ({', '.join(colunas_validas)})
            VALUES ({', '.join(placeholders)})
            """
            
            try:
                cursor.execute(query, valores)
            except Exception as e:
                print(f"Erro ao inserir linha: {e}")
                continue
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("Dados das operadoras importados com sucesso.")
        
    except Exception as e:
        print(f"Erro ao importar dados das operadoras: {e}")

# Função para processar arquivos XML/CSV das demonstrações contábeis
def process_demonstracoes_contabeis_files():
    print("Processando arquivos de demonstrações contábeis...")
    
    # Conectar ao banco de dados
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Encontrar todos os diretórios de demonstrações extraídos
    for raiz, dirs, arquivos in os.walk(DATA_DIR):
        for arquivo in arquivos:
            # Procurar por arquivos CSV ou XML das demonstrações contábeis
            if (arquivo.endswith('.csv') or arquivo.endswith('.CSV')) and 'demonstracoes' in raiz.lower():
                arquivo_path = os.path.join(raiz, arquivo)
                
                try:
                    # Extrair informações do nome do diretório/arquivo
                    # Exemplo: .../2023/3T.../arquivo.csv -> 2023, 3T
                    partes_caminho = raiz.split(os.sep)
                    ano = None
                    trimestre = None
                    
                    for parte in partes_caminho:
                        if re.match(r'^20\d{2}$', parte):  # Encontrar anos no formato 20XX
                            ano = parte
                        if re.match(r'^\d{1}T', parte):    # Encontrar trimestres no formato XT
                            trimestre = parte[:2]
                    
                    if not ano or not trimestre:
                        print(f"Não foi possível identificar ano e trimestre para {arquivo_path}")
                        continue
                    
                    # Construir data do trimestre
                    trimestre_num = int(trimestre[0])
                    mes = (trimestre_num - 1) * 3 + 3  # 1T -> mês 3, 2T -> mês 6, etc.
                    data_trimestre = f"{ano}-{mes:02d}-30"
                    
                    print(f"Processando arquivo {arquivo_path} - Ano: {ano}, Trimestre: {trimestre}")
                    
                    # Tentar diferentes encodings
                    encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
                    df = None
                    
                    for encoding in encodings:
                        try:
                            df = pd.read_csv(arquivo_path, encoding=encoding, sep=';', quotechar='"', on_bad_lines='skip')
                            break
                        except UnicodeDecodeError:
                            continue
                    
                    if df is None:
                        print(f"Não foi possível ler o arquivo CSV {arquivo_path} com nenhum dos encodings tentados.")
                        continue
                    
                    # Mostrar as colunas do arquivo para debugar
                    print(f"Colunas encontradas: {df.columns.tolist()}")
                    
                    # Identificar colunas relevantes - podem variar dependendo do formato
                    # Vamos procurar por colunas que possam conter os dados necessários
                    colunas_possiveis = {
                        'registro_ans': ['REGISTRO_ANS', 'Registro ANS', 'registro_ans', 'ans', 'REG_ANS'],
                        'codigo_conta': ['CODIGO', 'Código', 'codigo', 'cd_conta', 'COD_CONTA', 'CONTA'],
                        'descricao_conta': ['DESCRICAO', 'Descrição', 'descricao', 'desc_conta', 'DESC_CONTA', 'DESCRIÇÃO', 'NOME_CONTA'],
                        'valor': ['VL_SALDO_FINAL', 'Valor', 'valor', 'saldo', 'VL_SALDO_ATUAL', 'SALDO_FINAL', 'SALDO']
                    }
                    
                    # Mapear colunas encontradas
                    colunas_mapeadas = {}
                    for nome_padrao, alternativas in colunas_possiveis.items():
                        for alt in alternativas:
                            if alt in df.columns:
                                colunas_mapeadas[nome_padrao] = alt
                                break
                    
                    # Verificar se temos as colunas necessárias
                    colunas_necessarias = ['registro_ans', 'codigo_conta', 'descricao_conta', 'valor']
                    colunas_faltando = [col for col in colunas_necessarias if col not in colunas_mapeadas]
                    
                    if colunas_faltando:
                        print(f"Colunas necessárias faltando: {colunas_faltando}")
                        continue
                    
                    # Inserir dados na tabela
                    for _, row in df.iterrows():
                        try:
                            registro_ans = str(row[colunas_mapeadas['registro_ans']])
                            codigo_conta = str(row[colunas_mapeadas['codigo_conta']])
                            descricao_conta = str(row[colunas_mapeadas['descricao_conta']])
                            
                            # Tratar valor (pode estar em diferentes formatos)
                            valor_str = str(row[colunas_mapeadas['valor']]).replace('.', '').replace(',', '.')
                            try:
                                valor = float(valor_str)
                            except ValueError:
                                valor = 0.0
                            
                            # Verificar se a descrição da conta contém o texto desejado
                            if "EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR" in descricao_conta.upper():
                                print(f"Encontrada conta relevante: {descricao_conta}")
                            
                            # Inserir no banco de dados
                            query = """
                            INSERT INTO demonstracoes_contabeis
                            (registro_ans, data_trimestre, trimestre, codigo_conta, descricao_conta, valor)
                            VALUES (?, ?, ?, ?, ?, ?)
                            """
                            
                            cursor.execute(query, (
                                registro_ans,
                                data_trimestre,
                                trimestre,
                                codigo_conta,
                                descricao_conta,
                                valor
                            ))
                            
                        except Exception as e:
                            print(f"Erro ao inserir linha: {e}")
                            continue
                    
                    conn.commit()
                    print(f"Arquivo {arquivo_path} processado com sucesso.")
                    
                except Exception as e:
                    print(f"Erro ao processar arquivo {arquivo_path}: {e}")
    
    cursor.close()
    conn.close()
    print("Processamento de arquivos concluído.")
    
    # Agora, salvar as queries SQL para futuro uso
    save_sql_queries()

# Função para salvar as queries SQL em arquivos
def save_sql_queries():
    # Consulta 1: Operadoras com maiores despesas no último trimestre
    query_ultimo_trimestre = """
    SELECT 
        o.razao_social,
        o.registro_ans,
        dc.data_trimestre as trimestre,
        ABS(SUM(dc.valor)) as total_despesa
    FROM 
        demonstracoes_contabeis dc
    JOIN 
        operadoras o ON dc.registro_ans = o.registro_ans
    WHERE 
        dc.descricao_conta LIKE '%EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR%'
        AND dc.data_trimestre = (SELECT MAX(data_trimestre) FROM demonstracoes_contabeis)
    GROUP BY 
        o.razao_social, o.registro_ans
    ORDER BY 
        total_despesa DESC
    LIMIT 10
    """
    
    # Consulta 2: Operadoras com maiores despesas no último ano
    query_ultimo_ano = """
    SELECT 
        o.razao_social,
        o.registro_ans,
        strftime('%Y', dc.data_trimestre) as ano,
        ABS(SUM(dc.valor)) as total_despesa
    FROM 
        demonstracoes_contabeis dc
    JOIN 
        operadoras o ON dc.registro_ans = o.registro_ans
    WHERE 
        dc.descricao_conta LIKE '%EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR%'
        AND strftime('%Y', dc.data_trimestre) = strftime('%Y', (SELECT MAX(data_trimestre) FROM demonstracoes_contabeis))
    GROUP BY 
        o.razao_social, o.registro_ans
    ORDER BY 
        total_despesa DESC
    LIMIT 10
    """
    
    # Guardar as queries SQL em arquivos
    with open(os.path.join(DATA_DIR, 'query_ultimo_trimestre.sql'), 'w') as f:
        f.write(query_ultimo_trimestre)
    
    with open(os.path.join(DATA_DIR, 'query_ultimo_ano.sql'), 'w') as f:
        f.write(query_ultimo_ano)
    
    print("\nAs queries SQL foram salvas nos arquivos:")
    print(f"- {os.path.join(DATA_DIR, 'query_ultimo_trimestre.sql')}")
    print(f"- {os.path.join(DATA_DIR, 'query_ultimo_ano.sql')}")

# Função para executar as consultas analíticas
def run_analytical_queries():
    print("Executando consultas analíticas...")
    
    # Conectar ao banco de dados
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Para acessar as colunas pelo nome
    cursor = conn.cursor()
    
    # Consulta 1: Operadoras com maiores despesas no último trimestre
    print("\n1. 10 operadoras com maiores despesas em EVENTOS/SINISTROS no último trimestre:")
    
    query_ultimo_trimestre = """
    SELECT 
        o.razao_social,
        o.registro_ans,
        dc.data_trimestre as trimestre,
        ABS(SUM(dc.valor)) as total_despesa
    FROM 
        demonstracoes_contabeis dc
    JOIN 
        operadoras o ON dc.registro_ans = o.registro_ans
    WHERE 
        UPPER(dc.descricao_conta) LIKE '%EVENTOS%SINISTROS%ASSIST%NCIA%MEDICO%HOSPITALAR%'
        AND dc.data_trimestre = (SELECT MAX(data_trimestre) FROM demonstracoes_contabeis)
    GROUP BY 
        o.razao_social, o.registro_ans
    ORDER BY 
        total_despesa DESC
    LIMIT 10
    """
    
    try:
        cursor.execute(query_ultimo_trimestre)
        results = cursor.fetchall()
        
        if results:
            for i, row in enumerate(results, 1):
                print(f"{i}. {row['razao_social']} (ANS: {row['registro_ans']}) - Trimestre: {row['trimestre']} - Despesa: R$ {row['total_despesa']:,.2f}")
        else:
            print("Nenhum resultado encontrado para o último trimestre.")
    except Exception as e:
        print(f"Erro ao executar consulta do último trimestre: {e}")
    
    # Consulta 2: Operadoras com maiores despesas no último ano
    print("\n2. 10 operadoras com maiores despesas em EVENTOS/SINISTROS no último ano:")
    
    query_ultimo_ano = """
    SELECT 
        o.razao_social,
        o.registro_ans,
        strftime('%Y', dc.data_trimestre) as ano,
        ABS(SUM(dc.valor)) as total_despesa
    FROM 
        demonstracoes_contabeis dc
    JOIN 
        operadoras o ON dc.registro_ans = o.registro_ans
    WHERE 
        UPPER(dc.descricao_conta) LIKE '%EVENTOS%SINISTROS%ASSIST%NCIA%MEDICO%HOSPITALAR%'
        AND strftime('%Y', dc.data_trimestre) = strftime('%Y', (SELECT MAX(data_trimestre) FROM demonstracoes_contabeis))
    GROUP BY 
        o.razao_social, o.registro_ans
    ORDER BY 
        total_despesa DESC
    LIMIT 10
    """
    
    try:
        cursor.execute(query_ultimo_ano)
        results = cursor.fetchall()
        
        if results:
            for i, row in enumerate(results, 1):
                print(f"{i}. {row['razao_social']} (ANS: {row['registro_ans']}) - Ano: {row['ano']} - Despesa: R$ {row['total_despesa']:,.2f}")
        else:
            print("Nenhum resultado encontrado para o último ano.")
    except Exception as e:
        print(f"Erro ao executar consulta do último ano: {e}")
    
    cursor.close()
    conn.close()

# Função principal
def main():
    print("Iniciando processamento de dados da ANS (usando SQLite)...")
    
    # Etapa 1: Baixar os arquivos
    download_demonstracoes_contabeis()
    csv_path = download_operadoras_ativas()
    
    # Etapa 2: Criar banco de dados e tabelas
    create_database_and_tables()
    
    # Etapa 3: Importar dados das operadoras
    if csv_path:
        import_operadoras_data(csv_path)
    
    # Etapa 4: Processar arquivos das demonstrações contábeis
    process_demonstracoes_contabeis_files()
    
    # Etapa 5: Executar consultas analíticas
    run_analytical_queries()
    
    print("Processamento concluído com sucesso!")
    print(f"Banco de dados SQLite criado em: {DB_FILE}")
    print("Queries SQL salvas na pasta:", DATA_DIR)

if __name__ == "__main__":
    main()