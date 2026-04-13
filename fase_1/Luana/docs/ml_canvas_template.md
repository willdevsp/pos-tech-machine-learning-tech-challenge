# ML Canvas - Tech Challenge Churn

## 1) Problema de negocio
- **Decisao apoiada**: identificar clientes com alto risco de cancelamento para que o time
  de retencao possa agir de forma proativa (oferta de desconto, contato personalizado).
- **Impacto esperado**: reducao da taxa de churn atual de ~26.5% e preservacao de receita
  recorrente mensal (MRR). O custo de reter um cliente e estimado como menor do que o custo
  de adquirir um novo.

## 2) Stakeholders
- **Dono de negocio**: Diretoria Comercial / VP de Customer Success
- **Time de dados**: Engenharia de ML (construcao e manutencao do modelo)
- **Time de produto/operacao**: CRM e time de retencao (consumidores do score)
- **Usuarios finais do score**: analistas de retencao e gestores de contas

## 3) Definicao de churn
- **Evento que define churn**: cancelamento do contrato pelo cliente (Churn Value = 1)
- **Janela de observacao**: historico de uso e faturamento ate o momento da predicao
- **Janela de previsao**: proximo ciclo de faturamento (mensal)

## 4) Dados
- **Fonte**: IBM Telco Customer Churn Dataset (Kaggle: yeanzc/telco-customer-churn-ibm-dataset)
- **Granularidade**: 1 linha por cliente (contrato ativo ou encerrado)
- **Volume**: 7.043 clientes, 33 variaveis originais (32 apos remover CustomerID)
- **Periodo coberto**: snapshot estatico — Q3 de uma operadora ficticia da California
- **Qualidade e lacunas**:
  - Total Charges: 11 valores ausentes (clientes novos sem faturamento acumulado) — imputados com mediana
  - Churn Reason: 5.174 valores ausentes (so preenchido para quem ja cancelou) — removida antes do treino
  - Demais colunas: sem ausencias

## 5) Metricas

### Metricas tecnicas
| Metrica  | Baseline (Dummy) | Baseline (LogReg) | Meta MLP |
|----------|-----------------|-------------------|----------|
| AUC-ROC  | 0.500           | **0.829**         | > 0.85   |
| PR-AUC   | 0.265           | **0.607**         | > 0.65   |
| F1       | 0.000           | **0.612**         | > 0.63   |

### Metrica de negocio
`valor_retido = TP * ticket_medio_mensal - FP * custo_contato - FN * ticket_medio_mensal`

Interpretacao: cada cliente corretamente identificado como churn e retido preserva o ticket
mensal; contatos desnecessarios (FP) tem custo operacional; clientes que churnam sem
intervencao (FN) representam perda total de receita.

## 6) SLOs e restricoes
- **Latencia maxima**: < 500ms por requisicao (batch ou real-time via API)
- **Frequencia de atualizacao**: re-treino mensal ou quando AUC-ROC cair > 3pp do baseline
- **Custo operacional**: modelo deve rodar em infraestrutura compartilhada (sem GPU dedicada)

## 7) Riscos e vieses
- **Vies geografico**: dataset restrito a California — generalizacao para outros estados nao garantida
- **Vies de contrato**: clientes month-to-month tem taxa de churn muito maior; modelo pode
  superpenalizar esse grupo
- **Data leakage**: colunas Churn Score, Churn Reason e Churn Label foram removidas antes
  do treino pois sao derivadas do proprio evento de churn
- **Plano de mitigacao**: validacao cruzada estratificada, analise de fairness por subgrupo
  (genero, senior citizen), monitoramento de distribuicao de features em producao

## 8) Plano de validacao
- **Split**: train/test estratificado por Churn Value (80/20), seed 42
- **Cross-validation**: StratifiedKFold k=5 para selecao de hiperparametros
- **Baselines**: DummyClassifier (referencia minima) e LogisticRegression (referencia linear)
- **Criterio minimo para promover modelo**: AUC-ROC > 0.85 e F1 > 0.63 no conjunto de teste
