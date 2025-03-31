<template>
  <div class="app-container">
    <!-- Header -->
    <header class="app-header">
      <div class="container">
        <h1 class="app-title">Teste Técnico</h1>
        <p class="app-subtitle">Pesquise informações sobre operadoras de planos de saúde</p>
      </div>
    </header>

    <!-- Main Content -->
    <main class="container main-content">
      <!-- Search Section -->
      <div class="search-card">
        <div class="search-form">
          <div class="search-input-container">
            <label for="search" class="search-label">Termo de Busca</label>
            <div class="search-input-wrapper">
              <span class="search-icon">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
                </svg>
              </span>
              <input
                id="search"
                v-model="termoBusca"
                @keyup.enter="buscarOperadoras"
                type="text"
                placeholder="Digite o nome ou informação da operadora..."
                class="search-input"
              />
              <span class="enter-key">Enter</span>
            </div>
          </div>
          <button
            @click="buscarOperadoras"
            :disabled="carregando"
            class="search-button"
            :class="{ 'loading': carregando }"
          >
            <span v-if="carregando" class="spinner"></span>
            <span v-if="!carregando">Buscar</span>
            <span v-else>Buscando...</span>
          </button>
        </div>
      </div>

      <!-- Error Alert -->
      <div v-if="erro" class="error-alert">
        <div class="error-icon">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <p class="error-message">{{ erro }}</p>
      </div>

      <!-- Results Section -->
      <div v-if="buscaRealizada && !carregando">
        <!-- Results Header -->
        <div class="results-header">
          <h2 class="results-title">
            {{ resultados.length > 0 ? `Resultados da busca: ${totalResultados}` : '' }}
          </h2>
          <div v-if="resultados.length > 0" class="export-container">
            <button @click="exportarCSV" class="export-button">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Exportar CSV
            </button>
          </div>
        </div>

        <!-- No Results -->
        <div v-if="resultados.length === 0" class="no-results">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 class="no-results-title">Nenhum resultado encontrado</h3>
          <p class="no-results-subtitle">Não encontramos operadoras que correspondam ao termo "{{ termoBusca }}".</p>
          <button @click="limparBusca" class="clear-button">
            Limpar busca
          </button>
        </div>

        <!-- Results Table -->
        <div v-else class="results-table-container">
          <div class="table-wrapper">
            <table class="results-table">
              <thead>
                <tr>
                  <th v-for="(coluna, index) in colunas" :key="index">
                    {{ coluna }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(operadora, index) in resultados" :key="index">
                  <td v-for="(coluna, colIndex) in colunas" :key="colIndex">
                    {{ operadora[coluna] }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <!-- Pagination -->
          <div class="pagination">
            <div class="pagination-mobile">
              <button class="pagination-button">Anterior</button>
              <button class="pagination-button">Próximo</button>
            </div>
            <div class="pagination-desktop">
              <div class="pagination-info">
                <p>
                  Mostrando <span>1</span> a <span>{{ Math.min(totalResultados, 10) }}</span> de <span>{{ totalResultados }}</span> resultados
                </p>
              </div>
              <div class="pagination-controls">
                <button class="pagination-arrow" aria-label="Anterior">
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </button>
                <button class="pagination-number active">1</button>
                <button class="pagination-arrow" aria-label="Próximo">
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="carregando" class="loading-container">
        <div class="loading-spinner"></div>
        <h3 class="loading-title">Buscando operadoras</h3>
        <p class="loading-subtitle">Aguarde enquanto processamos sua solicitação...</p>
      </div>
    </main>

    <!-- Footer -->
    <footer class="app-footer">
      <div class="container footer-content">
        <div class="footer-copyright">
          <p>&copy; 2025 Nicollas Alcântara. Todos os direitos reservados.</p>
        </div>
        <div class="footer-links">
          <a href="#">Termos</a>
          <a href="#">Privacidade</a>
          <a href="#">Ajuda</a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'BuscaOperadoras',
  data() {
    return {
      termoBusca: '',
      resultados: [],
      totalResultados: 0,
      carregando: false,
      erro: null,
      buscaRealizada: false,
      colunas: []
    }
  },
  methods: {
    async buscarOperadoras() {
      if (!this.termoBusca.trim()) {
        this.erro = 'Digite um termo para buscar';
        return;
    }

    this.erro = null;
    this.carregando = true;
    this.buscaRealizada = true;
  
    try {
      console.log(`Enviando requisição para buscar: ${this.termoBusca}`);
      const response = await axios.get('http://127.0.0.1:5000/api/operadoras/buscar', {
        params: { q: this.termoBusca }
      });
    
      console.log('Resposta recebida:', response.data);
      this.resultados = response.data.resultados;
      this.totalResultados = response.data.total_resultados;
    
      // Extrair colunas do primeiro resultado, se existir
      if (this.resultados.length > 0) {
        this.colunas = Object.keys(this.resultados[0]);
        console.log('Colunas detectadas:', this.colunas);
      }
    } catch (error) {
      console.error('Erro na busca:', error);
      // Detalhamento melhor do erro
      if (error.response) {
      // Resposta do servidor com código de erro
        console.error('Dados do erro:', error.response.data);
        console.error('Status:', error.response.status);
        this.erro = `Erro ${error.response.status}: ${error.response.data.erro || 'Erro desconhecido'}`;
      } else if (error.request) {
        // Requisição foi feita mas não teve resposta
        console.error('Sem resposta do servidor');
        this.erro = 'Servidor não respondeu. Verifique se o backend está rodando.';
      } else {
      // Algo aconteceu durante a configuração da requisição
      this.erro = 'Erro ao configurar requisição: ' + error.message;
    }
    this.resultados = [];
    } finally {
      this.carregando = false;
    }
  },
    
    limparBusca() {
      this.termoBusca = '';
      this.resultados = [];
      this.totalResultados = 0;
      this.erro = null;
      this.buscaRealizada = false;
    },
    
    exportarCSV() {
      if (!this.resultados.length) return;
      
      const csvRows = [];
      
      // Adicionar cabeçalhos
      csvRows.push(this.colunas.join(','));
      
      // Adicionar dados
      this.resultados.forEach(item => {
        const values = this.colunas.map(coluna => {
          const cell = item[coluna] + '';
          // Escapar aspas e adicionar aspas ao redor se contém vírgula
          return cell.includes(',') ? `"${cell.replace(/"/g, '""')}"` : cell;
        });
        csvRows.push(values.join(','));
      });
      
      // Criar blob e link para download
      const csvString = csvRows.join('\n');
      const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `operadoras_${this.termoBusca.replace(/\s+/g, '_')}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  }
}
</script>

<style>
/* Reset e estilos globais */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.5;
  color: #333;
  background-color: #f5f7fa;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* Header */
.app-header {
  background: linear-gradient(135deg, #3a7bd5 0%, #2b4bc9 100%);
  color: white;
  padding: 30px 0;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.app-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
}

.app-subtitle {
  font-size: 16px;
  opacity: 0.9;
}

/* Main Content */
.main-content {
  flex: 1;
  padding: 30px 0;
}

/* Search Card */
.search-card {
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  padding: 24px;
  margin-bottom: 30px;
}

.search-form {
  display: flex;
  flex-direction: column;
}

@media (min-width: 768px) {
  .search-form {
    flex-direction: row;
    align-items: flex-end;
    gap: 16px;
  }
}

.search-input-container {
  flex-grow: 1;
  margin-bottom: 16px;
}

@media (min-width: 768px) {
  .search-input-container {
    margin-bottom: 0;
  }
}

.search-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #4b5563;
  margin-bottom: 6px;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 12px;
  color: #9ca3af;
}

.search-input {
  display: block;
  width: 100%;
  padding: 12px 12px 12px 40px;
  font-size: 14px;
  line-height: 1.5;
  color: #1f2937;
  background-color: #fff;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  transition: all 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
}

.enter-key {
  position: absolute;
  right: 8px;
  background-color: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  color: #6b7280;
  border: 1px solid #d1d5db;
}

.search-button {
  padding: 12px 24px;
  background-color: #4f46e5;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 120px;
}

.search-button:hover {
  background-color: #4338ca;
}

.search-button:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.4);
}

.search-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.search-button.loading {
  background-color: #6366f1;
}

.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
  margin-right: 8px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Error Alert */
.error-alert {
  display: flex;
  align-items: center;
  background-color: #fee2e2;
  border-left: 4px solid #ef4444;
  padding: 16px;
  border-radius: 6px;
  margin-bottom: 24px;
}

.error-icon {
  flex-shrink: 0;
  color: #ef4444;
  margin-right: 12px;
}

.error-message {
  font-size: 14px;
  color: #b91c1c;
}

/* Results Header */
.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.results-title {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.export-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background-color: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.2s;
}

.export-button:hover {
  background-color: #f9fafb;
}

.export-button:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(209, 213, 219, 0.5);
}

/* No Results */
.no-results {
  text-align: center;
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  padding: 48px 24px;
}

.no-results svg {
  color: #9ca3af;
  margin-bottom: 16px;
}

.no-results-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
}

.no-results-subtitle {
  font-size: 16px;
  color: #6b7280;
  margin-bottom: 24px;
}

.clear-button {
  padding: 10px 20px;
  background-color: #4f46e5;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.clear-button:hover {
  background-color: #4338ca;
}

.clear-button:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.4);
}

/* Results Table */
.results-table-container {
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.table-wrapper {
  overflow-x: auto;
}

.results-table {
  width: 100%;
  border-collapse: collapse;
}

.results-table th {
  background-color: #f9fafb;
  padding: 12px 24px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #e5e7eb;
}

.results-table td {
  padding: 16px 24px;
  font-size: 14px;
  color: #4b5563;
  border-bottom: 1px solid #e5e7eb;
  white-space: nowrap;
}

.results-table tbody tr:hover {
  background-color: #f9fafb;
}

/* Pagination */
.pagination {
  padding: 16px 24px;
  border-top: 1px solid #e5e7eb;
}

.pagination-mobile {
  display: flex;
  justify-content: space-between;
}

.pagination-desktop {
  display: none;
  justify-content: space-between;
  align-items: center;
}

@media (min-width: 640px) {
  .pagination-mobile {
    display: none;
  }
  .pagination-desktop {
    display: flex;
  }
}

.pagination-button {
  padding: 8px 16px;
  background-color: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-button:hover {
  background-color: #f9fafb;
}

.pagination-info {
  font-size: 14px;
  color: #6b7280;
}

.pagination-info span {
  font-weight: 600;
  color: #4b5563;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pagination-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background-color: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-arrow:hover {
  background-color: #f9fafb;
}

.pagination-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background-color: white;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-number:hover {
  background-color: #f9fafb;
}

.pagination-number.active {
  background-color: #4f46e5;
  border-color: #4f46e5;
  color: white;
}

/* Loading State */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 0;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 3px solid rgba(79, 70, 229, 0.2);
  border-radius: 50%;
  border-top-color: #4f46e5;
  animation: spin 1s linear infinite;
  margin-bottom: 24px;
}

.loading-title {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
}

.loading-subtitle {
  font-size: 14px;
  color: #6b7280;
}

/* Footer */
.app-footer {
  background-color: #1f2937;
  color: white;
  padding: 24px 0;
  margin-top: 48px;
}

.footer-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

@media (min-width: 768px) {
  .footer-content {
    flex-direction: row;
    justify-content: space-between;
    text-align: left;
  }
}

.footer-copyright {
  font-size: 14px;
  color: #d1d5db;
  margin-bottom: 16px;
}

@media (min-width: 768px) {
  .footer-copyright {
    margin-bottom: 0;
  }
}

.footer-links {
  display: flex;
  gap: 16px;
}

.footer-links a {
  color: #d1d5db;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.2s;
}

.footer-links a:hover {
  color: white;
}
</style>