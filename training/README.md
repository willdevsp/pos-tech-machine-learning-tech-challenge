# RocketTail Training Component

Este componente gerencia os dados, engenharia de features, e loops de treinamento do modelo de recomendação utilizando **DVC** e **MLflow**.

## Setup e Execução
Instale localmente as dependências de treino:
```bash
cd training
pip install -e .
```

## Estrutura
- `src/rocket_tail_training/` — Códigos dos pipelines.
- `dvc.yaml` — Configuração dos estágios do DVC pipeline.
- `tests/` — Testes unitários para validação das transformações e do treino.
