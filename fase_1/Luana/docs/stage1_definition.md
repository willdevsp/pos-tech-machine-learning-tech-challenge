# Etapa 1 - Definicoes

## Metricas tecnicas
- AUC-ROC: desempenho global em classificacao binaria.
- PR-AUC: foco em qualidade na classe positiva (churn).
- F1: equilibrio entre precision e recall no threshold escolhido.

## Metrica de negocio (template)
Use este calculo para discutir custo evitado:

`custo_evitar_churn = TP * valor_cliente_retido - FP * custo_contato - FN * custo_perda`

Onde:
- `TP`: clientes de churn previstos corretamente.
- `FP`: clientes sem churn impactados por acao desnecessaria.
- `FN`: churn nao identificado.
