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
    requested_metrics = set(request.metrics)

    summary: list[dict] = []
    for column in numeric.columns:
        series = numeric[column].dropna()
        if series.empty:
            continue
        q1, median, q3 = series.quantile([0.25, 0.5, 0.75])
        iqr = q3 - q1
        outliers = int(((series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)).sum())
        modes = series.mode()
        values = {
            "count": int(series.count()),
            "missing": int(selected[column].isna().sum()),
            "unique": int(series.nunique()),
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
        row = {"column": column}
        for metric in ("count", "missing", "unique", "mean", "median", "mode", "std", "variance"):
            if metric in requested_metrics:
                row[metric] = values[metric]
        if "min_max" in requested_metrics:
            row["minimum"] = values["minimum"]
            row["maximum"] = values["maximum"]
        if "quartiles" in requested_metrics:
            row["q1"] = values["q1"]
            row["q3"] = values["q3"]
        if "outliers" in requested_metrics:
            row["outliers_iqr"] = values["outliers_iqr"]
        summary.append(row)

    categorical_summary: list[dict] = []
    for column in categorical.columns:
        series = categorical[column]
        counts = series.astype("string").fillna("Ausente").value_counts().head(10)
        mode = series.mode(dropna=True)
        row = {
            "column": column,
            "top_values": [
                {"value": str(key), "count": int(value)}
                for key, value in counts.items()
            ],
        }
        if "count" in requested_metrics:
            row["count"] = int(series.notna().sum())
        if "missing" in requested_metrics:
            row["missing"] = int(series.isna().sum())
        if "unique" in requested_metrics:
            row["unique"] = int(series.nunique(dropna=True))
        if "mode" in requested_metrics:
            row["mode"] = str(mode.iloc[0]) if not mode.empty else None
        categorical_summary.append(row)

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
        if request.include_correlations and len(numeric.columns) >= 2
        else []
    )

    histograms = []
    histogram_columns = numeric.columns[:8] if request.include_histograms else []
    for column in histogram_columns:
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

    interpretation: list[str] = []
    if {"mean", "std", "variance"} & requested_metrics:
        interpretation.append(
            "A média resume o valor central; desvio padrão e variância descrevem "
            "o afastamento dos valores em relação a ela."
        )
    if {"median", "mode"} & requested_metrics:
        interpretation.append(
            "A mediana representa o ponto central após a ordenação, enquanto a moda "
            "é o valor observado com maior frequência."
        )
    if "outliers" in requested_metrics:
        interpretation.append(
            "Valores discrepantes foram sinalizados pela regra do intervalo "
            "interquartil (1,5 × IQR); eles não foram removidos."
        )
    if request.include_correlations and correlations:
        interpretation.append(
            "Correlação descreve associação linear e, isoladamente, não demonstra "
            "causa e efeito."
        )
    if not interpretation:
        interpretation.append(
            "Os resultados exibem somente as medidas selecionadas para esta execução."
        )

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
            "settings": {
                "metrics": request.metrics,
                "include_histograms": request.include_histograms,
                "include_correlations": request.include_correlations,
                "include_missing_chart": request.include_missing_chart,
                "columns": columns,
            },
            "interpretation": interpretation,
        },
        warnings,
    )
