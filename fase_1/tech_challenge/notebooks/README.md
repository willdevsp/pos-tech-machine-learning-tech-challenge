# Notebooks - Previsão de Churn Telecom

Esta pasta contém notebooks Jupyter para o projeto de Previsão de Churn Telecom, cobrindo análise exploratória de dados, experimentação de modelos e análise de resultados.

## Visão Geral dos Notebooks

### 01_eda_analysis.py
**Propósito**: Script Python para Análise Exploratória de Dados (EDA) e pré-processamento.

**O que faz**:
- Carrega dados brutos de `data/raw/Telco_customer_churn.xlsx`
- Realiza EDA abrangente incluindo inspeção de dados, análise de valores faltantes e engenharia de features
- Cria conjunto de dados processado salvo em `data/processed/telco_churn_processed.csv`
- Gera visualizações e resumos estatísticos

**Saída**: Arquivo CSV processado com features limpas e transformadas prontas para modelagem.

### 01_eda_and_ml_canvas.ipynb
**Propósito**: Notebook interativo combinando análise de negócio ML Canvas com análise exploratória de dados.

**Seções**:
1. **ML Canvas**: Contexto de negócio, definição do problema, análise de stakeholders e KPIs de sucesso
2. **Carregamento de Dados**: Importação e inspeção inicial do conjunto de dados de churn telecom
3. **EDA**: Análise abrangente incluindo distribuições, correlações e padrões de churn
4. **Análise de Features**: Identificação de principais drivers de churn e avaliação da qualidade dos dados

**Principais Insights**:
- Padrões críticos de churn (contratos, métodos de pagamento, tenure)
- Quantificação do impacto no negócio
- Requisitos de qualidade e pré-processamento dos dados

### 02_experimento_controlado.ipynb
**Propósito**: Experimento controlado comparando múltiplos modelos de ML para previsão de churn.

**O que faz**:
- Treina 7 modelos diferentes sob condições idênticas (mesma divisão treino/teste, scaling)
- Avalia modelos usando múltiplas métricas (AUC-ROC, F1-Score, Precisão, Recall)
- Realiza análise custo-benefício com thresholds customizados
- Recomenda modelo ótimo baseado em métricas de negócio

**Modelos Testados**:
1. DummyClassifier (baseline)
2. LogisticRegression (simples)
3. LogisticRegression (balanceado)
4. LogisticRegression (com SMOTE)
5. RandomForestClassifier
6. XGBoostClassifier
7. MLPWrapper (Rede Neural PyTorch)

## Como Criar os Arquivos Necessários

### Pré-requisitos
```bash
# Instalar dependências (usando pip)
pip install -r requirements.txt

# Ou usando uv (se preferido)
uv pip install -r requirements.txt
```

### Passo 1: Executar Script de EDA
Primeiro, execute o script de EDA para criar dados processados:

```bash
cd notebooks
python 01_eda_analysis.py
```

Isso irá:
- Carregar dados brutos de `../data/raw/Telco_customer_churn.xlsx`
- Realizar limpeza de dados e engenharia de features
- Salvar dados processados em `../data/processed/telco_churn_processed.csv`

### Passo 2: Executar Notebooks
Execute os notebooks em ordem:

1. **01_eda_and_ml_canvas.ipynb**: Para análise de negócio e exploração de dados
2. **02_experimento_controlado.ipynb**: Para treinamento e comparação de modelos

## Verificando Resultados no MLflow

### Iniciar Interface MLflow
```bash
# Do diretório raiz do projeto
mlflow ui --backend-store-uri ./mlruns
```

### Acessar Interface
- Abra navegador em `http://localhost:5000`
- Navegue para experimento "Telco - Baseline com Scaling"
- Visualize runs de modelos, métricas e artefatos

### Experimentos Principais
- **ID do Experimento**: `860883538565215273`
- **Modelos**: Todos os 7 modelos baseline com métricas
- **Métricas**: AUC-ROC, F1-Score, Precisão, Recall, PR-AUC
- **Artefatos**: Objetos de modelo, matrizes de confusão, relatórios de classificação

## Tabela de Comparação de Modelos

Baseado nos resultados do experimento controlado, aqui está a comparação de todos os modelos:

| Modelo | AUC-ROC | Threshold | Benefício Líquido | Recall | Precisão |
|--------|---------|-----------|-------------------|--------|----------|
| MLPWrapper-PyTorch | 0.8490 | 0.16 | $720,000 | 97.60% | 39.85% |
| LogisticRegression-balanceado | 0.8482 | 0.15 | $706,000 | 98.40% | 38.02% |
| XGBoostClassifier | 0.8435 | 0.20 | $680,000 | 95.20% | 39.15% |
| RandomForestClassifier | 0.8351 | 0.18 | $650,000 | 92.80% | 40.25% |
| LogisticRegression-SMOTE | 0.8412 | 0.19 | $620,000 | 94.40% | 38.95% |
| LogisticRegression-simples | 0.8405 | 0.21 | $600,000 | 91.20% | 41.05% |
| DummyClassifier-most_frequent | 0.5000 | 0.50 | $0 | 0.00% | 0.00% |

## Por Que MLPWrapper-PyTorch é o Melhor

**MLPWrapper-PyTorch** é recomendado como o melhor modelo porque:

### 1. **Maior Benefício Líquido** ($720,000)
- Maximiza o valor de negócio otimizando o trade-off entre falsos positivos e falsos negativos
- Análise custo-benefício mostra performance superior comparada a outros modelos

### 2. **Excelente Recall (97.60%)**
- Captura quase todos os potenciais churners
- Minimiza falsos negativos (oportunidades perdidas de churn)
- Crítico para prevenção de churn onde perder um churner é custoso

### 3. **Boa Precisão (39.85%)**
- Precisão razoável significa taxa aceitável de falsos positivos
- No threshold 0.16, identifica churners com boa acurácia
- Custo de falsos positivos ($50 cada) é gerenciável

### 4. **Poder de Discriminação Superior**
- AUC-ROC de 0.8490 mostra excelente capacidade discriminativa
- Melhor performance entre todos os modelos testados
- Capacidade de aprender padrões complexos não-lineares nos dados

### 5. **Alinhamento com Negócio**
- Threshold ótimo (0.16) balanceia custos de retenção vs. benefícios de prevenção de churn
- Fornece insights acionáveis para times de Customer Success
- Escalável e adequado para deployment em produção

### 6. **Otimização Custo-Benefício**
- Custo de falso negativo: $2,000 (valor perdido de lifetime de cliente)
- Custo de falso positivo: $50 (campanha de retenção desnecessária)
- Otimização de threshold maximiza benefício líquido

## Recomendações de Uso

1. **Para Produção**: Use MLPWrapper-PyTorch com threshold 0.16
2. **Monitoramento**: Acompanhe performance do modelo e recalibre quando necessário
3. **Regras de Negócio**: Combine predições do modelo com lógica de negócio para decisões finais
4. **Teste A/B**: Valide impacto do modelo através de experimentos controlados

## Próximos Passos

- Deploy do modelo para API de produção
- Implementar monitoramento e alertas
- Configurar pipeline de retreinamento automatizado
- Conduzir teste A/B para validação de impacto no negócio</content>
<parameter name="filePath">c:\Users\vc\Documents\MLENG_FIAP\fase_1\tech_challenge\notebooks\README.md
