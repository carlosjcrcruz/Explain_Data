"""Leakage-safe supervised learning pipelines and evaluation."""

from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    root_mean_squared_error,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

from app.core.exceptions import AppError
from app.schemas.analysis import SupervisedRequest
from app.services.dataset_service import store
from app.utils.preprocessing import apply_filters, require_columns
from app.utils.serialization import json_value


def _estimator(problem: str, model: str) -> Any:
    if problem == "classification":
        return {
            "logistic": LogisticRegression(max_iter=1000, random_state=42),
            "decision_tree": DecisionTreeClassifier(max_depth=8, random_state=42),
            "random_forest": RandomForestClassifier(
                n_estimators=150, max_depth=12, random_state=42, n_jobs=-1
            ),
        }[model]
    return {
        "linear": LinearRegression(),
        "decision_tree": DecisionTreeRegressor(max_depth=8, random_state=42),
        "random_forest": RandomForestRegressor(
            n_estimators=150, max_depth=12, random_state=42, n_jobs=-1
        ),
    }[model]


def analyze(request: SupervisedRequest) -> tuple[dict, list[str]]:
    """Train and evaluate a supervised model on one reproducible split."""

    dataframe = store.get(request.dataset_id).dataframe
    filtered, warnings = apply_filters(dataframe, request.filters)
    all_columns = [request.target_column, *request.feature_columns]
    require_columns(filtered, all_columns)
    work = filtered.loc[:, all_columns].copy()
    before = len(work)
    work = work.dropna(subset=[request.target_column])
    removed_target = before - len(work)
    if removed_target:
        warnings.append(
            f"Foram removidas {removed_target} linhas porque a variável alvo estava ausente."
        )
    if len(work) < 20:
        raise AppError(
            "INSUFFICIENT_TRAINING_DATA",
            "São necessárias ao menos 20 linhas com variável alvo válida.",
        )

    target = work[request.target_column]
    features = work[request.feature_columns]
    if request.problem_type == "regression":
        target = pd.to_numeric(target, errors="coerce")
        valid = target.notna()
        features, target = features.loc[valid], target.loc[valid]
        if len(target) < 20:
            raise AppError(
                "INVALID_TARGET_COLUMN",
                "A variável alvo de regressão precisa conter ao menos 20 números válidos.",
            )
    else:
        unique_classes = target.nunique()
        if unique_classes < 2 or unique_classes > min(50, len(target) // 2):
            raise AppError(
                "INVALID_TARGET_COLUMN",
                "Para classificação, a variável alvo deve conter entre 2 e 50 classes com observações suficientes.",
            )
        counts = target.value_counts()
        if counts.min() < 2:
            raise AppError(
                "INSUFFICIENT_CLASS_DATA",
                "Cada classe precisa ter ao menos 2 observações.",
            )
        imbalance = float(counts.max() / counts.sum())
        if imbalance >= 0.7:
            warnings.append(
                f"A classe majoritária representa {imbalance:.1%} da amostra; avalie F1, precisão e recall além da acurácia."
            )

    numeric_columns = list(features.select_dtypes(include="number").columns)
    categorical_columns = [
        column for column in request.feature_columns if column not in numeric_columns
    ]
    transformers = []
    if numeric_columns:
        transformers.append(
            (
                "numeric",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric_columns,
            )
        )
    if categorical_columns:
        transformers.append(
            (
                "categorical",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        (
                            "encoder",
                            OneHotEncoder(handle_unknown="ignore", max_categories=50),
                        ),
                    ]
                ),
                categorical_columns,
            )
        )

    stratify = target if request.problem_type == "classification" else None
    try:
        x_train, x_test, y_train, y_test = train_test_split(
            features,
            target,
            test_size=request.test_size,
            random_state=42,
            stratify=stratify,
        )
    except ValueError as exc:
        raise AppError(
            "INVALID_TRAIN_TEST_SPLIT",
            "Não foi possível preservar as classes na divisão. Adicione mais exemplos por classe.",
        ) from exc

    pipeline = Pipeline(
        [
            ("preprocessor", ColumnTransformer(transformers)),
            ("model", _estimator(request.problem_type, request.model)),
        ]
    )
    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_test)

    chart: dict[str, Any]
    if request.problem_type == "classification":
        labels = list(pd.unique(target))
        average = "binary" if len(labels) == 2 else "weighted"
        positive = labels[1] if len(labels) == 2 else None
        metrics = {
            "accuracy": float(accuracy_score(y_test, predictions)),
            "precision": float(
                precision_score(
                    y_test,
                    predictions,
                    average=average,
                    pos_label=positive,
                    zero_division=0,
                )
            ),
            "recall": float(
                recall_score(
                    y_test,
                    predictions,
                    average=average,
                    pos_label=positive,
                    zero_division=0,
                )
            ),
            "f1": float(
                f1_score(
                    y_test,
                    predictions,
                    average=average,
                    pos_label=positive,
                    zero_division=0,
                )
            ),
        }
        matrix = confusion_matrix(y_test, predictions, labels=labels)
        chart = {
            "type": "confusion_matrix",
            "labels": [str(label) for label in labels],
            "values": matrix.tolist(),
        }
    else:
        mse = mean_squared_error(y_test, predictions)
        metrics = {
            "mae": float(mean_absolute_error(y_test, predictions)),
            "mse": float(mse),
            "rmse": float(root_mean_squared_error(y_test, predictions)),
            "r2": float(r2_score(y_test, predictions)),
        }
        chart = {
            "type": "actual_vs_predicted",
            "actual": [json_value(value) for value in y_test.iloc[:300]],
            "predicted": [float(value) for value in predictions[:300]],
        }

    transformations = []
    if numeric_columns:
        transformations.append(
            "Variáveis numéricas: ausências preenchidas pela mediana e valores padronizados usando apenas o treino."
        )
    if categorical_columns:
        transformations.append(
            "Variáveis categóricas: ausências preenchidas pela moda e categorias codificadas usando apenas o treino."
        )

    return (
        {
            "metrics": metrics,
            "chart": chart,
            "split": {
                "training_rows": len(x_train),
                "test_rows": len(x_test),
                "test_percentage": request.test_size,
                "random_state": 42,
            },
            "settings": {
                "problem_type": request.problem_type,
                "model": request.model,
                "target": request.target_column,
                "features": request.feature_columns,
            },
            "transformations": transformations,
            "interpretation": [
                "As métricas descrevem o desempenho nesta divisão específica entre treino e teste.",
                "Uma única métrica não é suficiente para declarar o modelo bom; compare erros, equilíbrio entre classes e contexto de uso.",
                "O conjunto de teste foi usado para avaliação e não para ajustar transformações ou hiperparâmetros.",
            ],
        },
        warnings,
    )

