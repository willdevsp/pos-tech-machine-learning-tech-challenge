---
name: rocket-tail-pytorch-model
description: >-
  Develops and trains the PyTorch Hybrid Neural Network (Collaborative + Content-Based),
  implements baselines (KNN, Cosine, Popularity), metrics (NDCG, Recall, Precision, MRR), and MLflow Model Registry.
---

# rocket-tail-pytorch-model

Esta skill foca no design da arquitetura neural do modelo de recomendação com PyTorch, no processo de treinamento/validação, comparação de baselines clássicos, e registro/versionamento do modelo final no MLflow Model Registry.

## Ações e Responsabilidades

### 1. Arquitetura Neural Híbrida (PyTorch)
* Criar uma rede neural profunda baseada em Multi-Layer Perceptron (MLP) com 3 a 4 camadas (ex: densidades de 256, 128, 64) e saída sigmoide indicando a probabilidade de interação.
* Combinar camadas de Embedding para filtragem colaborativa (identidade de usuário e item) com as características coletadas do produto (Content-Based) no modelo híbrido (`HybridNN`).
* Aplicar regularização para mitigar overfitting (como Dropout de 0.1 a 0.3 e L2 weight decay).

### 2. Pipeline de Treinamento
* Definir datasets e dataloaders eficientes em PyTorch.
* Executar o loop de treinamento puro (ou com auxílio do PyTorch Lightning) controlando épocas, otimizador Adam, critério de perda Binary Cross-Entropy (BCE) e critério de early stopping baseado no loss do conjunto de validação.
* Exportar o melhor modelo treinado para `models/best_model.pt`.

### 3. Implementação de Baselines para Comparação
* **Popularity**: Recomendação de itens mais acessados.
* **Cosine/Item-Item Similarity**: Similaridade baseada nos atributos dos itens.
* **KNN/User-User Similarity**: Vizinhos mais próximos no histórico de compras.

### 4. Métricas de Recomendação
Computar pelo menos 4 métricas clássicas avaliando o top-K itens recomendados:
* **NDCG@K** (Normalized Discounted Cumulative Gain)
* **Precision@K** e **Recall@K**
* **MRR** (Mean Reciprocal Rank)
* **Diversity** e **Coverage** de produtos recomendados.

### 5. MLflow Model Registry
* Registrar e catalogar os artefatos de modelo no registro do MLflow.
* Controlar os estágios de transição de modelos registrados (`Staging` e `Production`) de forma segura através do pipeline do GitHub Actions utilizando ambientes com regras de aprovação manual (*manual approvals*):
  - **Staging**: Acionado via workflow, requer aprovação de um revisor para rodar o job que altera o estágio no MLflow para `Staging`.
  - **Production**: Acionado em um segundo momento, requer uma nova rodada de aprovação manual para promover o modelo mais recente de `Staging` para `Production`.

