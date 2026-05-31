# RocketTail Shared Package

Pacote Python com componentes reutilizáveis compartilhados entre a API e o pipeline de treinamento.

## Instalação Local
Para instalar em modo de desenvolvimento:
```bash
cd shared
pip install -e .
```

## Estrutura
- `models/` — Arquiteturas de redes neurais em PyTorch.
- `ml/` — Factory de modelos e métricas comuns.
- `data/` — Lógicas de pré-processamento estruturadas via Strategy Pattern.
- `config/` — Configurações compartilhadas usando Pydantic Settings.
- `utils/` — Utilidades como logs comuns.
