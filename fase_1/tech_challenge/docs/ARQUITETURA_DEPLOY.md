# Arquitetura de Deploy - Telco Churn Prediction

**Data**: 2026-04-19
**Versão**: 1.0
**Status**: Aprovado para Staging

---

## 1. VISÃO GERAL

### Decisão Arquitetural: Hybrid Real-Time + Batch

```
┌─────────────────────────────────────────────────────────────┐
│                    ARQUITETURA HÍBRIDA                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Real-Time Path:  API REST → Inference → Score Individual   │
│  Batch Path:      ETL → Preprocessing → Inference → Export  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Justificativa**:
- **Real-Time (API)**: Para atendimento de clientes (agentes VoIP/chat podem ver risco em tempo real)
- **Batch**: Para campanhas de retenção noturnas, análises agregadas, backup
- **Híbrido**: Flexibilidade máxima com custo otimizado

---

## 2. ARQUITETURA DETALHADA

### 2.1 Visão em Camadas

```
┌─────────────────────────────────────────────────────────────┐
│              PRESENTATION LAYER                             │
│  FastAPI OpenAPI Docs | Dashboards Grafana | CLI Scripts   │
└────────────────┬────────────────────────────────────────────┘
                 │
┌─────────────────▼────────────────────────────────────────────┐
│              API & ORCHESTRATION LAYER                       │
│  • Flask/FastAPI HTTP Server (ALB + ASG)                    │
│  • Lambda Functions (batch, async jobs)                     │
│  • SQS Queues (async processing)                            │
└────────────────┬────────────────────────────────────────────┘
                 │
┌─────────────────▼────────────────────────────────────────────┐
│              ML & INFERENCE LAYER                            │
│  • Model Loader (TorchScript cached in memory)              │
│  • Feature Transformer (standardscaler, encodings)          │
│  • Prediction Service                                       │
└────────────────┬────────────────────────────────────────────┘
                 │
┌─────────────────▼────────────────────────────────────────────┐
│              DATA LAYER                                      │
│  • RDS PostgreSQL (features, predictions, logs)             │
│  • S3 (model artifacts, backups, audit logs)                │
│  • ElastiCache Redis (caching)                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Componentes Principais

#### A. API de Inferência (Real-Time)

```
FastAPI Application
├── GET    /health              → Health Check
├── POST   /api/predict         → Single prediction
├── POST   /api/predict-batch   → Batch (até 100 samples)
├── GET    /api/model-info      → Metadados do modelo
└── GET    /api/docs            → Swagger OpenAPI
```

**Especificações**:
- **Framework**: FastAPI (Python 3.10+)
- **Server**: Gunicorn (4 workers, 2 threads each)
- **Load Balancer**: AWS Application Load Balancer (ALB)
- **Auto Scaling**: EC2 Auto Scaling Group (min=2, max=10 instâncias)

**Latência Esperada**:
- P50: 80ms
- P95: 200ms
- P99: 500ms

#### B. Modelo & Preprocessing

```
Model Pipeline:
┌─────────────────────────────────────┐
│ Input: JSON {19 features}           │
├─────────────────────────────────────┤
│ 1. Validação Schema (Pydantic)     │
│ 2. Feature Engineering              │
│    - Binary Encoding (Yes/No → 1/0) │
│    - One-Hot Encoding (categorias)  │
│    - Reordenar features             │
│ 3. StandardScaler Normalization     │
│ 4. XGBoost Inference                │
│ 5. Probabilidade → Classe           │
├─────────────────────────────────────┤
│ Output: {prediction, probability}   │
└─────────────────────────────────────┘
```

**Detalhes**:
- **Formato Modelo**: XGBoost (.xgb) + Pickle scaler
- **Tamanho Modelo**: ~50MB (compactado)
- **Loading**: Feito no startup, cached em RAM
- **Versioning**: Git tags + S3 backup

#### C. Processamento em Batch

```
Batch Pipeline (Executado noturno via Lambda):
1. ETL: Buscar 7k clientes novos do RDS
2. Preprocessing: Aplicar transformações
3. Inference: Rodar predictions em lote (7k em ~1 min)
4. Export: Salvar em CSV no S3 + atualizar RDS
5. Alertas: Enviar scores para CRM via API
```

**Scheduling**:
- **Frequência**: Diariamente às 23:00 UTC (horário baixo)
- **Duração**: ~5 minutos
- **Trigger**: EventBridge + Lambda
- **Fallback**: Manual via CLI se falhar

---

## 3. INFRAESTRUTURA AWS

### 3.1 Componentes AWS

| Componente | Propósito | Tier/Config | Custo Estimado |
|-----------|----------|------------|----------------|
| **ALB** | Load Balancer | 1 ALB | $16/mês |
| **EC2** | API Servers | t3.medium (2 instâncias) | $60/mês |
| **ASG** | Auto Scaling | Min=2, Max=10 | Variável com uso |
| **RDS** | Banco Dados | db.t3.small, 100GB | $45/mês |
| **S3** | Armazenamento | 10GB (modelo + logs) | $0.23/mês |
| **ElastiCache** | Redis Caching | cache.t3.micro | $15/mês |
| **Lambda** | Batch Processing | 5min × 1x/dia | $1/mês |
| **EventBridge** | Scheduling | 1 regra simples | $1/mês |
| **CloudWatch** | Monitoramento | Logs + Métricas | $10/mês |
| **CloudFormation** | IaC | Sem custo | $0 |

**Total Estimado**: ~$150/mês em staging | ~$200-250/mês em produção (com escala)

### 3.2 Diagrama de Infraestrutura

```
                          ┌─────────────────────┐
                          │  Route 53 (DNS)     │
                          │  api.churn.co       │
                          └──────────┬──────────┘
                                     │
                          ┌──────────▼──────────┐
                          │  CloudFront CDN     │
                          │  (cache responses)  │
                          └──────────┬──────────┘
                                     │
                ┌────────────────────▼─────────────────────┐
                │     AWS Application Load Balancer        │
                │  Port 80 (HTTP) → HTTPS redirect        │
                │  Port 443 (HTTPS) → EC2 Target Group    │
                └────────────────────┬─────────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
    ┌────▼─────┐             ┌──────▼──────┐          ┌──────────▼────┐
    │ EC2 #1   │             │ EC2 #2     │          │ EC2 #3 (ASG)  │
    │ t3.medium│             │ t3.medium  │          │ (auto-created)│
    │ FastAPI  │             │ FastAPI    │          │ FastAPI       │
    │ Port 8000│             │ Port 8000  │          │ Port 8000     │
    └────┬─────┘             └──────┬──────┘          └──────────┬────┘
         │                          │                           │
         └──────────────────────────┼───────────────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
         ┌────▼────────┐       ┌────▼────────┐      ┌────▼────────┐
         │ RDS DB      │       │ S3 Bucket   │      │ ElastiCache │
         │ PostgreSQL  │       │ Model       │      │ Redis       │
         │ db.t3.small │       │ Artifacts   │      │ cache.t3    │
         │ 100GB SSD   │       │ & Logs      │      │ micro       │
         └─────────────┘       └─────────────┘      └─────────────┘


         ┌──────────────────────────────────────────┐
         │  Lambda + EventBridge (Batch)            │
         │  Executa noturno: 23:00 UTC              │
         │  - Lê dados RDS                          │
         │  - Roda inference                        │
         │  - Salva S3 + atualiza RDS               │
         └──────────────────────────────────────────┘


         ┌──────────────────────────────────────────┐
         │  CloudWatch                              │
         │  - Logs (CloudWatch Logs)                │
         │  - Métricas (CPU, latência, erros)       │
         │  - Alerta (F1-score, disponibilidade)    │
         └──────────────────────────────────────────┘
```

---

## 4. FLUXO DE REQUISIÇÃO (Real-Time)

### Caso de Uso: Agente de Vendas verifica risco de cliente

```
1. CLIENTE → HTTP POST /api/predict
   Headers: Authorization: Bearer <token>
   Body: {
     "features": {
       "gender": "Male",
       "senior_citizen": 0,
       "tenure_months": 24,
       ...
     }
   }

2. ALB → Distribui para EC2 saudável (health check validado)

3. FastAPI (EC2)
   - Valida schema Pydantic
   - Busca scaler do cache Redis
   - Aplica preprocessamento
   - Realiza inferência
   - Log da predição em CloudWatch

4. Response → HTTP 200 OK
   Body: {
     "prediction": 1,
     "probability": 0.72,
     "risk_level": "high",
     "recommended_action": "offer_discount",
     "model_version": "v1.0",
     "latency_ms": 145
   }

5. Salva em RDS (auditoria)
   - customer_id, timestamp, prediction, probability
```

**SLAs**:
- Latência P95: <200ms ✅
- Disponibilidade: >99.9% ✅
- Taxa de erro: <0.5% ✅

---

## 5. FLUXO DE PROCESSAMENTO (Batch)

### Execução Noturna: 7K clientes

```
23:00 UTC → EventBridge Trigger
   ↓
Lambda Function (timeout=300s)
   ↓
1. Query RDS: SELECT * FROM customers WHERE updated_at > now() - interval 24h
   → ~7,000 registros
   ↓
2. Preprocessing em lote (pandas + numpy)
   - Apply transformations (scaling, encoding)
   - Tempo: ~30s
   ↓
3. XGBoost Inference em lote
   - 7K predictions em paralelo (numpy)
   - Tempo: ~20s
   ↓
4. Salvar resultados
   - UPDATE customers SET churn_score = ?
   - INSERT INTO prediction_history
   - Tempo: ~10s
   ↓
5. Export para S3
   - CSV com top 1K em risco
   - JSON para integração CRM
   ↓
6. Send to Webhook (CRM)
   - POST https://crm.company.com/api/predictions
   - Payload: [customer_id, score, risk_level]
   ↓
Total: ~5 minutos

23:05 → Notificação enviada a Success Team
```

**Fallback**:
- Se Lambda falhar: Tentativa automática 2x
- Se ainda falhar: Alerta manual em Slack
- Retry manual: `make batch-predict`

---

## 6. SEGURANÇA

### 6.1 Autenticação & Autorização

```
┌─────────────────────┐
│ API Requests        │
└──────────┬──────────┘
           │
    ┌──────▼──────────┐
    │ API Gateway     │
    │ + Auth Headers  │
    └──────┬──────────┘
           │
    ┌──────▼──────────┐
    │ JWT Validation  │
    │ (HS256/RS256)   │
    └──────┬──────────┘
           │
    ┌──────▼──────────┐
    │ Rate Limit      │
    │ 100 req/min     │
    └──────┬──────────┘
           │
    ┌──────▼──────────┐
    │ FastAPI App     │
    │ (proceed)       │
    └─────────────────┘
```

**Credenciais**:
- JWT tokens (6h expiry)
- Refresh tokens (30d expiry)
- Keys armazenadas em AWS Secrets Manager

### 6.2 Network Security

```
VPC com 3 Subnets:
├── Public (ALB)
│   └── Security Group: Allow 80/443 from 0.0.0.0/0
│
├── Private App (EC2)
│   └── Security Group: Allow 8000 from ALB only
│
└── Private Data (RDS, Redis)
    └── Security Group: Allow 5432/6379 from App only
```

**TLS/SSL**:
- Certificate: AWS ACM (free)
- Protocol: TLS 1.2 (minimum)
- Ciphers: Modern suites only

### 6.3 Data Protection

- **In Transit**: TLS 1.2+
- **At Rest**:
  - RDS: AWS KMS encryption
  - S3: SSE-S3 encryption
  - Redis: No PII stored (only scores)
- **Backups**: RDS automated backup (7 days retention)

---

## 7. MONITORAMENTO & OBSERVABILIDADE

### 7.1 Métricas Principais

```
CloudWatch Dashboard (Real-time):

Application Metrics:
├── Request Rate (req/min)
├── Latency (P50, P95, P99)
├── Error Rate (4xx, 5xx)
├── Cache Hit Rate (Redis)
└── Model Inference Time

Infrastructure Metrics:
├── EC2 CPU Utilization
├── Memory Usage
├── Network In/Out
├── RDS Connections
└── Lambda Execution Time

Model Metrics:
├── Prediction Distribution (% churn vs non-churn)
├── Feature Drift (KL divergence from baseline)
├── Model Version in use
└── Last Model Update
```

### 7.2 Alertas Configurados

| Alerta | Threshold | Ação | Recipient |
|--------|-----------|------|-----------|
| **API Latency P95** | >500ms | PagerDuty | On-call |
| **Error Rate** | >1% | Slack | #alerts |
| **Model Drift** | KL>0.1 | Slack | #ml-team |
| **DB Connection Pool** | >80% | Slack | #ops |
| **Disk Space (RDS)** | >80% | Slack | #ops |
| **Lambda Batch Fail** | Any | Email | ml-lead |

### 7.3 Logging

```
CloudWatch Logs (estruturado em JSON):
{
  "timestamp": "2026-04-19T14:23:45Z",
  "level": "INFO",
  "service": "prediction-api",
  "request_id": "abc123",
  "customer_id": "HASH(xxx)", ← sem PII
  "latency_ms": 145,
  "prediction": 1,
  "probability": 0.72,
  "model_version": "v1.0",
  "status": "success"
}

Retention: 30 days online, archive to S3 after
```

---

## 8. DISASTER RECOVERY & BUSINESS CONTINUITY

### 8.1 Cenários de Falha

| Cenário | Probabilidade | RTO | RPO | Mitigação |
|---------|--------------|-----|-----|-----------|
| **EC2 crash** | Média | 2 min | 0 | ALB health check + ASG auto-replace |
| **RDS failover** | Baixa | 5 min | <1 min | Multi-AZ enabled |
| **S3 bucket deleted** | Muito Baixa | 1h | 24h | Versioning + MFA delete |
| **Model corrupted** | Muito Baixa | 5 min | 0 | Model versioning + git history |
| **Data breach** | Muito Baixa | N/A | - | Encryption at rest + VPC |

**RTO/RPO Targets**:
- RTO: < 15 minutos (objetivo do negócio)
- RPO: < 1 hora (perda aceitável de dados)

### 8.2 Backup Strategy

```
Backups:
├── RDS: Automated daily + manual weekly
├── S3 Model: Version control + git backup
├── Configurations: IaC (Terraform) in git
└── Secrets: AWS Secrets Manager backed up
```

---

## 9. DEPLOYMENT PIPELINE

### 9.1 CI/CD

```
GitHub PR → GitHub Actions:
  ├── Run tests (pytest)
  ├── Lint check (ruff)
  ├── Security scan (bandit)
  └── Coverage check (>80%)
      │
      └─→ Merge to main ✅
           │
           ├─→ Docker build
           ├─→ Push to ECR
           └─→ Update task definition
                │
                ├─→ Deploy to Staging (automatic)
                │   - Run smoke tests
                │   - Verify endpoints
                │   - Check latency baseline
                │
                └─→ Manual approval
                     │
                     └─→ Deploy to Production
                         - Canary: 10% traffic
                         - Monitor 5 minutes
                         - Full rollout (100%)
```

### 9.2 Model Deployment

```
Model Training Complete:
  ├── Evaluate metrics (F1, AUC, etc.)
  ├── Compare vs current model
  └── If better:
      ├── Tag in git: v1.1-20260419
      ├── Upload to S3 (versioned)
      ├── Update model_version.txt
      └── Trigger staging deployment

      → Monitoring 48h in staging
        → If all metrics OK
           → Approve for production
           → Update model serving
           → Notify stakeholders
```

---

## 10. ESCALAÇÃO HORIZONTAL

### 10.1 Current Setup (Staging)

- **EC2**: t3.medium × 2 (1 vCPU, 4GB RAM)
- **Capacity**: ~500 req/min sustained
- **Cost**: $60/month

### 10.2 Production Scaling

```
Load (req/min) | EC2 Type | Count | Estimated Latency | Cost/month
─────────────────────────────────────────────────────────────────────
<500           | t3.medium| 2     | <150ms            | $60
500-2K         | t3.large | 3     | <200ms            | $100
2K-5K          | t3.large | 5     | <250ms            | $160
>5K            | t3.xlarge| 8+    | <300ms            | $250+
```

**Escalação Automática (ASG)**:
- Scale up: If CPU > 70% for 2 min → add 2 instances
- Scale down: If CPU < 30% for 5 min → remove 1 instance
- Cooldown: 3 minutes between scaling actions

---

## 11. ROADMAP DE EVOLUÇÃO

### Q2 2026 (Próximas 3 meses)

- [ ] Deploy em staging completo
- [ ] Testes de carga (5K req/min)
- [ ] Integração CRM real
- [ ] Monitoring dashboard em produção

### Q3 2026 (3-6 meses)

- [ ] Multi-region deploy (US + EU)
- [ ] Model retraining automático (trigger semanal)
- [ ] A/B testing framework para modelos
- [ ] Explicabilidade (SHAP values in API response)

### Q4 2026 (6-12 meses)

- [ ] On-device inference (edge, telefone)
- [ ] Federated learning (privacy-preserving retraining)
- [ ] GraphQL API (alternativa a REST)

---

## 12. APROVAÇÕES

| Papel | Nome | Data | Status |
|-------|------|------|--------|
| **CTO** | - | - | ____ |
| **VP Engineering** | - | - | ____ |
| **Security Officer** | - | - | ____ |
| **ML Lead** | - | - | ____ |

---

**Data de Criação**: 2026-04-19
**Versão**: 1.0
**Próxima Revisão**: 2026-05-19
**Autor**: Platform/ML Team
