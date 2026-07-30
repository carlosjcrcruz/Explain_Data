"""K-Means segmentation with standardized inputs and PCA visualization."""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.metrics import silhouette_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from app.core.config import MAX_CHART_POINTS
from app.core.exceptions import AppError
from app.schemas.analysis import ClusteringRequest
from app.services.dataset_service import store
from app.utils.preprocessing import apply_filters, require_columns


def analyze(request: ClusteringRequest) -> tuple[dict, list[str]]:
    """Create neutral K-Means groups from validated numeric features."""

    dataframe = store.get(request.dataset_id).dataframe
    filtered, warnings = apply_filters(dataframe, request.filters)
    require_columns(filtered, request.feature_columns)
    converted = filtered[request.feature_columns].apply(
        pd.to_numeric, errors="coerce"
    )
    incompatible = [
        column for column in converted.columns if converted[column].notna().sum() == 0
    ]
    if incompatible:
        raise AppError(
            "INCOMPATIBLE_CLUSTER_COLUMNS",
            "Use apenas colunas numéricas. Sem valores numéricos: "
            + ", ".join(incompatible),
        )
    if len(converted) < max(10, request.n_clusters * 2):
        raise AppError(
            "INSUFFICIENT_CLUSTER_DATA",
            "Há poucas linhas para a quantidade de grupos solicitada.",
        )

    preparation = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    matrix = preparation.fit_transform(converted)
    model = KMeans(n_clusters=request.n_clusters, random_state=42, n_init=10)
    labels = model.fit_predict(matrix)
    if len(np.unique(labels)) < 2:
        raise AppError(
            "CLUSTERING_FAILED",
            "Os dados não apresentaram variação suficiente para formar grupos.",
        )
    silhouette = float(silhouette_score(matrix, labels))

    pca = PCA(n_components=2, random_state=42)
    coordinates = pca.fit_transform(matrix)
    chart_indexes = np.arange(len(converted))
    if len(chart_indexes) > MAX_CHART_POINTS:
        rng = np.random.default_rng(42)
        chart_indexes = np.sort(
            rng.choice(chart_indexes, MAX_CHART_POINTS, replace=False)
        )
        warnings.append(
            f"O gráfico PCA usa uma amostra reprodutível de {MAX_CHART_POINTS:,} pontos; os grupos usam todas as linhas."
        )

    profile_frame = converted.copy()
    profile_frame["group"] = labels + 1
    profiles = []
    for group, values in profile_frame.groupby("group"):
        profiles.append(
            {
                "group": f"Grupo {group}",
                "size": int(len(values)),
                "percentage": float(len(values) / len(profile_frame) * 100),
                "averages": {
                    column: (
                        float(values[column].mean())
                        if values[column].notna().any()
                        else None
                    )
                    for column in request.feature_columns
                },
            }
        )

    return (
        {
            "metrics": {
                "groups": request.n_clusters,
                "observations": len(converted),
                "silhouette": silhouette,
                "pca_explained_variance": float(
                    pca.explained_variance_ratio_.sum()
                ),
            },
            "profiles": profiles,
            "points": [
                {
                    "x": float(coordinates[index, 0]),
                    "y": float(coordinates[index, 1]),
                    "group": f"Grupo {labels[index] + 1}",
                }
                for index in chart_indexes
            ],
            "settings": {
                "method": "K-Means",
                "features": request.feature_columns,
                "random_state": 42,
            },
            "transformations": [
                "Valores ausentes foram preenchidos pela mediana de cada variável.",
                "As variáveis foram padronizadas antes da clusterização para terem escalas comparáveis.",
                "O gráfico reduz as dimensões com PCA; os grupos foram calculados usando todas as variáveis selecionadas.",
            ],
            "interpretation": [
                "Os grupos são semelhanças matemáticas e precisam ser interpretados no contexto dos dados.",
                "O Silhouette Score varia aproximadamente de -1 a 1; valores maiores sugerem separação mais clara.",
                "Nenhum significado comercial, social ou comportamental foi atribuído automaticamente aos grupos.",
            ],
        },
        warnings,
    )

