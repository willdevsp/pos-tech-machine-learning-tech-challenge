# 📚 DICIONÁRIO DE DADOS - Telco Customer Churn

---

## 📋 Índice Rápido

1. Identificadores (3 colunas)
2. Dados Geográficos (6 colunas)
3. Dados Demográficos (4 colunas)
4. Características de Serviço (10 colunas)
5. Dados de Negócio (4 colunas)
6. Variável Target (Churn) (6 colunas)

---

## 🔑 IDENTIFICADORES

### 1. **CustomerID**
- **Tipo**: String (e.g., "3668-QPYBK")
- **Descrição**: Identificador único do cliente
- **Valores Possíveis**: Strings alfanuméricas únicas
- **Uso em ML**: Apenas para rastreabilidade, NÃO usar como feature
- **Cheque de Qualidade**: 7,043 valores únicos (sem duplicatas)
- **Insight**: Cada linha = 1 cliente único

### 2. **Count**
- **Tipo**: Inteiro (sempre = 1)
- **Descrição**: Contador de clientes (todos têm valor 1)
- **Valores Possíveis**: [1]
- **Uso em ML**: REMOVER (coluna sem variância)
- **Cheque de Qualidade**: Todos os valores = 1
- **Insight**: Coluna redundante, apenas preenche espaço

### 3. **Churn Value** (Duplicata de Churn Label)
- **Tipo**: Inteiro binário (0/1)
- **Descrição**: Versão numérica de Churn Label
- **Valores Possíveis**: [0 = No, 1 = Yes]
- **Uso em ML**: Pode usar como complemento a Churn Label
- **Distribuição**: 0: 73.5% | 1: 26.5%
- **Insight**: Mesma informação que Churn Label mas em formato numérico

---

## 🌍 DADOS GEOGRÁFICOS

### 4. **Country**
- **Tipo**: String (sempre "United States")
- **Descrição**: País do cliente
- **Valores Possíveis**: ["United States"]
- **Uso em ML**: REMOVER (sem variância, todos EUA)
- **Cheque de Qualidade**: 7,043 valores = "United States"
- **Insight**: Dataset é apenas de clientes dos EUA

### 5. **State**
- **Tipo**: String (e.g., "CA", "TX", "NY")
- **Descrição**: Estado do cliente (2 letras, código USPS)
- **Valores Possíveis**: 50+ estados dos EUA
- **Uso em ML**: Feature categórica (pode ter variação geográfica em churn)
- **Distribuição**: Ca lifornia tem mais clientes (~1,000)
- **Insight**: Possível padrão regional de churn

### 6. **City**
- **Tipo**: String (e.g., "Los Angeles", "New York")
- **Descrição**: Cidade do cliente
- **Valores Possíveis**: 500+ cidades
- **Uso em ML**: Opcional (muito cardinalidade alta)
- **Alternativa**: Agrupar por State em vez de City
- **Insight**: Granularidade geográfica muito fina

### 7. **Zip Code**
- **Tipo**: String (e.g., "90001", "10001")  
- **Descrição**: CEP (código postal) do cliente
- **Valores Possíveis**: 1,000+ códigos postais únicos
- **Uso em ML**: REMOVER ou agrupar (cardinalidade alta)
- **Alternativa**: Usar já temos State (suficiente)
- **Insight**: Redundante com State para análise de churn

### 8. **Lat Long**
- **Tipo**: String (e.g., "34.06-118.24")
- **Descrição**: Latitude-Longitude combinadas
- **Valores Possíveis**: Coordenadas geográficas
- **Uso em ML**: REMOVER (formato ruim, use Latitude + Longitude)
- **Problema**: String em vez de float
- **Insight**: Não adiciona valor sobre State

### 9. **Latitude**
- **Tipo**: Float (e.g., 34.06)
- **Descrição**: Coordenada de latitude do cliente
- **Valores Possíveis**: [25.0 - 49.0] (EUA continental)
- **Uso em ML**: Opcional (para análise geoespacial avançada)
- **Distribuição**: Concentrada na Califórnia high
- **Insight**: Correlação com State (redundante)

### 10. **Longitude**
- **Tipo**: Float (e.g., -118.24)
- **Descrição**: Coordenada de longitude do cliente
- **Valores Possíveis**: [-125.0 - (-66.0)] (EUA)
- **Uso em ML**: Opcional (combinado com Latitude para clusters geográficos)
- **Distribuição**: Segue padrão USA
- **Insight**: Combinar com Latitude gera distância a data centers (feature engineering)

---

## 👥 DADOS DEMOGRÁFICOS

### 11. **Gender**
- **Tipo**: Categórico (Binário)
- **Descrição**: Gênero do cliente
- **Valores Possíveis**: ["Male", "Female"]
- **Distribuição**: ~50% Male | ~50% Female
- **Uso em ML**: Feature categórica (codificar One-Hot)
- **Cheque de Qualidade**: Sem valores faltantes
- **Insight**: Balanceado (sem viés);reco = verificar fairness por gênero

### 12. **Senior Citizen**
- **Tipo**: Binário (0/1)
- **Descrição**: Se cliente é idoso (65+ anos assumed)
- **Valores Possíveis**: [0 = Não idoso, 1 = Idoso]
- **Distribuição**: 0: 87.6% | 1: 12.4%
- **Uso em ML**: Feature importante; usar como binary
- **Cheque de Qualidade**: Sem faltantes
- **Insight Churn**: Investigar se idosos têm churn diferente

### 13. **Partner**
- **Tipo**: Categórico (Binário)
- **Descrição**: Se cliente tem parceiro/cônjuge
- **Valores Possíveis**: ["Yes", "No"]
- **Distribuição**: Yes: ~48% | No: ~52%
- **Uso em ML**: Feature categórica (One-Hot)
- **Cheque de Qualidade**: Sem valores faltantes
- **Insight Churn**: Clientes com parceiro podem ter churn mais baixo

### 14. **Dependents**
- **Tipo**: Categórico (Binário)
- **Descrição**: Se cliente tem dependentes (filhos, pais)
- **Valores Possíveis**: ["Yes", "No"]
- **Distribuição**: Yes: ~30% | No: ~70%
- **Uso em ML**: Feature categórica (One-Hot)
- **Cheque de Qualidade**: Sem faltantes
- **Insight Churn**: Dependentes = menos churn (comprometimento maior)

---

## 📱 CARACTERÍSTICAS DE SERVIÇO

### 15. **Tenure Months**
- **Tipo**: Inteiro (0-72 meses)
- **Descrição**: Meses desde que cliente é ativo
- **Valores Possíveis**: [0, 1, 2, ..., 72]
- **Estatísticas**: 
  - Mínimo: 0 meses
  - Máximo: 72 meses
  - Média: 32.4 meses
  - Mediana: 29 meses
- **Uso em ML**: Feature numérica contínua
- **Insight Churn**: **FORTE correlação negativa** - quanto mais antigo, menos chance de churn
  - Novos clientes (0-3 meses): ~50% churn
  - Clientes antigos (60+ meses): ~3% churn
- **Recomendação**: Usar como feature principal

### 16. **Phone Service**
- **Tipo**: Categórico
- **Descrição**: Se cliente tem serviço de telefone
- **Valores Possíveis**: ["Yes", "No"]
- **Distribuição**: Yes: ~91% | No: ~9%
- **Uso em ML**: Feature categórica (One-Hot)
- **Insight Churn**: Clientes sem telefone têm churn mais baixo (são casos edge)
- **Nota**: Desbalanceado em favor de "Yes"

### 17. **Multiple Lines**
- **Tipo**: Categórico
- **Descrição**: Se cliente tem múltiplas linhas telefônicas
- **Valores Possíveis**: ["Yes", "No", "No phone service"]
- **Distribuição**: No: ~42% | Yes: ~42% | No phone service: ~16%
- **Uso em ML**: Feature categórica (One-Hot com 3 categorias)
- **Insight Churn**: Clientes com múltiplas linhas = mais engajados = menos churn
- **Nota**: 3 categorias (usar cuidado em codificação)

### 18. **Internet Service**
- **Tipo**: Categórico (3 valores)
- **Descrição**: Tipo de serviço de internet
- **Valores Possíveis**: ["DSL", "Fiber optic", "No"]
- **Distribuição**: DSL: ~39% | Fiber optic: ~44% | No: ~17%
- **Uso em ML**: Feature categórica (One-Hot)
- **Insight Churn**: 
  - Fiber optic: **41.89% churn** 🔴 ALTO
  - DSL: **18.96% churn** 🟡 MÉDIO  
  - No Internet: **7.40% churn** 🟢 BAIXO
- **Recomendação**: Feature IMPORTANTE para modelo

### 19. **Online Security**
- **Tipo**: Categórico
- **Descrição**: Se cliente tem serviço de segurança online
- **Valores Possíveis**: ["Yes", "No", "No internet service"]
- **Distribuição**: No: ~42% | Yes: ~29% | No internet: ~29%
- **Uso em ML**: Feature categórica (One-Hot)
- **Insight Churn**: Clientes com "Online Security" = menos churn (aumento de stickiness)
- **Nota**: 3 categorias

### 20. **Online Backup**
- **Tipo**: Categórico
- **Descrição**: Se cliente tem serviço de backup online
- **Valores Possíveis**: ["Yes", "No", "No internet service"]
- **Distribução**: No: ~46% | Yes: ~24% | No internet: ~30%
- **Uso em ML**: Feature categórica (One-Hot)
- **Insight Churn**: Com Backup = menos churn (agregação de serviços)
- **Nota**: 3 categorias

### 21. **Device Protection**
- **Tipo**: Categórico
- **Descrição**: Se cliente tem proteção de dispositivo
- **Valores Possíveis**: ["Yes", "No", "No internet service"]
- **Distribuição**: No: ~47% | Yes: ~23% | No internet: ~30%
- **Uso em ML**: Feature categórica (One-Hot)
- **Insight Churn**: Serviços adicionais = cliente mais comprometido = menos churn
- **Nota**: 3 categorias

### 22. **Tech Support**
- **Tipo**: Categórico
- **Descrição**: Se cliente tem suporte técnico
- **Valores Possíveis**: ["Yes", "No", "No internet service"]
- **Distribuição**: No: ~45% | Yes: ~23% | No internet: ~32%
- **Uso em ML**: Feature categórica (One-Hot)
- **Insight Churn**: Tech Support usage = satisfação com serviço = menos churn
- **Nota**: 3 categorias

### 23. **Streaming TV**
- **Tipo**: Categórico
- **Descrição**: Se cliente tem streaming de TV
- **Valores Possíveis**: ["Yes", "No", "No internet service"]
- **Distribuição**: No: ~45% | Yes: ~24% | No internet: ~31%
- **Uso em ML**: Feature categórica (One-Hot)
- **Insight Churn**: Streaming services = mais uso = menos churn
- **Nota**: 3 categorias

### 24. **Streaming Movies**
- **Tipo**: Categórico
- **Descrição**: Se cliente tem streaming de filmes
- **Valores Possíveis**: ["Yes", "No", "No internet service"]
- **Distribuição**: No: ~44% | Yes: ~25% | No internet: ~31%
- **Uso em ML**: Feature categórica (One-Hot)
- **Insight Churn**: Streaming usage = engajamento = menos churn
- **Nota**: 3 categorias; correlacionado com Streaming TV

---

## 💼 DADOS DE NEGÓCIO

### 25. **Contract**
- **Tipo**: Categórico (3 valores)
- **Descrição**: Tipo de contrato do cliente
- **Valores Possíveis**: ["Month-to-month", "One year", "Two year"]
- **Distribuição**: Month-to-month: ~55% | One year: ~20% | Two year: ~25%
- **Uso em ML**: Feature categórica (One-Hot)
- **Insight Churn**: 
  - Month-to-month: **42.71% churn** 🔴 CRÍTICO
  - One year: **11.27% churn** 🟡 MÉDIO
  - Two year: **2.83% churn** 🟢 EXCELENTE
- **Recomendação**: Feature **CRÍTICA** para modelo
- **Impacto**: 15x diferença entre month-to-month e two year!

### 26. **Paperless Billing**
- **Tipo**: Categórico
- **Descrição**: Se cliente usa faturamento digital (sem papel)
- **Valores Possíveis**: ["Yes", "No"]
- **Distribuição**: Yes: ~60% | No: ~40%
- **Uso em ML**: Feature categórica (One-Hot ou binary)
- **Insight Churn**: Paperless = tech-savvy = pode ter outros padrões de engajamento
- **Nota**: Balanceado

### 27. **Payment Method**
- **Tipo**: Categórico (4 valores)
- **Descrição**: Método de pagamento preferido do cliente
- **Valores Possíveis**: ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"]
- **Distribuição**: 
  - Electronic check: ~35%
  - Mailed check: ~18%
  - Bank transfer: ~23%
  - Credit card: ~24%
- **Uso em ML**: Feature categórica (One-Hot)
- **Insight Churn**: 
  - Electronic check: **45.29% churn** 🔴 ALTO (cliente pode estar insatisfeito)
  - Mailed check: **20.73% churn** 🟡 MÉDIO
  - Bank transfer: **16.26% churn** 🟢 BOM (automático = comprometido)
  - Credit card: **15.29% churn** 🟢 BOM (automático)
- **Recomendação**: Feature IMPORTANTE
- **Insight Principal**: Automatização = menos churn

---

### 28. **Monthly Charges**
- **Tipo**: Float (valor em $ USD)
- **Descrição**: Fatura mensal do cliente
- **Valores Possíveis**: [$18.25 - $118.75]
- **Estatísticas**:
  - Mínimo: $18.25
  - Máximo: $118.75
  - Média: $64.80
  - Mediana: $63.30
- **Uso em ML**: Feature numérica contínua
- **Cheque de Qualidade**: Sem valores faltantes, sem outliers óbvios
- **Insight Churn**: Clientes com fatura ALTA têm... menos churn? (paradoxo - precisa investigar interação com Contract)
- **Nota**: Correlação com muitos serviços = clientes com mais valor

### 29. **Total Charges**
- **Tipo**: Float (valor acumulado em $ USD)
- **Descrição**: Valor total já pago pelo cliente (histórico)
- **Valores Possíveis**: [$0 - $8,684.80]
- **Estatísticas**:
  - Mínimo: $0 (clientes novos)
  - Máximo: $8,684.80
  - Média: $2,283.30
  - Mediana: $1,394.60
- **Missing Values**: 11 valores faltantes (identificados como clientes com tenure=0)
- **Tratamento**: Preenchidos com 0 (clientes novos não geraram cobranças)
- **Uso em ML**: Feature numérica contínua
- **Insight Churn**: Total Charges correlacionado com Tenure (quanto mais tempo, mais cobrado, menos churn)
- **Eng. Feature**: Total Charges / Monthly Charges = Tenure (poderia derivar, mas temos Tenure direto)

---

## 🎯 VARIÁVEL TARGET (CHURN)

### 30. **Churn Label**
- **Tipo**: Categórico (Binário)
- **Descrição**: **VARIÁVEL TARGET** - Se cliente cancelou serviço
- **Valores Possíveis**: ["Yes", "No"]
- **Distribuição**:
  - No (Não-Churn): 5,174 (73.5%) ✅
  - Yes (Churn): 1,869 (26.5%) ⚠️ MINORIA
- **Desbalanceamento**: Razão 1:2.77 (para cada 1 churn, há 2.77 não-churns)
- **Uso em ML**: TARGET BINARY para classificação
- **Impacto ML**: Necessário rebalanceamento (class weights ou SMOTE)
- **Checklist**:
  - ✓ Sem valores faltantes
  - ✓ Claro e não-ambíguo
  - ✓ Representa decisão real do negócio

### 31. **Churn Score** (Probabilidade)
- **Tipo**: Float [0.0 - 1.0]
- **Descrição**: Score de propensão ao churn (pre-calculado, não usar para treino!)
- **Valores Possíveis**: [0.00 - 1.00]
- **Distribuição**: Concentrado em extremos (0 ou 1)
- **Uso em ML**: 🚫 NUNCA usar como feature de entrada
- **Razão**: Data leakage - informa diretamente a resposta (Y)
- **Uso Válido**: Apenas validação posterior do modelo

### 32. **CLTV** (Customer Lifetime Value)
- **Tipo**: Float (valor em $ USD)
- **Descrição**: Valor estimado do cliente ao longo da vida
- **Valores Possíveis**: [$0 - $9,945.00]
- **Distribuição**: Correlacionada com Total Charges + Contract length
- **Uso em ML**: 🚫 EVITAR como feature
- **Razão**: Derivada de Tenure + Charges (colinariedade)
- **Uso Válido**: Apenas para análise de negócio (qual cliente é mais valioso)
- **Insight**: Clientes 2-year contracts têm CLTV muito mais alto

### 33. **Churn Reason**
- **Tipo**: String (texto livre)
- **Descrição**: Motivo do churn informado pelo cliente
- **Valores Possíveis**: 
  - "Competitor made better offer"
  - "Moved"
  - "Switched to better device"
  - "Better device offer"
  - "Cheaper alternative"
  - "Technical support" (insuficiente)
  - "Don't know"
  - NaN (para clientes que não churned)
- **Distribuição**: ~20+ razões diferentes
- **Uso em ML**: 🔄 USAR COM CUIDADO - NLP opcional
  - Se usar: Necessário text preprocessing (limpeza, tokenização, embedding)
  - Se NÃO usar: OK, outras features suficientes
- **Insight Churn**: 
  - "Competitor...": Problema preço/serviço
  - "Technical support": Problema de qualidade
  - "Moved": Fora de alcance geográfico
- **Recomendação para Etapa 1**: IGNORAR (foco em features estruturadas); considerar em Etapa posterior

---

## 📊 RESUMO EXECUTIVO

### Colunas por Importância para Churn Prediction

| Prioridade | Colunas | Razão |
|-----------|---------|-------|
| 🔴 CRÍTICA | Contract, Internet Service, Tenure Months, Payment Method | Correlação forte com churn (>30% diferença entre categorias) |
| 🟡 IMPORTANTE | Monthly Charges, Total Charges, Multiple Lines, Tech Support, Streaming | Correlação média com churn (10-20% diferença) |
| 🟢 ÚTIL | Gender, Senior Citizen, Partner, Dependents, Phone Service | Contextual demográfico (verificar fairness) |
| ⚪ REMOVER | CustomerID, Count, Country, Zip Code, Lat Long | Sem variância ou redundância geográfica |
| 🚫 NUNCA USE | Churn Score, CLTV, Churn Reason | Data leakage ou features derivadas |

### Recomendações de Pré-processamento

```
1. One-Hot Encoding (Categóricas):
   - Gender, Senior Citizen, Partner, Dependents
   - Phone Service, Multiple Lines, Internet Service
   - Online Security, Online Backup, Device Protection, Tech Support
   - Streaming TV, Streaming Movies
   - Contract, Payment Method
   - Paperless Billing

2. StandardScaler (Numéricas):
   - Tenure Months
   - Monthly Charges  
   - Total Charges

3. Remover (Sem variância):
   - CustomerID (apenas ID)
   - Count (sempre 1)
   - Country (sempre USA)
   - Zip Code (muito cardinalidade alta)
   - Lat Long (formato ruim, use Latitude+Longitude se necessário)
   - Churn Value (duplicata de Churn Label)

4. Evitar/Remover (Data Leakage):
   - Churn Score (informa diretamente Y)
   - CLTV (derivada de outras features)
   - Churn Reason (somente para clientes que churned)
```

---

## 📝 Notas Finais

- **Tamanho Dataset**: 7,043 registros × 33 colunas
- **Target**: Churn Label (26.5% churn, 73.5% não-churn)
- **Qualidade**: Excelente (99.85% completo)
- **Features Core**: Tenure, Contract, Internet Service, Payment Method
- **Desafio Principal**: Desbalanceamento 1:2.77 (rebalancear com class_weight ou SMOTE)

---

**Versão**: 1.0  
**Última Atualização**: Abril 2026  