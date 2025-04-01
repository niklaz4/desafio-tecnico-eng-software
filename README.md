# Desafio Técnico - TESTES DE NIVELAMENTO 

Este repositório contém os testes técnicos solicitados, divididos em quatro partes principais:

1. **Teste de Web Scraping**
2. **Teste de Transformação de Dados**
3. **Teste de Banco de Dados**
4. **Teste de API**

## 1. Teste de Web Scraping

### Como executar:
1. Certifique-se de que o ambiente Python esteja configurado.
2. Execute o código do Web Scraping (detalhes fornecidos no código).
3. O script irá acessar a página, baixar os anexos em PDF e compactá-los em um arquivo ZIP.

## 2. Teste de Transformação de Dados

### Como executar:
1. Certifique-se de que o ambiente Python esteja configurado e que a biblioteca para leitura de PDFs esteja instalada.
2. Execute o script de transformação de dados.
3. O código irá processar o PDF, extrair os dados da tabela, salvar os dados em formato CSV e compactá-los em um arquivo ZIP.

## 3. Teste de Banco de Dados

1. Importe os arquivos CSV para o banco de dados MySQL 8.0 ou PostgreSQL > 10.0 utilizando os scripts SQL.
2. Execute as queries analíticas para obter as 10 operadoras com maiores despesas.

## 4. Teste de API

1. Certifique-se de ter o ambiente de desenvolvimento Vue.js e Python configurado.
2. Execute o servidor Python, que estará aguardando requisições.
3. Acesse a interface web e realize buscas na lista de cadastros de operadoras.
4. Utilize o Postman para testar a API e ver os resultados.

## Instruções gerais de compilação

### 1. **Instalar dependências:**
- Para Python: Verifique se as bibliotecas necessárias estão instaladas, como `requests`, `pdfplumber`, `pandas`, etc.
- Para Vue.js: Utilize o comando `npm run serve` para instalar as dependências.

### 2. **Executar scripts Python:**
- Para rodar os testes de Web Scraping e Transformação de Dados, basta executar os respectivos scripts Python utilizando o comando:
  ```bash
  python nome_do_script.py
