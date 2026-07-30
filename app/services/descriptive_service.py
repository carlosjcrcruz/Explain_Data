"""Descriptive statistics with accessible interpretations."""

import math

import numpy as np
import pandas as pd

from app.core.config import MAX_CHART_POINTS
from app.core.exceptions import AppError
from app.schemas.analysis import DescriptiveRequest
from app.services.dataset_service import store
from app.utils.preprocessing import apply_filters, require_columns
from app.utils.serialization import json_value, records


def _finite(value: float | int | None) -> float | int | None:
    if value is None or not math.isfinite(float(value)):
        return None
    return json_value(value)


def analyze(request: DescriptiveRequest) -> tuple[dict, list[str]]:
    """Run descriptive statistics and prepare chart-ready structures."""

    dataframe = store.get(request.dataset_id).dataframe
    filtered, filter_messages = apply_filters(dataframe, request.filters)
    columns = request.columns or list(filtered.columns)
    require_columns(filtered, columns)
    selected = filtered.loc[:, columns]
    numeric = selected.select_dtypes(include="number")
    categorical = selected.select_dtypes(exclude="number")
    warnings = list(filter_messages)

    summary: list[dict] = []
    for column in numeric.columns:
        series = numeric[column].dropna()
        if series.empty:
            continue
        q1, median, q3 = series.quantile([0.25, 0.5, 0.75])
        iqr = q3 - q1
        outliers = int(((series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)).sum())
        modes = series.mode()
        summary.append(
            {
                "column": column,
                "count": int(series.count()),
                "missing": int(selected[column].isna().sum()),
                "mean": _finite(series.mean()),
                "median": _finite(median),
                "mode": _finite(modes.iloc[0]) if not modes.empty else None,
                "std": _finite(series.std()),
                "variance": _finite(series.var()),
                "minimum": _finite(series.min()),
                "q1": _finite(q1),
                "q3": _finite(q3),
                "maximum": _finite(series.max()),
                "outliers_iqr": outliers,
            }
        )

    categorical_summary: list[dict] = []
    for column in categorical.columns:
        series = categorical[column]
        counts = series.astype("string").fillna("Ausente").value_counts().head(10)
        mode = series.mode(dropna=True)
        categorical_summary.append(
            {
                "column": column,
                "count": int(series.notna().sum()),
                "missing": int(series.isna().sum()),
                "unique": int(series.nunique(dropna=True)),
                "mode": str(mode.iloc[0]) if not mode.empty else None,
                "top_values": [
                    {"value": str(key), "count": int(value)}
                    for key, value in counts.items()
                ],
            }
        )

    missing = [
        {
            "column": column,
            "count": int(selected[column].isna().sum()),
            "percentage": round(float(selected[column].isna().mean() * 100), 2),
        }
        for column in selected.columns
    ]
    correlations = (
        records(numeric.corr().reset_index(names="column"))
        if len(numeric.columns) >= 2
        else []
    )

    histograms = []
    for column in numeric.columns[:8]:
        values = numeric[column].dropna()
        if len(values) > MAX_CHART_POINTS:
            values = values.sample(MAX_CHART_POINTS, random_state=42)
            warnings.append(
                f"O histograma de {column} usa amostra de "
                f"{MAX_CHART_POINTS:,} pontos; as métricas usam todas as linhas filtradas."
            )
        counts, edges = np.histogram(values, bins=min(20, max(5, int(np.sqrt(len(values))))))
        histograms.append(
            {
                "column": column,
                "x": [float((edges[index] + edges[index + 1]) / 2) for index in range(len(counts))],
                "y": [int(value) for value in counts],
            }
        )

    if not summary:
        warnings.append("Não há colunas numéricas na seleção atual.")

    return (
        {
            "overview": {
                "rows_original": len(dataframe),
                "rows_analyzed": len(selected),
                "columns_analyzed": len(selected.columns),
                "numeric_columns": len(numeric.columns),
                "categorical_columns": len(categorical.columns),
                "missing_cells": int(selected.isna().sum().sum()),
            },
            "numeric_summary": summary,
            "categorical_summary": categorical_summary,
            "missing": missing,
            "correlations": correlations,
            "histograms": histograms,
            "interpretation": [
                "A média resume o valor central, enquanto o desvio padrão mostra a dispersão em torno dela.",
                "Valores discrepantes foram sinalizados pela regra do intervalo interquartil (1,5 × IQR); eles não foram removidos.",
                "Correlação descreve associação linear e, isoladamente, não demonstra causa e efeito.",
            ],
        },
        warnings,
    )
