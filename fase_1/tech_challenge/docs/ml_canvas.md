# ML Canvas - Previsão de Churn Telecomunicações

## 1. Entendimento de Negócio e Formulação

### Contexto do Projeto
Uma operadora de telecomunicações está perdendo clientes em ritmo acelerado. A diretoria necessita um modelo preditivo de churn para classificar clientes com risco de cancelamento, permitindo ações proativas de retenção.

---

## ML Canvas

### 1. **Proposta de Valor**
> Implementar um **sistema de alerta precoce** que identifique clientes com alta propensão ao cancelamento, permitindo que o time de Customer Success atue de forma personalizada antes do encerramento do contrato.

**Benefício Direto**: Redução de perda de receita mensal (MRR) e aumento do Lifetime Value (LTV) dos clientes.

---

### 2. **Atores de Negócio (Stakeholders)**

| Ator | Responsabilidade | Impacto |
|------|------------------|--------|
| **Marketing** | Criação de campanhas de retenção segmentadas | Otimizar orçamento de retenção |
| **Financeiro** | Controle do impacto no MRR (Monthly Recurring Revenue) | Prever receita e impacto de churn |
| **Customer Success** | Ação de retenção personalizada (ofertas, upgrades) | Aumentar taxa de retenção |
| **Engenharia de ML / Data** | Manutenção da robustez, precisão e monitoramento do modelo | Garantir performance e confiabilidade |
| **CTO / Operações** | Governança, compliance e segurança | Garantir aderência a regulamentos |

---

### 3. **Métricas de Sucesso (KPIs)**

#### **Negócio**

- **Redução de Churn Trimestral: 10%**
  - **Base Atual (EDA)**: 26.5% de churn (1,869 de 7,043 clientes)
  - **Métrica**: De 26.5% → 23.85% (redução de 2.65 p.p.)
  - **Impacto**: ~263 clientes retidos/trimestre
  - **Receita Preservada**: 263 clientes × $80/mês (ticket médio) = **$21k+/trimestre**
  - **Por que 10%?** Estudos mostram modelos de churn bem executados retêm 5-15% dos casos em risco (nosso alvo é conservador e realista, não promete milagres)

- **Aumento de Lifetime Value (LTV): 15%**
  - **Cálculo**: LTV = Monthly Revenue × Average Tenure
  - **LTV Atual**: $65/mês × 32 meses (median do EDA) = $2,080
  - **LTV Esperado**: $65/mês × 37 meses (+5 meses retenção) = $2,405 (+15%)
  - **Por que 15%?** Reflete aproximadamente 5-6 meses adicionais de retenção por cliente

- **ROI da Retenção: < 25%**
  - **Lógica**: Custo de ação/cliente não pode exceder 25% da receita anual
  - **Custo Permitido**: $65/mês × 0.25 × 12 = **$195/ano/cliente**
  - **Exemplos Viáveis**: Desconto de 10-15% por 3 meses | Upgrade de serviço grátis | Crédito em conta
  - **Por que < 25%?** Benchmark telecom: ROI típico de 3:1 a 4:1 (precisamos de mínimo 4 clientes retidos por cada 1 real gasto)

- **Taxa de Conversão: 40%**
  - **Cenário**: De ~1,000 clientes alertados como alto risco
  - **Resultado Esperado**: 400 respondem às ofertas | 300 já decidiram sair | 300 ignoram
  - **Por que 40%?** Taxa típica de resposta em campanhas orientadas por ML (30-50% é padrão de mercado, não é 100% realista)

#### **Técnico**

- **F1-Score: > 0.70**
  - **Por que F1 (não acurácia)?** Com 73.5% de não-churn, modelo dummy que prevê todos como "não-churn" teria 73.5% acurácia (inútil). F1 é a média harmônica de Precision e Recall
  - **Interpretação**: F1=0.70 significa Precision ~65% (quando alerta, acerta 65%) + Recall ~80% (identifica 80% dos casos reais)
  - **Benchmark**: Baseline simples 0.40-0.50 | Modelos bons 0.65-0.75 | Estado da arte 0.80+
  - **Por que não 0.90?** Em dados reais, 0.90 geralmente indica overfitting

- **AUC-ROC: > 0.85**
  - **Significado**: Mede a capacidade do modelo discriminar entre classes (0.50=random, 0.70=bom, 0.85=muito bom, 0.95+=Kaggle)
  - **Por que 0.85?** Sweet spot realista: acima de "bom", abaixo de "provavelmente overfitting"

- **Recall (Sensibilidade): ≥ 0.80**
  - **Crítico para Churn**: Recall=0.60 significa perder 40% dos 1,869 casos reais (~749 clientes). Recall=0.80 significa reter apenas 374, capturando 1,495
  - **Racional**: Preferimos alertar alguns clientes a mais (falsos positivos baratos) do que deixar churn real passar despercebido

- **Precision: ≥ 0.65**
  - **Trade-off Consciente**: Precision=0.95 geraria muito poucas alertas (subutilizando o modelo). Precision=0.65 significa: de 100 alertas, 65 são reais, 35 são "falsos positivos"
  - **Custo-Benefício**: Custo de contato ~$5/cliente | Valor de retê-lo = $2,080 LTV | ROI = 1,495 clientes retidos × $2,080 / (3,000 alertas × $5) ≈ **410% ROI**

- **Latência da API: < 200ms**
  - **Use Case Batch**: 7,000 clientes × 200ms = 23 minutos (aceitável para rodar à noite)
  - **Use Case Real-time**: Durante atendimento, agente vê risco do cliente em tempo real (> 500ms = lento; < 200ms = transparente)

- **Disponibilidade: 99.9% uptime** (3:00 downtime/mês máximo)

---

### 4. **Requisitos Funcionais**

1. **Modelagem**
   - Rede neural (MLP) treinada com PyTorch
   - Baselines de comparação (Regressão Logística, Random Forest)
   - Validação cruzada estratificada K-fold

2. **Pipeline Reprodutível**
   - Pré-processamento automático via `sklearn.Pipeline`
   - Tratamento de dados faltantes
   - Normalização de features numéricas
   - Encoding de features categóricas

3. **API de Inferência**
   - Endpoint `/predict` para classificação individual
   - Endpoint `/health` para monitoramento
   - Validação de schema de entrada (Pydantic)
   - Resposta em tempo real (< 200ms)

4. **Rastreamento e Governança**
   - MLflow para tracking de experimentos (parâmetros, métricas, artefatos)
   - Model Card documentando performance, vieses e limitações
   - Auditoria de Fairness via Fairlearn
   - Testes automatizados (unitários, schema, smoke test)

---

### 5. **Requisitos Não-Funcionais**

- **Reprodutibilidade**: Seeds fixados, ambiente versionado, dependências explícitas em `pyproject.toml`
- **Qualidade de Código**: Linting com `ruff`, sem erros, cobertura de testes ≥ 80%
- **Escalabilidade**: API containerizada (Docker) para deploy em nuvem
- **Segurança**: Validação de entrada, logging sem PII, conformidade com regulamentações (LGPD)
- **Documentação**: README completo, Model Card, plano de monitoramento

---

### 6. **Dataset**

- **Fonte**: IBM Telco Customer Churn Dataset (público)
- **Tamanho**: ~7,000 registros de clientes
- **Features**: 20 variáveis tabulares (contrato, serviços, dados demográficos, churn)
- **Target**: Binária (Churn: Yes/No)
- **Desafio**: Desbalanceamento ~73% (Não-Churn) vs ~27% (Churn)

---

### 7. **Limitações e Cenários de Falha**

- Modelo treinado para **contexto de telecomunicações**; não é generalizável para outros setores
- Não aplicável para **clientes B2B** (modelo focado em clientes residenciais)
- Performance pode degradar se perfil demográfico mudar significativamente
- Requer **retreinamento trimestral** para adaptar a novas tendências de mercado
- Viés potencial: necessária auditoria de fairness para grupos etários e demográficos

---

### 8. **Cronograma**

| Etapa | Atividade | Duração |
|-------|-----------|---------|
| 1 | ML Canvas + EDA + Baselines + MLflow setup | 1-2 semanas |
| 2 | Modelagem MLP + Comparação de modelos | 1-2 semanas |
| 3 | Refatoração + API FastAPI + Testes | 2 semanas |
| 4 | Model Card + Deploy + Vídeo | 1 semana |

---

### 4.5 Balanceamento de Classes

**Problema**: Desbalanceamento 1:2.77 (26.5% churn vs 73.5% não-churn)

**Solução em 3 Camadas**:
1. **Class Weights**: Penalizar churn errado (pos_weight = 2.77)
2. **SMOTE**: Gerar amostras sintéticas de churn no treino
3. **Stratified K-Fold**: Manter distribuição em cada fold

**Implementação**:
- Baseline: Class Weights alone → esperado F1 ~0.65
- MLP: Class Weights + SMOTE → esperado F1 ~0.72+

---

## Próximas Etapas

✅ **Etapa 1 Completa**: ML Canvas definido
→ **Etapa 2**: Exploração exploratória de dados (EDA) em andamento
→ **Etapa 3**: Baseline com DummyClassifier e Regressão Logística
→ **Etapa 4**: Treinar MLP com PyTorch

---

**Versão**: 1.0
**Data**: Abril 2026
**Autor**: Equipe de ML
