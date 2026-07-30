"""Create derived datasets with transparent user-defined classification rules."""

from pathlib import Path

import pandas as pd

from app.core.exceptions import AppError
from app.schemas.datasets import ClassificationRequest, ClassificationRule
from app.services.dataset_service import dataset_payload, store
from app.utils.preprocessing import require_columns


def _rule_mask(
    dataframe: pd.DataFrame,
    rule: ClassificationRule,
) -> pd.Series:
    """Build a boolean mask for one validated classification rule."""

    series = dataframe[rule.source_column]
    if rule.kind == "range":
        numeric = pd.to_numeric(series, errors="coerce")
        mask = numeric.notna()
        if rule.minimum is not None:
            mask &= numeric >= rule.minimum
        if rule.maximum is not None:
            mask &= numeric <= rule.maximum
        return mask
    if rule.kind == "categories":
        return series.astype("string").isin(rule.values).fillna(False)
    return (
        series.astype("string")
        .str.contains(
            rule.text or "",
            case=rule.case_sensitive,
            regex=False,
            na=False,
        )
        .fillna(False)
    )


def classify(request: ClassificationRequest) -> tuple[dict, list[str]]:
    """Create a derived dataset while preserving the source dataframe."""

    source = store.get(request.dataset_id)
    dataframe = source.dataframe
    column_name = request.classification_column.strip()
    if not column_name:
        raise AppError(
            "INVALID_CLASSIFICATION_COLUMN",
            "Informe um nome válido para a nova coluna de classificação.",
        )
    if column_name in dataframe.columns:
        raise AppError(
            "CLASSIFICATION_COLUMN_EXISTS",
            f"A coluna “{column_name}” já existe. Escolha outro nome.",
        )
    require_columns(dataframe, (rule.source_column for rule in request.rules))

    derived = dataframe.copy()
    labels = pd.Series(pd.NA, index=derived.index, dtype="string")
    rule_results: list[dict] = []
    transformations: list[str] = []

    for position, rule in enumerate(request.rules, start=1):
        mask = _rule_mask(derived, rule) & labels.isna()
        matched = int(mask.sum())
        labels.loc[mask] = rule.label.strip()
        rule_results.append(
            {
                "position": position,
                "source_column": rule.source_column,
                "kind": rule.kind,
                "label": rule.label.strip(),
                "matched_rows": matched,
            }
        )
        transformations.append(
            f"Regra {position}: “{rule.label.strip()}” foi atribuída a "
            f"{matched} registros usando a coluna “{rule.source_column}”."
        )

    classified_by_rules = int(labels.notna().sum())
    default_count = 0
    if request.default_label and request.default_label.strip():
        default_mask = labels.isna()
        default_count = int(default_mask.sum())
        labels.loc[default_mask] = request.default_label.strip()
        transformations.append(
            f"O rótulo padrão “{request.default_label.strip()}” foi atribuído "
            f"a {default_count} registros não correspondidos."
        )

    classified_total = int(labels.notna().sum())
    if classified_total == 0:
        raise AppError(
            "NO_ROWS_CLASSIFIED",
            "Nenhuma linha correspondeu às regras. Revise colunas, valores e limites.",
        )

    derived[column_name] = labels
    source_stem = Path(source.original_name).stem
    derived_name = f"{source_stem}_classificado.csv"
    transformation = (
        f"Foi criada a coluna “{column_name}” por classificação definida pelo usuário. "
        "O conjunto original foi preservado."
    )
    dataset = store.add(
        derived_name,
        derived,
        parent_identifier=source.identifier,
        transformations=(*source.transformations, transformation, *transformations),
    )
    unclassified = int(labels.isna().sum())
    warnings: list[str] = []
    if unclassified:
        warnings.append(
            f"{unclassified} registros permaneceram sem classificação. "
            "Você pode criar novas regras ou definir um rótulo padrão."
        )

    return (
        dataset_payload(dataset)
        | {
            "classification": {
                "column": column_name,
                "classified_rows": classified_total,
                "unclassified_rows": unclassified,
                "classified_by_rules": classified_by_rules,
                "default_label_rows": default_count,
                "rules": rule_results,
            }
        },
        warnings,
    )

