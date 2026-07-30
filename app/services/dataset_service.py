"""Secure CSV ingestion and in-memory dataset lifecycle."""

import csv
import io
import logging
from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from uuid import uuid4

import pandas as pd

from app.core.config import (
    ALLOWED_EXTENSIONS,
    MAX_COLUMNS,
    MAX_ROWS,
    MAX_UPLOAD_BYTES,
    PREVIEW_ROWS,
)
from app.core.exceptions import AppError
from app.utils.serialization import records

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class Dataset:
    """Dataset kept in process memory for the current application session."""

    identifier: str
    original_name: str
    dataframe: pd.DataFrame
    parent_identifier: str | None = None
    transformations: tuple[str, ...] = ()


class DatasetStore:
    """Thread-safe, bounded in-memory dataset registry."""

    def __init__(self, max_datasets: int = 20) -> None:
        self._datasets: dict[str, Dataset] = {}
        self._order: list[str] = []
        self._lock = RLock()
        self._max_datasets = max_datasets

    def add(
        self,
        filename: str,
        dataframe: pd.DataFrame,
        parent_identifier: str | None = None,
        transformations: tuple[str, ...] = (),
    ) -> Dataset:
        identifier = uuid4().hex
        dataset = Dataset(
            identifier,
            Path(filename).name,
            dataframe,
            parent_identifier,
            transformations,
        )
        with self._lock:
            self._datasets[identifier] = dataset
            self._order.append(identifier)
            if len(self._order) > self._max_datasets:
                oldest = self._order.pop(0)
                self._datasets.pop(oldest, None)
        return dataset

    def get(self, identifier: str) -> Dataset:
        with self._lock:
            dataset = self._datasets.get(identifier)
        if dataset is None:
            raise AppError(
                "DATASET_NOT_FOUND",
                "O conjunto de dados não existe mais. Envie o arquivo novamente.",
                404,
            )
        return dataset


store = DatasetStore()


def _decode(content: bytes) -> tuple[str, str]:
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return content.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    raise AppError(
        "INVALID_ENCODING",
        "Não foi possível identificar a codificação do arquivo.",
    )


def _separator(text: str) -> str:
    try:
        dialect = csv.Sniffer().sniff(text[:8192], delimiters=",;\t|")
        return dialect.delimiter
    except csv.Error:
        return ","


def ingest_csv(filename: str, content: bytes) -> dict:
    """Validate and parse a CSV upload without persisting its raw bytes."""

    suffix = Path(filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise AppError(
            "UNSUPPORTED_FILE_TYPE",
            "Nesta versão, envie um arquivo com extensão .csv.",
        )
    if not content:
        raise AppError("EMPTY_FILE", "O arquivo enviado está vazio.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise AppError(
            "FILE_TOO_LARGE",
            "O arquivo ultrapassa o limite de 10 MB.",
            413,
        )
    if b"\x00" in content[:8192]:
        raise AppError(
            "INVALID_FILE_CONTENT",
            "O conteúdo não parece ser um arquivo de texto CSV válido.",
        )

    text, encoding = _decode(content)
    separator = _separator(text)
    try:
        header = next(csv.reader(io.StringIO(text), delimiter=separator))
    except (csv.Error, StopIteration) as exc:
        raise AppError("MISSING_HEADER", "O arquivo não possui um cabeçalho válido.") from exc
    normalized_header = [column.strip() for column in header]
    if len(normalized_header) != len(set(normalized_header)):
        raise AppError(
            "DUPLICATE_COLUMNS",
            "O arquivo possui nomes de colunas duplicados.",
        )
    try:
        dataframe = pd.read_csv(
            io.StringIO(text),
            sep=separator,
            nrows=MAX_ROWS + 1,
            low_memory=False,
        )
    except (pd.errors.ParserError, UnicodeError, ValueError) as exc:
        LOGGER.info("CSV parsing rejected: %s", type(exc).__name__)
        raise AppError(
            "INVALID_CSV",
            "Não foi possível ler o CSV. Verifique o cabeçalho e o separador.",
        ) from exc

    if dataframe.empty and len(dataframe.columns) == 0:
        raise AppError("MISSING_HEADER", "O arquivo não possui um cabeçalho válido.")
    if len(dataframe) > MAX_ROWS:
        raise AppError(
            "TOO_MANY_ROWS",
            f"O arquivo excede o limite de {MAX_ROWS:,} linhas.",
            413,
        )
    if len(dataframe.columns) > MAX_COLUMNS:
        raise AppError(
            "TOO_MANY_COLUMNS",
            f"O arquivo excede o limite de {MAX_COLUMNS} colunas.",
            413,
        )
    if dataframe.columns.duplicated().any():
        raise AppError(
            "DUPLICATE_COLUMNS",
            "O arquivo possui nomes de colunas duplicados.",
        )

    dataframe.columns = [str(column).strip() for column in dataframe.columns]
    if any(not column for column in dataframe.columns):
        raise AppError("EMPTY_COLUMN_NAME", "Há uma coluna sem nome no cabeçalho.")

    dataset = store.add(filename, dataframe)
    empty_columns = [
        column for column in dataframe.columns if dataframe[column].isna().all()
    ]
    warnings: list[str] = []
    if empty_columns:
        warnings.append(
            "Colunas completamente vazias: " + ", ".join(empty_columns[:10]) + "."
        )
    if encoding != "utf-8":
        warnings.append(f"O arquivo foi lido usando a codificação {encoding}.")

    return dataset_payload(dataset, separator=separator, encoding=encoding) | {
        "warnings": warnings,
    }


def dataset_payload(
    dataset: Dataset,
    *,
    separator: str | None = None,
    encoding: str | None = None,
) -> dict:
    """Return consistent metadata for uploaded and derived datasets."""

    dataframe = dataset.dataframe
    payload = {
        "dataset_id": dataset.identifier,
        "filename": dataset.original_name,
        "rows": len(dataframe),
        "columns_count": len(dataframe.columns),
        "columns": column_metadata(dataframe),
        "preview": records(dataframe.head(PREVIEW_ROWS)),
        "parent_dataset_id": dataset.parent_identifier,
        "transformations": list(dataset.transformations),
    }
    if separator is not None:
        payload["separator"] = "\\t" if separator == "\t" else separator
    if encoding is not None:
        payload["encoding"] = encoding
    return payload



def column_metadata(dataframe: pd.DataFrame) -> list[dict]:
    """Describe dataframe columns without exposing full values."""

    metadata: list[dict] = []
    for column in dataframe.columns:
        series = dataframe[column]
        numeric = pd.api.types.is_numeric_dtype(series)
        date_ratio = 0.0
        if not numeric and series.notna().any():
            sample = series.dropna().head(100)
            parsed = pd.to_datetime(sample, errors="coerce", format="mixed")
            date_ratio = float(parsed.notna().mean())
        kind = "numeric" if numeric else "date_candidate" if date_ratio >= 0.8 else "categorical"
        item = {
            "name": column,
            "kind": kind,
            "dtype": str(series.dtype),
            "missing": int(series.isna().sum()),
            "unique": int(series.nunique(dropna=True)),
        }
        if numeric and series.notna().any():
            item["minimum"] = float(series.min())
            item["maximum"] = float(series.max())
        elif series.nunique(dropna=True) <= 30:
            item["sample_values"] = [
                str(value) for value in series.dropna().unique()[:30]
            ]
        metadata.append(item)
    return metadata
