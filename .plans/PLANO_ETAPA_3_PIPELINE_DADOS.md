# PLANO ETAPA 3: Pipeline de Dados + Preparação

## TL;DR
Montar pipeline DVC reproduzível com 3+ stages: download dataset → preprocess → feature engineering. EDA exploratória, split train/val/test, logging de artefatos no MLflow. Tudo versionado com DVC, trigger automático no GitHub quando `training/` muda.

## Steps

### 3.1 DVC Initialization (em `training/`)
**Arquivo**: `training/dvc.yaml`

```yaml
stages:
  download:
    cmd: python -m rocket_tail_training.download_dataset
    deps:
      - src/rocket_tail_training/download_dataset.py
    outs:
      - ../data/raw/events.csv
      - ../data/raw/category_tree.csv
      - ../data/raw/item_properties_part1.csv
      - ../data/raw/item_properties_part2.csv
    params:
      - training.download

  preprocess:
    cmd: python -m rocket_tail_training.preprocess
    deps:
      - ../data/raw/
      - src/rocket_tail_training/preprocess.py
    outs:
      - ../data/processed/events_clean.csv
      - ../data/processed/items_clean.csv
    params:
      - training.preprocess
    plots:
      - ../data/processed/distribution_plots.json:
          template: linear

  feature_engineering:
    cmd: python -m rocket_tail_training.features
    deps:
      - ../data/processed/
      - src/rocket_tail_training/features.py
    outs:
      - ../data/features/user_features.parquet
      - ../data/features/item_features.parquet
      - ../data/features/interaction_matrix.sparse
    params:
      - training.features
```

**Arquivos de config**:

**Arquivo**: `training/params.yaml`

```yaml
training:
  download:
    source: kaggle
    dataset_name: retailrocket/ecommerce-dataset
    force: false  # Reusar se já existe

  preprocess:
    remove_duplicates: true
    handle_missing: drop
    min_events_per_user: 2
    min_events_per_item: 1

  features:
    embedding_dim: 32
    n_factors: 16  # Matriz fatorizada
    min_support: 5
    test_size: 0.2
    val_size: 0.1
```

### 3.2 Dataset Download Script
**Arquivo**: `training/src/rocket_tail_training/download_dataset.py`

```python
import kagglehub
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def download_dataset(output_dir: Path = Path("data/raw")):
    """Baixa dataset RetailRocket do Kaggle."""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Autenticação via ~/.kaggle/kaggle.json
    logger.info("Downloading RetailRocket dataset...")
    path = kagglehub.dataset_download("retailrocket/ecommerce-dataset")
    
    # Copiar arquivos
    import shutil
    for csv_file in Path(path).glob("*.csv"):
        dest = output_dir / csv_file.name
        shutil.copy(csv_file, dest)
        logger.info(f"Copied {csv_file.name} to {dest}")

if __name__ == "__main__":
    download_dataset()
```

### 3.3 Preprocessing Stage
**Arquivo**: `training/src/rocket_tail_training/preprocess.py`

**Funcionalidades**:
1. Carregar 4 CSVs
2. Validar schema
3. Handle missing values (drop ou forward fill)
4. Remove duplicates
5. Filter low-activity users/items
6. Join e consolidate
7. Salvar em Parquet (mais eficiente)

```python
def preprocess_events(df: pd.DataFrame, min_events: int = 2) -> pd.DataFrame:
    """Limpa dataset de eventos."""
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Filter low-activity users
    user_counts = df.groupby('visitorid').size()
    active_users = user_counts[user_counts >= min_events].index
    df = df[df['visitorid'].isin(active_users)]
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    return df

def preprocess_items(properties: pd.DataFrame) -> pd.DataFrame:
    """Limpa propriedades de items."""
    # Consolidate part1 + part2
    # Remove duplicates (últimas versões)
    properties = properties.drop_duplicates(subset=['itemid'], keep='last')
    
    # Handle missing categories
    properties['categoryid'].fillna(-1, inplace=True)
    
    return properties
```

### 3.4 Feature Engineering Stage
**Arquivo**: `training/src/rocket_tail_training/features.py`

**Objetivo**: Criar features para modelo neural

1. **User Features**:
   - user_id
   - activity_count (quantas interações)
   - avg_view_time
   - purchase_history (0/1)
   - favorite_categories (top 3)

2. **Item Features**:
   - item_id
   - category_id
   - popularity (view count)
   - conversion_rate (purchases / views)
   - avg_rating (se houver)

3. **Interaction Matrix**:
   - User-Item interactions (sparse matrix)
   - Tipo: {view: 1, addtocart: 2, purchase: 3}
   - Formato: `scipy.sparse.csr_matrix`

```python
def create_user_features(events_df: pd.DataFrame) -> pd.DataFrame:
    """Extrai features por usuário."""
    user_features = events_df.groupby('visitorid').agg({
        'event': 'count',  # activity_count
        'itemid': 'nunique',  # item_diversity
        'timestamp': ['min', 'max']
    }).reset_index()
    
    # Rename
    user_features.columns = ['user_id', 'activity_count', 'item_diversity', 
                             'first_event', 'last_event']
    
    # Adicionar purchase_history
    purchases = events_df[events_df['event'] == 'transaction']['visitorid'].unique()
    user_features['has_purchased'] = user_features['user_id'].isin(purchases).astype(int)
    
    return user_features

def create_interaction_matrix(events_df: pd.DataFrame) -> scipy.sparse.csr_matrix:
    """Cria matriz user-item."""
    from sklearn.preprocessing import LabelEncoder
    
    # Map event types to weights
    event_weights = {'view': 1, 'addtocart': 2, 'transaction': 3}
    events_df['weight'] = events_df['event'].map(event_weights)
    
    # Aggregate by user-item pair (máximo weight)
    interactions = events_df.groupby(['visitorid', 'itemid'])['weight'].max().reset_index()
    
    # Create sparse matrix
    user_enc = LabelEncoder().fit(interactions['visitorid'])
    item_enc = LabelEncoder().fit(interactions['itemid'])
    
    row = user_enc.transform(interactions['visitorid'])
    col = item_enc.transform(interactions['itemid'])
    data = interactions['weight'].values
    
    interaction_matrix = csr_matrix(
        (data, (row, col)),
        shape=(len(user_enc.classes_), len(item_enc.classes_))
    )
    
    return interaction_matrix, user_enc, item_enc
```

### 3.5 EDA (Exploratory Data Analysis)
**Arquivo**: `training/notebooks/eda.ipynb` (não versionado, apenas para exploração)

**Análises**:
1. Distribuição de eventos (view, addtocart, purchase)
2. Usuários mais ativos
3. Itens mais populares
4. Distribuição de categorias
5. Temporal trends (quando ocorrem events)
6. Sparsidade da interaction matrix
7. Viés de gênero/categoria (se houver dados)

**Output**: `data/processed/distribution_plots.json` (visualizations)

### 3.6 Train/Val/Test Split
**Arquivo**: `training/src/rocket_tail_training/split.py`

```python
def temporal_train_test_split(
    events_df: pd.DataFrame,
    train_ratio: float = 0.7,
    val_ratio: float = 0.1
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Temporal split (respeita cronologia de eventos)."""
    
    # Sort by timestamp
    events_df = events_df.sort_values('timestamp')
    
    n = len(events_df)
    train_idx = int(n * train_ratio)
    val_idx = int(n * (train_ratio + val_ratio))
    
    train_df = events_df.iloc[:train_idx]
    val_df = events_df.iloc[train_idx:val_idx]
    test_df = events_df.iloc[val_idx:]
    
    return train_df, val_df, test_df
```

**Razão temporal split**: Mais realístico (não vaza futura informação no treinamento)

### 3.7 MLflow Integration
**Arquivo**: `training/src/rocket_tail_training/pipeline.py`

```python
import mlflow
from rocket_tail_shared.config import settings

def run_pipeline():
    """Executa pipeline completo com MLflow logging."""
    
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment("rocket-tail-preprocessing")
    
    with mlflow.start_run(run_name="etapa-3-preprocessing"):
        # Log params
        mlflow.log_param("remove_duplicates", True)
        mlflow.log_param("min_events_per_user", 2)
        
        # Load + preprocess
        events_df = preprocess_events(...)
        items_df = preprocess_items(...)
        
        # Log metrics
        mlflow.log_metric("unique_users", events_df['visitorid'].nunique())
        mlflow.log_metric("unique_items", events_df['itemid'].nunique())
        mlflow.log_metric("total_events", len(events_df))
        
        # Feature engineering
        user_features = create_user_features(events_df)
        item_features = create_item_features(items_df)
        interaction_matrix, _, _ = create_interaction_matrix(events_df)
        
        # Log artifacts
        mlflow.log_artifact("data/processed/distribution_plots.json")
        mlflow.log_artifact("data/features/user_features.parquet")
        mlflow.log_artifact("data/features/item_features.parquet")
```

### 3.8 DVC Remote Configuration (S3)
**Arquivo**: `.dvc/config`

```ini
[core]
    analytics = false
    autostage = true
    
['remote "s3"']
    url = s3://rocket-tail-data/dvc-artifacts
    profile = default
    ssl_verify = true
```

**Setup inicial**:
```bash
dvc remote add -d s3 s3://rocket-tail-data/dvc-artifacts
dvc remote modify s3 profile default
```

### 3.9 Testes da Pipeline
**Arquivo**: `training/tests/test_preprocess.py`

```python
def test_preprocess_removes_duplicates():
    df = pd.DataFrame({
        'visitorid': [1, 1, 2],
        'itemid': [10, 10, 20],
        'event': ['view', 'view', 'view']
    })
    result = preprocess_events(df, min_events=1)
    assert len(result) < len(df)

def test_train_test_split_respects_ratios():
    df = pd.DataFrame({'timestamp': range(100)})
    train, val, test = temporal_train_test_split(df, 0.7, 0.2)
    assert len(train) == 70
    assert len(val) == 20
    assert len(test) == 10
```

### 3.10 DVC Pipeline Execution
**Comando**:
```bash
cd training
dvc repro  # Executa todas as stages
dvc push   # Upload artifacts para S3
dvc dag    # Visualiza dependency graph
```

### 3.11 GitHub Actions Trigger (Verificação no CI)
**No `train.yml` workflow** (da Etapa 1):

```yaml
- name: Test DVC pipeline
  run: |
    cd training
    dvc dag --check
    # Opcional: rodar localmente se dataset pequeno
    # dvc repro --dry
```

### 3.12 Documentation
**Arquivo**: `training/README.md`

Seções:
1. **Pipeline Overview**: Stages + outputs
2. **Data Sources**: RetailRocket dataset + Kaggle link
3. **Running the Pipeline**:
   ```bash
   # Setup
   poetry install
   dvc pull  # Baixa artifacts se existir S3
   
   # Run
   dvc repro
   ```
4. **Output Files**: Descrição de cada arquivo
5. **Metrics**: Stats do dataset processado

## Relevant files
- `training/dvc.yaml` — Pipeline definition
- `training/params.yaml` — Hyperparams + config
- `training/src/rocket_tail_training/download_dataset.py` — Kaggle download
- `training/src/rocket_tail_training/preprocess.py` — Data cleanup
- `training/src/rocket_tail_training/features.py` — Feature extraction
- `training/src/rocket_tail_training/pipeline.py` — MLflow integration
- `training/tests/test_preprocess.py`, `test_features.py` — Unit tests
- `.dvc/config` — Remote S3 setup
- `data/` — Raw, processed, features (gitignored, versionado com DVC)

## Verification
1. **DVC pipeline** executa sem erro: `dvc repro --dry`
2. **Artifacts versionados**: `dvc push` funciona para S3
3. **Testes passam**: `cd training && poetry run pytest tests/ -v`
4. **Outputs corretos**:
   - `events_clean.csv`: N linhas, sem duplicates
   - `user_features.parquet`: 1 linha por usuário
   - `interaction_matrix.sparse`: ~2M eventos em matriz esparsa
5. **MLflow tracking**: Métricas visíveis em http://localhost:5000
6. **EDA notebook**: Insights documentados
7. **Split respeitado**: train/val/test não se sobrepõem temporalmente

## Decisions
- **Temporal split**: Vs. random split (mais realístico para time-series)
- **DVC + S3**: Vs. Git LFS (melhor para ML artifacts)
- **Sparse matrix**: Vs. Dense (economiza 90% de memória)
- **Parquet**: Vs. CSV (mais rápido para features, comprime bem)
- **Kaggle auth via ~/.kaggle/kaggle.json**: Vs. API key em .env (segurança)

## Further Considerations
1. **Dados sensíveis**: Eventualmente, adicionar PII masking se necessário
2. **Dataset versioning**: Usar `dvc tag` para marcar snapshots importantes
3. **Benchmark**: Comparar com baseline simples (Popular Items) já nesta etapa
4. **Coldfstart**: Documentar como lidar com novos usuários/itens

---

**Duração Estimada**: 5-6 horas (setup DVC + EDA + features + testes)  
**Próxima Etapa**: PLANO_ETAPA_4_MODELO_DEPLOY.md  
**Dependência**: Etapa 1 + Etapa 2 completas
