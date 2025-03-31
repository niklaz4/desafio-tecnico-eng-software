from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import re

app = Flask(__name__)
CORS(app)  # Permitir requisições cross-origin

# Função para carregar o CSV de operadoras
def carregar_dados_operadoras():
    try:
        import os
        caminho_csv = os.path.join('backend', 'Relatorio_cadop.csv')
        
        # Tente determinar o delimitador correto
        # Experimente diferentes opções de delimitador
        for delimiter in [',', ';', '\t', '|']:
            try:
                print(f"Tentando ler com delimitador: '{delimiter}'")
                df = pd.read_csv(caminho_csv, 
                                encoding='latin1', 
                                delimiter=delimiter,
                                error_bad_lines=False,  # Ignora linhas problemáticas
                                warn_bad_lines=True)    # Avisa quando encontrar linha ruim
                print(f"Sucesso! CSV carregado com delimitador '{delimiter}'. Colunas: {df.columns.tolist()}")
                return df
            except Exception as e:
                print(f"  Falha com delimitador '{delimiter}': {e}")
        
        # Se todos os delimitadores falharem, tente ler uma linha de cada vez
        print("Tentando ler o arquivo linha por linha...")
        with open(caminho_csv, 'r', encoding='latin1') as file:
            linhas = file.readlines()
            
        print(f"Primeiras 10 linhas do arquivo:")
        for i, linha in enumerate(linhas[:10]):
            print(f"Linha {i+1}: {linha.strip()}")
            
        # Última tentativa: carregar ignorando erros
        print("Tentando carregar ignorando erros...")
        df = pd.read_csv(caminho_csv, 
                         encoding='latin1',
                         on_bad_lines='skip')
        
        print(f"CSV carregado ignorando linhas problemáticas. {len(df)} linhas lidas.")
        return df
    except Exception as e:
        print(f"Erro ao carregar CSV: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()
    
# Função para buscar operadoras com base em texto
def buscar_operadoras(texto_busca, df):
    # Convertendo para minúsculas para busca case-insensitive
    texto_busca = texto_busca.lower()
    
    # Lista de colunas onde faremos a busca
    colunas_busca = df.columns.tolist()
    
    # Convertendo valores para string e realizando a busca
    resultados = pd.DataFrame()
    
    for coluna in colunas_busca:
        # Filtrando registros que contêm o texto de busca
        matches = df[df[coluna].astype(str).str.lower().str.contains(texto_busca, na=False)]
        resultados = pd.concat([resultados, matches]).drop_duplicates()
    
    # Ordenando por relevância (poderia ser implementado um score mais sofisticado)
    # Aqui estamos apenas contando quantas vezes o termo aparece em cada registro
    def calcular_relevancia(row):
        score = 0
        for coluna in colunas_busca:
            value = str(row[coluna]).lower()
            score += value.count(texto_busca)
        return score
    
    # Aplicando função de relevância
    if not resultados.empty:
        resultados['relevancia'] = resultados.apply(calcular_relevancia, axis=1)
        resultados = resultados.sort_values('relevancia', ascending=False)
        resultados = resultados.drop('relevancia', axis=1)
    
    return resultados

# Rota para busca de operadoras
@app.route('/api/operadoras/buscar', methods=['GET'])
def api_buscar_operadoras():
    termo_busca = request.args.get('q', '')
    
    if not termo_busca:
        return jsonify({"erro": "Termo de busca não fornecido"}), 400
    
    df = carregar_dados_operadoras()
    
    if df.empty:
        return jsonify({"erro": "Falha ao carregar dados das operadoras"}), 500
    
    resultados = buscar_operadoras(termo_busca, df)
    
    # Convertendo resultados para JSON
    resultados_json = resultados.to_dict(orient='records')
    
    return jsonify({
        "termo_busca": termo_busca,
        "total_resultados": len(resultados_json),
        "resultados": resultados_json
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')