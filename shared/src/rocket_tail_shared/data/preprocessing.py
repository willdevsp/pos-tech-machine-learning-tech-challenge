"""Data preprocessing using native scikit-learn Pipeline and ColumnTransformer."""

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder


class PipelineBuilder:
    """Construtor do Pipeline de pré-processamento nativo scikit-learn."""

    def __init__(self, target_columns: list[str] = None, id_columns: list[str] = None):
        """Initializes the PipelineBuilder.

        Args:
            target_columns: Target categorical columns like 'event'.
            id_columns: Identifier columns like 'visitorid', 'itemid'.
        """
        self.target_columns = target_columns or ["event"]
        self.id_columns = id_columns or ["visitorid", "itemid"]

    def create_preprocessor(self) -> Pipeline:
        """Cria o pipeline de pré-processamento completo.

        Returns:
            Pipeline configurado para retornar um Pandas DataFrame.
        """
        # Transformer para o target (ordinal encoding)
        target_transformer = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)),
            ]
        )

        # Transformer para identificadores (preenchimento básico)
        id_transformer = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
            ]
        )

        # Usa ColumnTransformer para aplicar nas colunas corretas
        preprocessor = ColumnTransformer(
            transformers=[
                ("target_pipe", target_transformer, self.target_columns),
                ("id_pipe", id_transformer, self.id_columns),
            ],
            remainder="passthrough",
            verbose_feature_names_out=False,
        )

        # Encapsula no Pipeline principal
        pipeline = Pipeline(steps=[("preprocessor", preprocessor)])

        # Força a saída a ser um Pandas DataFrame
        try:
            pipeline.set_output(transform="pandas")
        except AttributeError:
            # Compatibilidade com versões muito antigas do sklearn
            pass

        return pipeline
