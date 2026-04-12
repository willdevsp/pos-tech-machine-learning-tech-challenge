Esta é a versão detalhada e expandida do documento de **Previsão de Churn**, estruturada com o rigor técnico de uma solução "Enterprise" e cobrindo todo o ciclo de vida de ML conforme as diretrizes da POSTECH.

---

# Documento de Definição de Projeto: Ciclo Completo de ML - Previsão de Churn

## 1. Entendimento de Negócio e Formulação (ML Canvas)

O objetivo primordial é transformar dados brutos de telecomunicações em inteligência acionável para reduzir a perda de receita.

* **Proposta de Valor**: Implementar um sistema de alerta precoce que identifique clientes com alta propensão ao cancelamento, permitindo que o time de Customer Success atue de forma personalizada antes do encerramento do contrato.
* **Atores de Negócio**:
    * **Marketing**: Criação de campanhas de retenção segmentadas.
    * **Financeiro**: Redução do impacto no MRR (Monthly Recurring Revenue).
    * **Engenharia de ML**: Manutenção da robustez e precisão do serviço.
* **Métricas de Sucesso (KPIs)**:
    * **Negócio**: Redução de 10% na taxa de churn trimestral e aumento do Lifetime Value (LTV).
    * **Técnico**: F1-Score (devido ao desbalanceamento) e AUC-ROC superiores aos baselines de mercado.

## 2. Exploração de Dados (EDA) e Qualidade

A análise exploratória do dataset **Telco Customer Churn (IBM)** revelou padrões críticos que direcionam a estratégia de modelagem:

* **Identificação de Ruído**: A coluna `Total Charges` contém strings vazias para clientes com `Tenure Months` zero. O tratamento consiste na coerção para float e preenchimento com zero, refletindo o fato de que clientes novos ainda não geraram cobranças totais.
* **Padrões de Churn Detectados**:
    * **Tipo de Contrato** (coluna `Contract`): Clientes com contratos "Month-to-month" possuem uma taxa de churn drasticamente superior aos contratos anuais (42.71% vs 11.26%), indicando baixa fidelização imediata.
    * **Serviços de Internet** (coluna `Internet Service`): Clientes de Fibra Óptica apresentam maior churn (41.89%) que os de DSL, sugerindo possíveis problemas de custo ou estabilidade técnica que o modelo deve capturar.
    * **Métodos de Pagamento** (coluna `Payment Method`): O uso de "Electronic Check" está fortemente correlacionado com a saída do cliente (45.29% de churn).
* **Desbalanceamento de Classe**: A proporção aproximada de 3:1 (Não-Churn vs. Churn) exige o uso de técnicas de amostragem ou ajuste de pesos na função de custo do PyTorch.

## 3. Arquitetura Técnica e Modelagem

### 3.1 Pipeline de Processamento
Utilização de `sklearn.pipeline.Pipeline` para garantir que o pré-processamento seja atômico:
* **Numéricas**: `Tenure Months`, `Monthly Charges`, `Total Charges` - Imputação e `StandardScaler`.
* **Categóricas**: `OneHotEncoder` para variáveis nominais como `Contract`, `Internet Service`, `Payment Method`, `Gender`, etc.

### 3.2 Rede Neural (PyTorch)
Implementação de uma **Multi-Layer Perceptron (MLP)** modular:
* **Camadas**: 3 camadas densas com ativação `ReLU` e `Dropout` (p=0.3) para controle de variância.
* **Otimização**: Otimizador `Adam` com *Learning Rate Scheduler* para ajuste fino da convergência.
* **Rastreamento**: Integração nativa com **MLflow** para registro de hiperparâmetros (batch size, learning rate) e métricas por época.

## 4. Governança, Ética e MLOps

Alinhado com a Aula 8 da POSTECH, o projeto não termina no treinamento.

* **Auditoria de Fairness**: Uso do `Fairlearn` para calcular a "Disparidade de Seleção". O modelo será testado para garantir que não haja viés contra o grupo `Senior Citizen` (idosos), assegurando que a estratégia de retenção seja equânime.
* **Model Card**: Documento técnico anexo detalhando:
    * Propósito do modelo.
    * Dados de treinamento e recortes demográficos.
    * Riscos e limitações (ex: não aplicabilidade para clientes B2B).
* **CI/CD Pipeline**: Automação via GitHub Actions para:
    * Execução de testes unitários com `pytest`.
    * Verificação de linting com `ruff`.
    * "Gatekeeping": O deploy é impedido se o Recall cair abaixo de um limiar pré-estabelecido ou se o teste de Fairness falhar.

## 5. Estratégia de Deploy e Monitoramento

### 5.1 Serving
* **API**: FastAPI operando em container Docker, expondo endpoints de saúde e predição.
* **Assinatura de Dados**: Uso de Pydantic para validação de contrato de entrada, evitando que dados malformados cheguem ao modelo.

### 5.2 Monitoramento de Produção
* **Data Drift**: Implementação de testes estatísticos (como Kolmogorov-Smirnov) para monitorar se a distribuição das variáveis de entrada (ex: `Monthly Charges`, `Tenure Months`) em produção mudou em relação ao treino.
* **Concept Drift**: Monitoramento da performance real conforme os dados de cancelamento efetivo retroalimentam o sistema, disparando gatilhos de retreinamento automático (Continuous Training).

---

Este documento serve como a "Fonte da Verdade" para o seu **Tech Challenge**, garantindo que todas as fases, desde a visão de negócio até o monitoramento em nuvem, estejam integradas sob as melhores práticas de Engenharia de Machine Learning.


Use os arquivos projeto-referencia para referencia de tudo que precisa ser feito e o tech-challencher.md