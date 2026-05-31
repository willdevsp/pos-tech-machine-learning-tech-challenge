# RocketTail API Component

Este componente gerencia o serviço de inferência RESTful da API de recomendação utilizando **FastAPI**.

## Setup e Execução
Instale localmente as dependências da API:
```bash
cd api
pip install -e .
```

Inicie o servidor uvicorn:
```bash
uvicorn rocket_tail_api.app:app --reload
```

## Endpoints Principais
- `GET /health` — Verificação de saúde da API.
- `POST /recommend` — Retorna recomendações personalizadas para um usuário específico.
