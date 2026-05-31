---
name: rocket-tail-pipeline
description: >-
  Configures the DVC data pipeline (download, preprocess, feature engineering),
  performs EDA, handles temporal train/val/test splits, and logs preprocessing metadata to MLflow.
---

# rocket-tail-pipeline

Esta skill é responsável por configurar e executar o pipeline reprodutível de processamento de dados usando DVC, além da extração de features e análise exploratória de dados (EDA) do dataset RetailRocket.

## Ações e Responsabilidades

### 1. Definição do Pipeline DVC
Definir o fluxo de processamento no arquivo `dvc.yaml` contendo pelo menos 3 etapas (stages):
* **`download`**: Executa o script para obter o dataset via API do Kaggle.
* **`preprocess`**: Realiza a limpeza de dados brutos e validação de schema.
* **`feature_engineering`**: Gera vetores de entrada do modelo e a matriz de interação.

### 2. Parâmetros da Pipeline (`params.yaml`)
* Centralizar hiperparâmetros e limites (como atividade mínima de usuários/itens, divisão de teste/validação e dimensões de fatoração) para permitir ajustes dinâmicos nas execuções do DVC.

### 3. Limpeza e Pré-processamento
* Filtrar usuários de baixa atividade (ex: menos de 2 eventos) e remover eventos duplicados.
* Consolidar os arquivos de propriedades dos itens e efetuar o tratamento de nulos/categorias faltantes.
* Converter timestamps em data/hora estruturadas.

### 4. Engenharia de Features
* **User Features**: Calcular frequência de atividades, diversidade de itens visitados e histórico de compras.
* **Item Features**: computar popularidade (contagem de visualizações), conversão (compras / visualizações) e mapeamento de categorias.
* **Interaction Matrix**: Construir matriz esparsa do tipo CSR (`scipy.sparse.csr_matrix`) associando pesos a eventos (view: 1, addtocart: 2, purchase: 3).

### 5. Divisão Temporal de Dados (Temporal Split)
* Dividir os conjuntos de treino, validação e teste respeitando a ordem cronológica dos dados, para simular de forma realista a inferência real de modelos de e-commerce e prevenir o vazamento de dados do futuro.

### 6. Rastreamento e Log no MLflow
* Registrar métricas agregadas (número total de eventos, contagem de usuários únicos, contagem de itens únicos) e artefatos de distribuição de dados no MLflow durante o preprocessamento.
