import os
import urllib.request
import pandas as pd
import sqlite3
from datetime import datetime
import zipfile
import io
import re
import ssl
import sys

# Configuração para ignorar erros de certificado SSL
ssl._create_default_https_context = ssl._create_unverified_context

def criar_diretorios():
    """Cria os diretórios necessários para o download dos arquivos"""
    os.makedirs('dados_ans/demonstracoes_contabeis', exist_ok=True)
    os.makedirs('dados_ans/operadoras_ativas', exist_ok=True)
    print("Diretórios criados com sucesso!")

def download_arquivo(url, caminho_destino):
    """Faz o download de um arquivo e salva no caminho especificado"""
    try:
        print(f"Baixando {url}...")
        urllib.request.urlretrieve(url, caminho_destino)
        print(f"Download concluído: {caminho_destino}")
        return True
    except Exception as e:
        print(f"Erro ao baixar {url}: {e}")
        return False

def baixar_demonstracoes_contabeis():
    """Baixa os arquivos de demonstrações contábeis dos últimos 2 anos"""
    anos = [2023, 2024]
    trimestres = [1, 2, 3, 4]
    
    arquivos_baixados = []
    
    for ano in anos:
        for trimestre in trimestres:
            url = f"https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/{ano}/{trimestre}T{ano}.csv"
            caminho_destino = f"dados_ans/demonstracoes_contabeis/{trimestre}T{ano}.csv"
            
            # Se o arquivo já existe, não baixa novamente
            if os.path.exists(caminho_destino):
                print(f"Arquivo {caminho_destino} já existe. Pulando download.")
                arquivos_baixados.append((ano, trimestre, caminho_destino))
                continue
            
            # Tenta fazer o download
            if download_arquivo(url, caminho_destino):
                arquivos_baixados.append((ano, trimestre, caminho_destino))
            else:
                # Se não conseguir baixar, tenta com extensão .zip
                url_zip = f"https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/{ano}/{trimestre}T{ano}.zip"
                caminho_zip = f"dados_ans/demonstracoes_contabeis/{trimestre}T{ano}.zip"
                
                if download_arquivo(url_zip, caminho_zip):
                    # Extrai o arquivo zip
                    with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
                        zip_ref.extractall("dados_ans/demonstracoes_contabeis/")
                    
                    # Remove o arquivo zip
                    os.remove(caminho_zip)
                    
                    # Verifica se o CSV foi extraído
                    if os.path.exists(caminho_destino):
                        arquivos_baixados.append((ano, trimestre, caminho_destino))
    
    return arquivos_baixados

def baixar_operadoras_ativas():
    """Baixa o arquivo de operadoras ativas"""
    url = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/operadoras_ativas.csv"
    caminho_destino = "dados_ans/operadoras_ativas/operadoras_ativas.csv"
    
    # Se o arquivo já existe, não baixa novamente
    if os.path.exists(caminho_destino):
        print(f"Arquivo {caminho_destino} já existe. Pulando download.")
        return caminho_destino
    
    # Tenta fazer o download
    if download_arquivo(url, caminho_destino):
        return caminho_destino
    
    # Se não conseguir baixar, tenta com extensão .zip
    url_zip = "https://dadosabertos.ans.gov.br/FTP/PDA/operadoras_de_plano_de_saude_ativas/operadoras_ativas.zip"
    caminho_zip = "dados_ans/operadoras_ativas/operadoras_ativas.zip"
    
    if download_arquivo(url_zip, caminho_zip):
        # Extrai o arquivo zip
        with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
            zip_ref.extractall("dados_ans/operadoras_ativas/")
        
        # Remove o arquivo zip
        os.remove(caminho_zip)
        
        # Verifica se o CSV foi extraído
        if os.path.exists(caminho_destino):
            return caminho_destino
    
    return None

def criar_banco_sqlite():
    """Cria o banco de dados SQLite e as tabelas necessárias"""
    # Conecta ao banco de dados (cria se não existir)
    conn = sqlite3.connect("ans_database.db")
    cursor = conn.cursor()
    
    # Cria tabela para demonstrações contábeis
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS demonstracoes_contabeis (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_importacao TEXT DEFAULT CURRENT_TIMESTAMP,
        ano INTEGER,
        trimestre INTEGER,
        registro_ans TEXT,
        cd_conta_contabil TEXT,
        descricao TEXT,
        vl_saldo_final REAL
    )
    ''')
    
    # Cria tabela para operadoras ativas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS operadoras_ativas (
        registro_ans TEXT PRIMARY KEY,
        cnpj TEXT,
        razao_social TEXT,
        nome_fantasia TEXT,
        modalidade TEXT,
        logradouro TEXT,
        numero TEXT,
        complemento TEXT,
        bairro TEXT,
        cidade TEXT,
        uf TEXT,
        cep TEXT,
        ddd TEXT,
        telefone TEXT,
        fax TEXT,
        email TEXT,
        representante TEXT,
        cargo_representante TEXT,
        data_registro TEXT,
        data_atualizacao_dados TEXT
    )
    ''')
    
    # Cria índices para otimizar consultas
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_registro_ans ON demonstracoes_contabeis(registro_ans)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ano_trimestre ON demonstracoes_contabeis(ano, trimestre)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_cd_conta_contabil ON demonstracoes_contabeis(cd_conta_contabil)')
    
    # Salva as alterações
    conn.commit()
    conn.close()
    
    print("Banco de dados e tabelas criados com sucesso!")

def detectar_encoding(arquivo):
    """Tenta detectar o encoding do arquivo"""
    encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(arquivo, 'r', encoding=encoding) as f:
                f.read(1024)  # Tenta ler os primeiros 1024 bytes
                return encoding
        except UnicodeDecodeError:
            continue
    
    # Se falhar em detectar, retorna utf-8 como padrão
    return 'utf-8'

def detectar_delimitador(arquivo, encoding):
    """Tenta detectar o delimitador do arquivo CSV"""
    with open(arquivo, 'r', encoding=encoding) as f:
        linha = f.readline()
        
        if ';' in linha:
            return ';'
        elif ',' in linha:
            return ','
        elif '\t' in linha:
            return '\t'
        
    # Se falhar em detectar, retorna ponto e vírgula como padrão
    return ';'

def limpar_valor(valor):
    """Limpa e converte um valor monetário para float"""
    if isinstance(valor, str):
        # Remove caracteres não numéricos, exceto ponto e vírgula
        valor_limpo = re.sub(r'[^\d,.-]', '', valor)
        
        # Trata diferentes formatos de números
        if ',' in valor_limpo and '.' in valor_limpo:
            # Formato brasileiro (ex: 1.234,56)
            valor_limpo = valor_limpo.replace('.', '').replace(',', '.')
        elif ',' in valor_limpo:
            # Formato com vírgula como decimal
            valor_limpo = valor_limpo.replace(',', '.')
        
        try:
            return float(valor_limpo)
        except ValueError:
            return 0.0
    elif pd.isna(valor):
        return 0.0
    else:
        return float(valor)

def importar_demonstracoes_contabeis(arquivos_baixados):
    """Importa os dados das demonstrações contábeis para o banco de dados"""
    conn = sqlite3.connect("ans_database.db")
    
    # Verificar se já existem dados no banco
    query = "SELECT COUNT(*) FROM demonstracoes_contabeis"
    count = pd.read_sql_query(query, conn).iloc[0, 0]
    
    if count > 0:
        print(f"Já existem {count} registros na tabela de demonstrações contábeis. Pulando importação.")
        conn.close()
        return
    
    for ano, trimestre, arquivo in arquivos_baixados:
        print(f"Importando {arquivo}...")
        
        # Detecta encoding e delimitador
        encoding = detectar_encoding(arquivo)
        delimitador = detectar_delimitador(arquivo, encoding)
        
        try:
            # Lê o arquivo CSV
            df = pd.read_csv(arquivo, delimiter=delimitador, encoding=encoding, low_memory=False)
            
            # Verifica e padroniza os nomes das colunas
            colunas = [col.lower() for col in df.columns]
            df.columns = colunas
            
            # Identifica colunas relevantes
            registro_col = next((col for col in colunas if 'registro' in col and 'ans' in col), None)
            conta_col = next((col for col in colunas if 'conta' in col), None)
            descricao_col = next((col for col in colunas if 'descri' in col), None)
            saldo_col = next((col for col in colunas if 'saldo' in col), None)
            
            if not all([registro_col, conta_col, descricao_col, saldo_col]):
                print(f"Colunas necessárias não encontradas em {arquivo}. Pulando.")
                continue
            
            # Cria DataFrame com as colunas padronizadas
            df_padronizado = pd.DataFrame({
                'ano': ano,
                'trimestre': trimestre,
                'registro_ans': df[registro_col],
                'cd_conta_contabil': df[conta_col],
                'descricao': df[descricao_col],
                'vl_saldo_final': df[saldo_col].apply(limpar_valor)
            })
            
            # Importa para o banco de dados
            df_padronizado.to_sql('demonstracoes_contabeis', conn, if_exists='append', index=False)
            
            print(f"Importação de {arquivo} concluída: {len(df_padronizado)} registros.")
        
        except Exception as e:
            print(f"Erro ao importar {arquivo}: {e}")
    
    conn.close()

def importar_operadoras_ativas(arquivo):
    """Importa os dados das operadoras ativas para o banco de dados"""
    if not arquivo:
        print("Arquivo de operadoras ativas não encontrado.")
        return
    
    conn = sqlite3.connect("ans_database.db")
    
    # Verificar se já existem dados no banco
    query = "SELECT COUNT(*) FROM operadoras_ativas"
    count = pd.read_sql_query(query, conn).iloc[0, 0]
    
    if count > 0:
        print(f"Já existem {count} registros na tabela de operadoras ativas. Pulando importação.")
        conn.close()
        return
    
    print(f"Importando {arquivo}...")
    
    # Detecta encoding e delimitador
    encoding = detectar_encoding(arquivo)
    delimitador = detectar_delimitador(arquivo, encoding)
    
    try:
        # Lê o arquivo CSV
        df = pd.read_csv(arquivo, delimiter=delimitador, encoding=encoding, low_memory=False)
        
        # Padroniza os nomes das colunas
        colunas = [col.lower() for col in df.columns]
        df.columns = colunas
        
        # Mapeia as colunas para o modelo do banco de dados
        colunas_mapeadas = {
            'registro_ans': next((col for col in colunas if 'registro' in col and 'ans' in col), None),
            'cnpj': next((col for col in colunas if 'cnpj' in col), None),
            'razao_social': next((col for col in colunas if 'razao' in col and 'social' in col), None),
            'nome_fantasia': next((col for col in colunas if 'fantasia' in col or 'nome_fantasia' in col), None),
            'modalidade': next((col for col in colunas if 'modalidade' in col), None),
            'logradouro': next((col for col in colunas if 'logradouro' in col), None),
            'numero': next((col for col in colunas if 'numero' in col or 'número' in col), None),
            'complemento': next((col for col in colunas if 'complemento' in col), None),
            'bairro': next((col for col in colunas if 'bairro' in col), None),
            'cidade': next((col for col in colunas if 'cidade' in col or 'municipio' in col), None),
            'uf': next((col for col in colunas if 'uf' in col or 'estado' in col), None),
            'cep': next((col for col in colunas if 'cep' in col), None),
            'ddd': next((col for col in colunas if 'ddd' in col), None),
            'telefone': next((col for col in colunas if 'telefone' in col or 'fone' in col), None),
            'fax': next((col for col in colunas if 'fax' in col), None),
            'email': next((col for col in colunas if 'email' in col or 'e-mail' in col), None),
            'representante': next((col for col in colunas if 'representante' in col), None),
            'cargo_representante': next((col for col in colunas if 'cargo' in col), None),
            'data_registro': next((col for col in colunas if 'registro' in col and 'data' in col), None),
            'data_atualizacao_dados': next((col for col in colunas if 'atualiza' in col and 'data' in col), None)
        }
        
        # Filtra colunas que foram encontradas
        colunas_validas = {k: v for k, v in colunas_mapeadas.items() if v is not None}
        
        if 'registro_ans' not in colunas_validas:
            print(f"Coluna registro_ans não encontrada em {arquivo}. Pulando.")
            return
        
        # Cria DataFrame com as colunas padronizadas
        df_padronizado = pd.DataFrame()
        
        for col_destino, col_origem in colunas_validas.items():
            df_padronizado[col_destino] = df[col_origem]
        
        # Preenche colunas ausentes com None
        for col in set(colunas_mapeadas.keys()) - set(colunas_validas.keys()):
            df_padronizado[col] = None
        
        # Importa para o banco de dados
        df_padronizado.to_sql('operadoras_ativas', conn, if_exists='append', index=False)
        
        print(f"Importação de {arquivo} concluída: {len(df_padronizado)} registros.")
    
    except Exception as e:
        print(f"Erro ao importar {arquivo}: {e}")
    
    conn.close()

def executar_analise_maiores_despesas():
    """Executa a análise das operadoras com maiores despesas"""
    conn = sqlite3.connect("ans_database.db")
    
    # Identifica os valores mais recentes disponíveis
    query_ultimo_periodo = """
    SELECT ano, trimestre
    FROM demonstracoes_contabeis
    GROUP BY ano, trimestre
    ORDER BY ano DESC, trimestre DESC
    LIMIT 1
    """
    
    ultimo_periodo = pd.read_sql_query(query_ultimo_periodo, conn)
    
    if len(ultimo_periodo) == 0:
        print("Não há dados disponíveis para análise.")
        conn.close()
        return
    
    ultimo_ano = ultimo_periodo.iloc[0]['ano']
    ultimo_trimestre = ultimo_periodo.iloc[0]['trimestre']
    
    print(f"\nAnalisando dados do último período disponível: {ultimo_trimestre}T{ultimo_ano}\n")
    
    # 1. As 10 operadoras com maiores despesas em "EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR" no último trimestre
    query_ultimo_trimestre = """
    SELECT 
        d.registro_ans,
        o.razao_social,
        d.vl_saldo_final AS valor_despesa
    FROM 
        demonstracoes_contabeis d
    LEFT JOIN 
        operadoras_ativas o ON d.registro_ans = o.registro_ans
    WHERE 
        d.ano = ? AND d.trimestre = ?
        AND (
            d.descricao LIKE '%EVENTOS%SINISTROS CONHECIDOS OU AVISADOS%ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR%'
            OR d.descricao LIKE '%EVENTOS/%SINISTROS CONHECIDOS OU AVISADOS%ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR%'
        )
    ORDER BY 
        d.vl_saldo_final DESC
    LIMIT 10
    """
    
    df_ultimo_trimestre = pd.read_sql_query(query_ultimo_trimestre, conn, params=(ultimo_ano, ultimo_trimestre))
    
    # 2. As 10 operadoras com maiores despesas nessa categoria no último ano
    query_ultimo_ano = """
    SELECT 
        d.registro_ans,
        o.razao_social,
        SUM(d.vl_saldo_final) AS valor_despesa
    FROM 
        demonstracoes_contabeis d
    LEFT JOIN 
        operadoras_ativas o ON d.registro_ans = o.registro_ans
    WHERE 
        d.ano = ?
        AND (
            d.descricao LIKE '%EVENTOS%SINISTROS CONHECIDOS OU AVISADOS%ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR%'
            OR d.descricao LIKE '%EVENTOS/%SINISTROS CONHECIDOS OU AVISADOS%ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR%'
        )
    GROUP BY 
        d.registro_ans, o.razao_social
    ORDER BY 
        valor_despesa DESC
    LIMIT 10
    """
    
    df_ultimo_ano = pd.read_sql_query(query_ultimo_ano, conn, params=(ultimo_ano,))
    
    conn.close()
    
    # Formata os valores monetários
    df_ultimo_trimestre['valor_despesa'] = df_ultimo_trimestre['valor_despesa'].apply(
        lambda x: f"R$ {x:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
    )
    
    df_ultimo_ano['valor_despesa'] = df_ultimo_ano['valor_despesa'].apply(
        lambda x: f"R$ {x:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
    )
    
    # Exibe os resultados
    print("="*100)
    print(f"TOP 10 OPERADORAS COM MAIORES DESPESAS EM 'EVENTOS/SINISTROS CONHECIDOS OU AVISADOS DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR' NO ÚLTIMO TRIMESTRE ({ultimo_trimestre}T{ultimo_ano})")
    print("="*100)
    print(df_ultimo_trimestre.to_string(index=False))
    
    print("\n\n")
    print("="*100)
    print(f"TOP 10 OPERADORAS COM MAIORES DESPESAS EM 'EVENTOS/SINISTROS CONHECIDOS OU AVISADOS DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR' NO ÚLTIMO ANO ({ultimo_ano})")
    print("="*100)
    print(df_ultimo_ano.to_string(index=False))
    
    # Salva os resultados em CSV
    df_ultimo_trimestre.to_csv(f"top10_operadoras_ultimo_trimestre_{ultimo_trimestre}T{ultimo_ano}.csv", index=False)
    df_ultimo_ano.to_csv(f"top10_operadoras_ultimo_ano_{ultimo_ano}.csv", index=False)
    
    print("\n\nResultados salvos em arquivos CSV.")

def main():
    try:
        print("="*100)
        print("ANÁLISE DE DADOS DA ANS - DEMONSTRAÇÕES CONTÁBEIS E OPERADORAS ATIVAS")
        print("="*100)
        
        # 1. Criar diretórios
        criar_diretorios()
        
        # 2. Baixar arquivos
        print("\nBaixando arquivos de demonstrações contábeis...")
        arquivos_demonstracoes = baixar_demonstracoes_contabeis()
        
        print("\nBaixando arquivo de operadoras ativas...")
        arquivo_operadoras = baixar_operadoras_ativas()
        
        # 3. Criar banco de dados
        print("\nCriando banco de dados...")
        criar_banco_sqlite()
        
        # 4. Importar dados
        print("\nImportando demonstrações contábeis...")
        importar_demonstracoes_contabeis(arquivos_demonstracoes)
        
        print("\nImportando operadoras ativas...")
        importar_operadoras_ativas(arquivo_operadoras)
        
        # 5. Executar análises
        print("\nExecutando análises...")
        executar_analise_maiores_despesas()
        
        print("\n\nProcessamento concluído com sucesso!")
    
    except Exception as e:
        print(f"\nErro durante a execução: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()