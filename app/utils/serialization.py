"""Safe conversion of analytical values to JSON-compatible objects."""

from typing import Any

import numpy as np
import pandas as pd


def json_value(value: Any) -> Any:
    """Convert pandas and NumPy scalars to JSON-safe values."""

    if value is None or pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    return value


def records(dataframe: pd.DataFrame) -> list[dict[str, Any]]:
    """Serialize a dataframe as clean records."""

    return [
        {str(key): json_value(value) for key, value in row.items()}
        for row in dataframe.to_dict(orient="records")
    ]

