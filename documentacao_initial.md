# O problema:
Uma empresa de e-commerce precisa de um sistema de recomendação de
produtos baseado no comportamento de navegação dos usuários. O modelo central
é uma rede neural (MLP ou embedding-based) treinada com PyTorch, com pipeline
completo containerizado em Docker, dados versionados com DVC, experimentos
rastreados no MLflow e código seguindo padrões profissionais de clean code.

## Requisitos Obrigatórios
Repositório github
• Estrutura clean code: módulos curtos, nomes descritivos, SOLID, type hints.
• pyproject.toml com Poetry/uv, dependências prod/dev separadas, lock file commitado.
• .dockerignore, .gitignore, .env.example configurados.
• Histórico de commits semântico.


## Bibliotecas Requeridas
• PyTorch — rede neural para o modelo de recomendação.
• Scikit-Learn — pré-processamento e baselines.
• MLflow — tracking de experimentos e Model Registry.
• DVC — versionamento de dados e pipeline reprodutível.


## Boas Práticas Obrigatórias
• Clean code: funções ≤ 20 linhas, naming conventions, type hints.
• Design patterns aplicados (Factory, Strategy ou Template Method).
• Dockerfile multi-stage com imagem otimizada.
• Pipeline DVC com ≥ 3 stages.
• Seeds fixados, lock file, .env



## Etapas de Desenvolvimento (4 Etapas)
## Etapa 1 — Clean Code e Estrutura 
Foco: Projeto limpo com padrões de engenharia desde o início

### Tarefa Referência
- Definir estrutura de projeto com src/, tests/, data/, models/, configs/
- Aplicar naming conventions e SOLID desde a primeira linha.
- Implementar ≥ 1 design pattern (Factory para criar modelos, Strategy para reprocessors).
- Type hints em todas as funções públicas + docstrings Google style.
- Configurar ruff sem erros + precommit hooks.


Entregável: Repositório base com estrutura limpa e linting passando


## Etapa 2 -  Ambiente e Dependências
Foco: Reprodutibilidade garantida com gerenciamento moderno de
dependências
- Configurar pyproject.toml com Poetry: deps de prod (pytorch, sklearn, mlflow) e dev (pytest, ruff)
- Gerar e commitar lock file 
- Externalizar configurações para .env + Pydantic Settings. 
- Script de validação de ambiente (scripts/validate_env.py)
- Verificar instalação limpa em ambiente novo.
Entregável: Projeto instalável do zero com poetry install.


## Etapa 3 — Containerização e Versionamento
Foco: Docker + DVC + MLflow integrados em pipeline reprodutível.
- Dockerfile multi-stage: builder (deps) + runtime (app).
- docker-compose.yml com serviço de treino + MLflow server.
- DVC init, versionar dataset, configurar remote (AWS S3).
- Pipeline DVC (dvc.yaml): preprocess → feature_eng → train → evaluate.
- MLflow tracking: logar params, métricas, artefatos de cada run.


## Etapa 4 — Rede Neural, Registry e Entrega (Disciplina 04 + consolidação)
Foco: Modelo neural treinado, registrado e documentado.
- Treinar MLP/embedding model com PyTorch para recomendação.
- Comparar com baselines (ScikitLearn) usando ≥ 4 métricas.
- Registrar modelo no MLflow Model Registry → Staging → Production.
- Escrever Model Card com performance, limitações e vieses.
- Finalizar README com instruções completas.
- Deploy em nuvem via Docker


Passo a Passo Resumido
• [Etapa 1] Estrutura clean code + design patterns + linting.
• [Etapa 2] Poetry + lock file + .env + validação de ambiente.
• [Etapa 3] Docker multi-stage + DVC pipeline + MLflow tracking.
• [Etapa 4] MLP PyTorch + Model Registry + Model Card + vídeo


