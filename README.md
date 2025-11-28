# Lab05S01 — Desenho e Preparação do Experimento

**Disciplina:** Laboratório de Experimentação de Software  
**Curso:** Engenharia de Software  
**Tema:** Comparação de Desempenho entre APIs REST e GraphQL  
**Professor:** João Paulo Carneiro Aramuni  
**Entrega:** Sprint 01 - Passos 1 e 2  
**Valor:** 5 pontos

---

## 1. Introdução

Este documento apresenta o desenho experimental e a preparação de um estudo controlado que visa comparar quantitativamente o desempenho de duas abordagens distintas para construção de APIs Web: **REST** (Representational State Transfer) e **GraphQL**.

GraphQL é uma linguagem de consulta e manipulação de dados desenvolvida pelo Facebook, que permite aos clientes especificarem exatamente quais dados necessitam, estruturando consultas de forma flexível e eficiente. Em contraste, APIs REST utilizam endpoints fixos que retornam conjuntos pré-definidos de dados, frequentemente resultando em over-fetching (retorno de dados desnecessários) ou under-fetching (necessidade de múltiplas requisições).

A motivação deste experimento surge da necessidade de evidências quantitativas sobre os benefícios práticos do GraphQL, especialmente em cenários onde clientes necessitam apenas de subconjuntos específicos dos atributos de um recurso. A hipótese central é que GraphQL, ao permitir consultas mais granulares, resultará em menor tempo de resposta e menor volume de dados transferidos.

O escopo desta primeira entrega compreende exclusivamente o **desenho metodológico** do experimento e a **preparação de todos os artefatos necessários** para coleta de dados, sem ainda executar o experimento ou realizar análises estatísticas.

---

## 2. Questões de Pesquisa (Research Questions)

O experimento foi desenhado para responder às seguintes questões de pesquisa:

**RQ1:** As requisições realizadas por meio de GraphQL apresentam tempo de resposta inferior ao de requisições REST equivalentes?

**RQ2:** O tamanho das respostas retornadas por GraphQL é menor do que o tamanho das respostas retornadas por REST?

Estas questões direcionam todo o desenho experimental, desde a definição de variáveis até a escolha dos tratamentos e objetos experimentais.

---

## 3. Hipóteses Estatísticas

Para cada questão de pesquisa, formulamos hipóteses estatísticas que serão testadas na fase de análise.

### 3.1 Hipóteses para RQ1 (Tempo de Resposta)

**H₀_tempo:** μ_GraphQL ≥ μ_REST  
(A média do tempo de resposta do GraphQL é maior ou igual à média do tempo de resposta do REST)

**H₁_tempo:** μ_GraphQL < μ_REST  
(A média do tempo de resposta do GraphQL é menor que a média do tempo de resposta do REST)

### 3.2 Hipóteses para RQ2 (Tamanho da Resposta)

**H₀_tamanho:** μ_GraphQL ≥ μ_REST  
(O tamanho médio da resposta do GraphQL é maior ou igual ao tamanho médio da resposta do REST)

**H₁_tamanho:** μ_GraphQL < μ_REST  
(O tamanho médio da resposta do GraphQL é menor que o tamanho médio da resposta do REST)

Ambas as hipóteses alternativas são **direcionais** (unilaterais), refletindo a expectativa teórica de que GraphQL oferece vantagens em eficiência quando comparado ao REST em cenários de consultas parciais.

---

## 4. Variáveis do Estudo

### 4.1 Variável Independente (Fator Experimental)

**Tipo de API:** Variável categórica com dois níveis
- `REST` — Consulta via endpoint REST tradicional
- `GraphQL` — Consulta via query GraphQL

Esta é a variável que será manipulada no experimento para observar seu efeito nas variáveis dependentes.

### 4.2 Variáveis Dependentes (Métricas de Resposta)

**1. Tempo de Resposta (ms)**
- **Definição:** Duração total da requisição HTTP medida pelo cliente, desde o envio da requisição até o recebimento completo da resposta
- **Unidade:** Milissegundos (ms)
- **Método de coleta:** Timestamp antes e depois da requisição
- **Justificativa:** Tempo de resposta é uma métrica crítica de desempenho percebido pelo usuário

**2. Tamanho da Resposta (bytes)**
- **Definição:** Quantidade total de bytes recebidos no corpo (body) da resposta HTTP
- **Unidade:** Bytes
- **Método de coleta:** Medição do tamanho do conteúdo retornado via `len(response.content)`
- **Justificativa:** Menor volume de dados transferidos implica em menor consumo de banda e melhor eficiência de rede

### 4.3 Variáveis de Controle

Para garantir validade interna, as seguintes variáveis serão mantidas constantes:

- **Ambiente de execução:** Mesma máquina, mesma conexão de rede
- **Horário de execução:** Medições realizadas em sequência, minimizando variações temporais
- **Dados consultados:** Mesmos IDs de personagens em ambos os tratamentos
- **Bibliotecas e versões:** Versões fixas de Python e dependências (especificadas em `requirements.txt`)

---

## 5. Tratamentos

### 5.1 Tratamento REST (T_REST)

**Descrição:** Requisição HTTP GET ao endpoint de personagem individual

**Endpoint:** `https://rickandmortyapi.com/api/character/{id}`

**Método HTTP:** GET

**Características:**
- Retorna o objeto completo do personagem com todos os atributos disponíveis
- Estrutura de resposta fixa e não personalizável
- Inclui atributos como: `id`, `name`, `status`, `species`, `type`, `gender`, `origin`, `location`, `image`, `episode`, `url`, `created`

**Exemplo de uso:**
```http
GET https://rickandmortyapi.com/api/character/1
```

### 5.2 Tratamento GraphQL (T_GraphQL)

**Descrição:** Requisição HTTP POST com query GraphQL solicitando campos específicos

**Endpoint:** `https://rickandmortyapi.com/graphql`

**Método HTTP:** POST

**Query utilizada:**
```graphql
query {
  character(id: {id}) {
    name
    species
    status
  }
}
```

**Características:**
- Solicita apenas três campos específicos: `name`, `species`, `status`
- Resposta contém apenas os dados requisitados
- Representa um cenário comum de consulta parcial

**Exemplo de payload:**
```json
{
  "query": "query { character(id: 1) { name species status } }"
}
```

**Justificativa da escolha dos campos:**
Os três campos selecionados (`name`, `species`, `status`) representam aproximadamente 25% dos atributos disponíveis, simulando um cenário realista onde o cliente necessita apenas de informações básicas sobre o personagem.

---

## 6. Objetos Experimentais

### 6.1 API Utilizada

**Nome:** Rick and Morty API  
**Documentação:** https://rickandmortyapi.com/documentation  
**Versão:** v1 (atual)

**Justificativa da escolha:**
- Oferece implementações equivalentes e bem documentadas de REST e GraphQL
- API pública, estável e amplamente utilizada
- Estrutura de dados consistente e bem definida
- Não requer autenticação, simplificando a implementação
- Dados representativos para o cenário experimental (múltiplos atributos por recurso)

### 6.2 Amostra de Personagens

**Tamanho da amostra:** 50 personagens  
**Critério de seleção:** Primeiros 50 IDs sequenciais (1 a 50)  
**Tipo de amostragem:** Amostragem de conveniência sequencial

**Justificativa do tamanho amostral:**
- N=50 fornece poder estatístico adequado para testes paramétricos
- Quantidade suficiente para observar padrões consistentes
- Viável em termos de tempo de execução
- Minimiza risco de rate limiting da API

**IDs selecionados:** 1, 2, 3, ..., 50

---

## 7. Tipo de Projeto Experimental

### 7.1 Classificação do Desenho

**Tipo:** Experimento Controlado com **Desenho Pareado (Paired Design)**

**Características:**
- Cada objeto experimental (ID de personagem) é submetido a ambos os tratamentos
- Medições REST e GraphQL são realizadas para o mesmo ID
- Reduz variabilidade entre sujeitos, aumentando poder estatístico

### 7.2 Estrutura de Pareamento

Para cada ID *i* (onde i ∈ {1, 2, ..., 50}):
1. Executa requisição REST para personagem *i*
2. Registra tempo_REST(i) e tamanho_REST(i)
3. Executa requisição GraphQL para personagem *i*
4. Registra tempo_GraphQL(i) e tamanho_GraphQL(i)

**Ordem de execução:**
```
REST(id=1)    → GraphQL(id=1)
REST(id=2)    → GraphQL(id=2)
REST(id=3)    → GraphQL(id=3)
...
REST(id=50)   → GraphQL(id=50)
```

**Vantagens do pareamento:**
- Controla variações individuais dos objetos (diferentes personagens podem ter tamanhos naturalmente diferentes)
- Permite análise estatística mais sensível (testes pareados)
- Reduz variância residual

### 7.3 Caracterização quanto ao Ambiente

**Categoria:** Experimento **in vitro**

**Justificativa:**
- Executado em ambiente totalmente controlado
- Sem interação com usuários reais
- Condições experimentais artificiais mas replicáveis
- Foco em medições objetivas de desempenho

---

## 8. Quantidade de Medições

### 8.1 Estrutura das Medições

**Número de objetos experimentais:** 50 personagens

**Tratamentos por objeto:** 2 (REST e GraphQL)

**Total de medições planejadas:** 50 × 2 = **100 requisições**

### 8.2 Fase de Warm-up

**Objetivo:** Estabilizar conexões iniciais e cache de DNS/TCP

**Procedimento:**
- 5 requisições REST de aquecimento (IDs aleatórios fora da amostra)
- 5 requisições GraphQL de aquecimento (IDs aleatórios fora da amostra)
- Resultados descartados, não incluídos na análise

**Justificativa:**
Elimina efeitos de "cold start" que poderiam enviesar as primeiras medições, garantindo que todas as 100 medições experimentais ocorram em condições estáveis.

### 8.3 Estratégia de Repetição

Neste experimento, **não haverá repetições** (cada combinação ID × Tratamento medida uma vez).

**Justificativa:**
- Desenho pareado já fornece controle adequado
- API pública pode ter rate limiting
- Foco em comparação entre tratamentos, não em variabilidade temporal
- 50 pares fornecem poder estatístico suficiente

**Nota:** Se análise preliminar indicar alta variabilidade, repetições poderão ser consideradas em extensões futuras do estudo.

---

## 9. Ameaças à Validade

### 9.1 Validade Interna

**Ameaça 1: Oscilações na latência de rede**

*Descrição:* Variações momentâneas na velocidade da conexão podem afetar tempos de resposta independentemente do tratamento.

*Mitigação:*
- Desenho pareado: medições REST e GraphQL para o mesmo ID ocorrem em sequência, minimizando impacto de flutuações temporais
- Alternância de tratamentos: evita que todos os testes REST ocorram antes de todos os GraphQL
- Execução em horário estável: evitar horários de pico de tráfego

**Ameaça 2: Cold start e cache**

*Descrição:* Primeiras requisições podem ser mais lentas devido ao estabelecimento de conexões TCP/TLS.

*Mitigação:*
- Fase de warm-up com 10 requisições antes da coleta experimental
- Mantém conexões abertas quando possível (keep-alive)

**Ameaça 3: Efeitos de ordem**

*Descrição:* Realizar sempre REST antes de GraphQL poderia introduzir viés sistemático.

*Mitigação:*
- Embora a ordem REST→GraphQL seja mantida para facilitar análise pareada, o pareamento por ID atenua este risco
- Alternativa: randomização futura se necessário

### 9.2 Validade de Construto

**Ameaça 1: Medição do tempo de resposta**

*Descrição:* Tempo medido pode incluir overhead do código Python além do tempo real de I/O de rede.

*Mitigação:*
- Uso da biblioteca `requests` com medições de timestamp imediatamente antes e depois da chamada
- Overhead é constante entre tratamentos, não afeta comparação relativa
- Foco em tempo de resposta do cliente (métrica relevante para usuários finais)

**Ameaça 2: Definição de "tamanho da resposta"**

*Descrição:* Tamanho pode variar dependendo de headers HTTP, compressão, etc.

*Mitigação:*
- Medição consistente: `len(response.content)` captura tamanho do body descomprimido
- Mesma biblioteca e configurações para ambos os tratamentos

### 9.3 Validade de Conclusão Estatística

**Ameaça 1: Violação de premissas estatísticas**

*Descrição:* Testes paramétricos assumem normalidade; outliers podem distorcer resultados.

*Mitigação:*
- Análise exploratória dos dados antes de testes (Sprint 2)
- Verificação de normalidade com testes apropriados
- Uso de testes não-paramétricos se premissas violadas
- Identificação e tratamento de outliers

**Ameaça 2: Tamanho amostral insuficiente**

*Descrição:* N=50 pode não detectar diferenças pequenas.

*Mitigação:*
- Cálculo de poder estatístico na análise (Sprint 2)
- Tamanho escolhido baseado em convenções da área
- Foco em diferenças de magnitude prática, não apenas estatística

### 9.4 Validade Externa

**Ameaça 1: Generalização para outras APIs**

*Descrição:* Resultados são específicos da implementação da Rick and Morty API.

*Mitigação:*
- Reconhecimento explícito desta limitação
- API escolhida é representativa de casos reais
- Resultados informam sobre o potencial da tecnologia, não garantem comportamento universal

**Ameaça 2: Cenário de consulta específico**

*Descrição:* Query GraphQL solicita apenas 3 de 12+ campos; resultados podem diferir com outras proporções.

*Mitigação:*
- Escolha representa cenário comum e relevante
- Documentação clara do cenário avaliado
- Futuras extensões podem explorar diferentes proporções de campos

---

## 10. Preparação do Ambiente de Execução

### 10.1 Requisitos de Sistema

**Sistema Operacional:** Qualquer SO compatível com Python 3.10+  
(Windows, Linux, macOS)

**Linguagem de Programação:** Python 3.10 ou superior

**Bibliotecas Python necessárias:**
- `requests` — Para requisições HTTP
- `pandas` — Para estruturação e exportação de dados
- `time` — Para medições de tempo (biblioteca padrão)

### 10.2 Instalação das Dependências

**Passo 1:** Certifique-se de ter Python 3.10+ instalado
```bash
python --version
```

**Passo 2:** Instale as dependências listadas em `requirements.txt`
```bash
pip install -r requirements.txt
```

**Conteúdo do arquivo `requirements.txt`:**
```
requests==2.31.0
pandas==2.1.0
```

### 10.3 Estrutura de Arquivos do Projeto

```
lab05-graphql-rest/
│
├── README.md                    # Este documento
├── requirements.txt             # Dependências Python
├── experiment.py                # Script de coleta de dados
└── experiment_results.csv       # Dados coletados (gerado após execução)
```

### 10.4 Execução do Script de Coleta

**Comando básico:**
```bash
python experiment.py --start 1 --end 50 --out experiment_results.csv
```

**Parâmetros:**
- `--start`: ID inicial do intervalo de personagens (padrão: 1)
- `--end`: ID final do intervalo de personagens (padrão: 50)
- `--out`: Nome do arquivo CSV de saída (padrão: experiment_results.csv)

**Exemplo de uso alternativo:**
```bash
# Testar com amostra menor
python experiment.py --start 1 --end 10 --out test_results.csv
```

### 10.5 Descrição Detalhada do Script `experiment.py`

O script está organizado nas seguintes seções:

#### a) Importações e Configuração
```python
import requests
import time
import pandas as pd
import argparse
```

#### b) Funções de Requisição

**`make_rest_request(character_id)`**
- Realiza requisição GET ao endpoint REST
- Retorna tempo de resposta (ms) e tamanho da resposta (bytes)
- Trata erros HTTP apropriadamente

**`make_graphql_request(character_id)`**
- Constrói query GraphQL com os campos especificados
- Realiza requisição POST ao endpoint GraphQL
- Retorna tempo de resposta (ms) e tamanho da resposta (bytes)
- Trata erros HTTP apropriadamente

#### c) Fase de Warm-up

**`warmup()`**
- Executa 5 requisições REST com IDs aleatórios (51-100)
- Executa 5 requisições GraphQL com IDs aleatórios (51-100)
- Descarta resultados
- Exibe progresso no console

#### d) Coleta Principal

**`run_experiment(start_id, end_id)`**
- Itera sobre IDs de `start_id` até `end_id`
- Para cada ID:
  - Realiza requisição REST
  - Registra tempo_ms e tamanho_bytes
  - Realiza requisição GraphQL
  - Registra tempo_ms e tamanho_bytes
- Armazena resultados em lista de dicionários
- Exibe progresso (ex: "Processando ID 1/50...")

#### e) Armazenamento de Dados

**`save_results(results, output_file)`**
- Converte lista de resultados em DataFrame pandas
- Salva como CSV com as colunas:
  - `id` — ID do personagem
  - `type` — Tipo de API (REST ou GraphQL)
  - `time_ms` — Tempo de resposta em milissegundos
  - `size_bytes` — Tamanho da resposta em bytes
- Encoding UTF-8 para compatibilidade

#### f) Função Principal

**`main()`**
- Processa argumentos da linha de comando
- Executa warm-up
- Executa coleta experimental
- Salva resultados
- Exibe mensagem de conclusão

### 10.6 Formato dos Dados de Saída

**Arquivo:** `experiment_results.csv`

**Estrutura:**
```csv
id,type,time_ms,size_bytes
1,REST,245.3,1834
1,GraphQL,198.7,412
2,REST,251.1,1902
2,GraphQL,203.4,398
...
50,REST,239.8,1845
50,GraphQL,195.2,405
```

**Descrição das colunas:**
- `id` (int): Identificador do personagem consultado
- `type` (string): "REST" ou "GraphQL"
- `time_ms` (float): Tempo de resposta em milissegundos
- `size_bytes` (int): Tamanho da resposta em bytes

**Total de linhas esperadas:** 101 (header + 100 medições)

---

## 11. Protocolo de Execução do Experimento

Esta seção documenta o protocolo detalhado que deverá ser seguido na Sprint 02 (execução).

### 11.1 Pré-condições

Antes de iniciar a coleta de dados:

✓ Ambiente Python configurado corretamente  
✓ Dependências instaladas (`pip install -r requirements.txt`)  
✓ Conexão estável à internet  
✓ Verificar disponibilidade da Rick and Morty API  
✓ Espaço em disco suficiente para arquivo CSV  

### 11.2 Procedimento de Execução

**Passo 1:** Verificar conectividade
```bash
# Teste manual
curl https://rickandmortyapi.com/api/character/1
```

**Passo 2:** Executar warm-up e coleta
```bash
python experiment.py --start 1 --end 50 --out experiment_results.csv
```

**Passo 3:** Aguardar conclusão
- Tempo estimado: 3-5 minutos
- Não interromper o processo

**Passo 4:** Validar arquivo de saída
- Verificar existência de `experiment_results.csv`
- Conferir número de linhas (deve ser 101)
- Inspecionar visualmente primeiras linhas

### 11.3 Critérios de Aceitação dos Dados

Os dados coletados serão considerados válidos se:

✓ Todas as 100 requisições foram bem-sucedidas (status HTTP 200)  
✓ Nenhum valor de tempo ou tamanho é nulo  
✓ Tempos de resposta estão dentro de faixa razoável (ex: 50ms - 5000ms)  
✓ Tamanhos de resposta são coerentes (REST > GraphQL na maioria dos casos)  

### 11.4 Tratamento de Erros

**Se houver falhas de rede:**
- Aguardar 5 minutos e tentar novamente
- Verificar firewall e proxy
- Considerar horário alternativo se instabilidade persistir

**Se houver rate limiting (erro HTTP 429):**
- Adicionar delay entre requisições no script
- Reduzir tamanho da amostra temporariamente
- Executar em horários de menor carga

---

## 12. Cronograma de Entregas

### Sprint 01 (Atual) - Lab05S01
**Objetivo:** Desenho e Preparação  
**Entregáveis:**
- ✓ Documento de desenho experimental (este README.md)
- ✓ Script `experiment.py` implementado e testado
- ✓ Arquivo `requirements.txt`

**Valor:** 5 pontos  
**Status:** Em desenvolvimento

### Sprint 02 - Lab05S02
**Objetivo:** Execução e Análise  
**Entregáveis planejados:**
- Arquivo `experiment_results.csv` com dados coletados
- Análise estatística dos resultados (testes de hipótese)
- Relatório final com metodologia, resultados e discussão

**Valor:** 10 pontos

### Sprint 03 - Lab05S03
**Objetivo:** Dashboard de Visualização  
**Entregáveis planejados:**
- Dashboard interativo com gráficos e tabelas
- Comparações visuais entre REST e GraphQL
- Exportação de visualizações

**Valor:** 5 pontos

---

## 13. Considerações Éticas e de Reprodutibilidade

### 13.1 Uso Responsável da API

Este experimento utiliza a Rick and Morty API, um serviço público e gratuito. Para garantir uso ético:

- **Respeito aos termos de uso:** Seguimos diretrizes de fair use
- **Limitação de requisições:** Total de ~110 requisições (warm-up + experimento)
- **Horário adequado:** Evitamos horários de pico quando possível
- **Não sobrecarregar o serviço:** Intervalo natural entre requisições

### 13.2 Reprodutibilidade

Este experimento foi desenhado para máxima reprodutibilidade:

**Elementos que favorecem reprodução:**
- ✓ Documentação completa de todos os parâmetros
- ✓ Script automatizado com versões fixas de dependências
- ✓ API pública sem necessidade de autenticação
- ✓ Protocolo de execução detalhado
- ✓ Dados brutos serão disponibilizados

**Elementos que podem afetar replicação:**
- Variações na implementação da API ao longo do tempo
- Diferenças de latência geográfica e de provedor de internet
- Eventuais mudanças na estrutura de dados da API

**Recomendações para replicadores:**
- Documentar localização geográfica e provedor de internet
- Executar em horários similares (evitar picos)
- Reportar quaisquer diferenças observadas na API

---

## 14. Limitações Conhecidas do Estudo

### 14.1 Escopo Restrito

- **Uma única API:** Resultados específicos da Rick and Morty API
- **Um cenário de consulta:** Apenas consultas de leitura com subset de campos
- **Métrica limitada:** Não avalia complexidade de implementação, facilidade de manutenção, ou outros fatores qualitativos

### 14.2 Fatores Não Controlados

- **Implementação do servidor:** Não temos controle sobre como REST e GraphQL estão implementados no backend
- **Cache do servidor:** Não sabemos se há cache entre nosso requests
- **Infraestrutura de rede:** Roteamento, CDN e outros fatores intermediários

### 14.3 Validade Externa

Os resultados **NÃO podem ser generalizados** para:
- Outras implementações de APIs REST ou GraphQL
- Consultas mais complexas (queries aninhadas, múltiplos recursos)
- Operações de escrita (mutations)
- APIs com autenticação e autorização
- Cenários de alta concorrência

### 14.4 Implicações

Este estudo fornece evidências quantitativas para **um cenário específico**, contribuindo para o corpo de conhecimento sobre REST vs GraphQL, mas não deve ser interpretado como prova definitiva da superioridade de uma tecnologia sobre a outra em todos os contextos.

---

## 15. Referências e Recursos Adicionais

### 15.1 Documentação das Tecnologias

- **GraphQL Official:** https://graphql.org/
- **REST API Design:** https://restfulapi.net/
- **Rick and Morty API Docs:** https://rickandmortyapi.com/documentation

### 15.2 Bibliotecas Utilizadas

- **Requests:** https://docs.python-requests.org/
- **Pandas:** https://pandas.pydata.org/docs/

### 15.3 Referências Metodológicas

- Wohlin, C. et al. (2012). *Experimentation in Software Engineering*. Springer.
- Juristo, N., & Moreno, A. M. (2001). *Basics of Software Engineering Experimentation*. Springer.

---

## 16. Conclusão

Este documento apresentou o desenho completo e a preparação de um experimento controlado para comparar o desempenho de APIs REST e GraphQL. Foram definidos:

✓ Questões de pesquisa claras e objetivas  
✓ Hipóteses estatísticas testáveis  
✓ Variáveis dependentes e independentes bem especificadas  
✓ Tratamentos equivalentes e comparáveis  
✓ Objetos experimentais apropriados  
✓ Desenho experimental pareado robusto  
✓ Protocolo de coleta detalhado e automatizado  
✓ Ameaças à validade identificadas e mitigadas  

O experimento está **pronto para execução** na Sprint 02. Todos os artefatos necessários foram desenvolvidos e documentados, garantindo que a coleta de dados possa ser realizada de forma sistemática, confiável e reprodutível.

Os resultados obtidos contribuirão para uma compreensão quantitativa das diferenças de desempenho entre REST e GraphQL em cenários de consultas parciais, fornecendo evidências empíricas para informar decisões de arquitetura de software.

---

**Versão do documento:** 1.0  
**Data:** 28 de novembro de 2025  
**Autores:** [Incluir nomes dos integrantes do grupo]  
**Curso:** Engenharia de Software  
**Instituição:** [Incluir nome da instituição]
