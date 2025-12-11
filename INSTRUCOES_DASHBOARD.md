# 📊 Instruções de Uso - Dashboard REST vs GraphQL

## Pré-requisitos

- Python 3.10 ou superior
- Conexão com a internet (para instalação de pacotes)

## Instalação

### 1. Instalar dependências

```bash
pip install -r src/requirements.txt
```

**Nota:** Se houver problemas com a instalação do pandas, tente:

```bash
pip install requests pandas streamlit plotly scipy numpy
```

### 2. Verificar instalação

Certifique-se de que o arquivo `src/experiment_results.csv` existe no diretório.

## Execução

### Iniciar o Dashboard

```bash
streamlit run src/dashboard.py
```

O dashboard será aberto automaticamente no seu navegador em:

**http://localhost:8501**

Se não abrir automaticamente, copie e cole o endereço acima no seu navegador.

## Navegação

O dashboard possui 4 páginas principais acessíveis pela barra lateral:

1. **Visão Geral** - Métricas principais e comparações gerais
2. **Análise de Tempo (RQ1)** - Análise detalhada do tempo de resposta
3. **Análise de Tamanho (RQ2)** - Análise detalhada do tamanho da resposta
4. **Análise Detalhada** - Dados filtrados e exportação

## Funcionalidades

- ✅ Gráficos interativos (zoom, pan, hover)
- ✅ Testes estatísticos automáticos
- ✅ Filtros por ID e tipo de API
- ✅ Exportação de dados em CSV
- ✅ Interpretação automática dos resultados

## Parar o Dashboard

Pressione `Ctrl + C` no terminal onde o dashboard está rodando.

## Solução de Problemas

### Erro: "Arquivo não encontrado"
- Verifique se `src/experiment_results.csv` existe
- Execute o script `experimet.py` primeiro para gerar os dados

### Erro: "Module not found"
- Execute: `pip install -r src/requirements.txt`
- Ou instale manualmente: `pip install streamlit plotly scipy numpy pandas requests`

### Porta 8501 já em uso
- O Streamlit tentará usar a próxima porta disponível (8502, 8503, etc.)
- Verifique a mensagem no terminal para o endereço correto

## Estrutura de Arquivos

```
GraphQL-vs-Rest/
├── src/
│   ├── dashboard.py              # Script do dashboard
│   ├── experiment_results.csv   # Dados do experimento
│   └── requirements.txt          # Dependências
└── INSTRUCOES_DASHBOARD.md       # Este arquivo
```

