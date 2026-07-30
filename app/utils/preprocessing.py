"""Filtering and column validation helpers."""

from collections.abc import Iterable

import pandas as pd

from app.core.exceptions import AppError
from app.schemas.analysis import DataFilter


def require_columns(dataframe: pd.DataFrame, columns: Iterable[str]) -> None:
    """Ensure all requested columns exist."""

    missing = [column for column in columns if column not in dataframe.columns]
    if missing:
        raise AppError(
            "COLUMN_NOT_FOUND",
            f"As colunas não foram encontradas: {', '.join(missing)}.",
            404,
        )


def apply_filters(
    dataframe: pd.DataFrame,
    filters: list[DataFilter],
) -> tuple[pd.DataFrame, list[str]]:
    """Apply validated filters to a copy-free dataframe view."""

    filtered = dataframe
    messages: list[str] = []
    require_columns(filtered, (item.column for item in filters))

    for item in filters:
        before = len(filtered)
        series = filtered[item.column]

        if item.kind == "range":
            numeric = pd.to_numeric(series, errors="coerce")
            if item.minimum is not None and item.maximum is not None:
                if item.minimum > item.maximum:
                    raise AppError(
                        "INVALID_FILTER_RANGE",
                        f"O mínimo de {item.column} não pode superar o máximo.",
                    )
            mask = pd.Series(True, index=filtered.index)
            if item.minimum is not None:
                mask &= numeric >= item.minimum
            if item.maximum is not None:
                mask &= numeric <= item.maximum
            filtered = filtered.loc[mask]
        elif item.kind == "categories":
            if not item.values:
                raise AppError(
                    "EMPTY_FILTER",
                    f"Selecione ao menos uma categoria para {item.column}.",
                )
            filtered = filtered.loc[series.astype(str).isin(item.values)]
        else:
            dates = pd.to_datetime(series, errors="coerce")
            mask = dates.notna()
            if item.start:
                start = pd.to_datetime(item.start, errors="coerce")
                if pd.isna(start):
                    raise AppError("INVALID_DATE", "A data inicial é inválida.")
                mask &= dates >= start
            if item.end:
                end = pd.to_datetime(item.end, errors="coerce")
                if pd.isna(end):
                    raise AppError("INVALID_DATE", "A data final é inválida.")
                mask &= dates <= end
            filtered = filtered.loc[mask]

        messages.append(
            f"Filtro em “{item.column}”: {before - len(filtered)} linhas ficaram fora."
        )

    if filtered.empty:
        raise AppError(
            "EMPTY_FILTER_RESULT",
            "Os filtros removeram todas as linhas. Amplie o intervalo selecionado.",
        )
    return filtered, messages

