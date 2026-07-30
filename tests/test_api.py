"""End-to-end API tests with small controlled datasets."""

import io

import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def upload_csv(dataframe: pd.DataFrame, name: str = "dados.csv") -> str:
    content = dataframe.to_csv(index=False).encode()
    response = client.post(
        "/api/datasets/upload",
        files={"file": (name, io.BytesIO(content), "text/csv")},
    )
    assert response.status_code == 201
    return response.json()["data"]["dataset_id"]


def test_homepage_and_static_assets_are_served() -> None:
    page = client.get("/")
    css = client.get("/static/css/styles.css")
    javascript = client.get("/static/js/app.js")
    assert page.status_code == 200
    assert "Explica Dados" in page.text
    assert 'class="sidebar"' in page.text
    assert "Enviar arquivo CSV" in page.text
    assert css.status_code == 200
    assert "--color-primary: #2563eb" in css.text
    assert "--purple" not in css.text
    assert "linear-gradient" not in css.text
    assert "--sidebar-width: 248px" in css.text
    assert javascript.status_code == 200
    assert "uploadFile" in javascript.text


def test_upload_valid_csv_returns_preview_and_metadata() -> None:
    dataframe = pd.DataFrame({"valor": [1, 2, 3], "grupo": ["a", "b", None]})
    response = client.post(
        "/api/datasets/upload",
        files={"file": ("dados.csv", dataframe.to_csv(index=False), "text/csv")},
    )
    body = response.json()
    assert response.status_code == 201
    assert body["success"] is True
    assert body["data"]["rows"] == 3
    assert body["data"]["columns_count"] == 2
    assert body["data"]["columns"][0]["kind"] == "numeric"


def test_upload_rejects_non_csv_and_empty_file() -> None:
    invalid = client.post(
        "/api/datasets/upload",
        files={"file": ("dados.xlsx", b"not-a-sheet", "application/octet-stream")},
    )
    empty = client.post(
        "/api/datasets/upload",
        files={"file": ("dados.csv", b"", "text/csv")},
    )
    assert invalid.status_code == 400
    assert invalid.json()["error"]["code"] == "UNSUPPORTED_FILE_TYPE"
    assert empty.status_code == 400
    assert empty.json()["error"]["code"] == "EMPTY_FILE"


def test_upload_rejects_duplicate_headers() -> None:
    response = client.post(
        "/api/datasets/upload",
        files={"file": ("dados.csv", b"valor,valor\n1,2\n", "text/csv")},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "DUPLICATE_COLUMNS"


def test_descriptive_statistics_and_filter() -> None:
    identifier = upload_csv(
        pd.DataFrame({"valor": [1, 2, 3, 4, 100], "grupo": ["A", "A", "B", "B", "B"]})
    )
    response = client.post(
        "/api/analyses/descriptive",
        json={
            "dataset_id": identifier,
            "columns": ["valor"],
            "filters": [
                {"column": "valor", "kind": "range", "minimum": 1, "maximum": 4}
            ],
        },
    )
    body = response.json()["data"]
    assert response.status_code == 200
    assert body["overview"]["rows_analyzed"] == 4
    assert body["numeric_summary"][0]["mean"] == 2.5
    assert body["numeric_summary"][0]["median"] == 2.5


def test_time_series_is_chronological_and_evaluated() -> None:
    dates = pd.date_range("2025-01-01", periods=20, freq="D")
    identifier = upload_csv(
        pd.DataFrame({"data": dates, "valor": np.arange(20) * 2 + 5})
    )
    response = client.post(
        "/api/analyses/time-series",
        json={
            "dataset_id": identifier,
            "date_column": "data",
            "value_column": "valor",
            "frequency": "D",
            "aggregation": "mean",
            "rolling_window": 3,
            "forecast_horizon": 4,
        },
    )
    body = response.json()["data"]
    assert response.status_code == 200
    assert body["metrics"]["observations"] == 20
    assert body["evaluation"]["mae"] < 1e-8
    assert len(body["forecast"]) == 4


def test_supervised_regression_pipeline() -> None:
    rows = 60
    dataframe = pd.DataFrame(
        {
            "x": np.arange(rows),
            "categoria": ["A", "B"] * (rows // 2),
            "alvo": np.arange(rows) * 3 + 2,
        }
    )
    identifier = upload_csv(dataframe)
    response = client.post(
        "/api/analyses/supervised",
        json={
            "dataset_id": identifier,
            "target_column": "alvo",
            "feature_columns": ["x", "categoria"],
            "problem_type": "regression",
            "model": "linear",
            "test_size": 0.2,
        },
    )
    body = response.json()["data"]
    assert response.status_code == 200
    assert body["metrics"]["r2"] > 0.99
    assert body["split"]["training_rows"] == 48


def test_clustering_is_reproducible() -> None:
    dataframe = pd.DataFrame(
        {
            "x": [0, 0.1, -0.1, 0.2, -0.2, 9, 9.1, 8.9, 9.2, 8.8],
            "y": [0, -0.1, 0.2, 0.1, -0.2, 9, 8.9, 9.1, 8.8, 9.2],
        }
    )
    identifier = upload_csv(dataframe)
    payload = {
        "dataset_id": identifier,
        "feature_columns": ["x", "y"],
        "n_clusters": 2,
    }
    first = client.post("/api/analyses/clustering", json=payload)
    second = client.post("/api/analyses/clustering", json=payload)
    assert first.status_code == 200
    assert first.json()["data"]["metrics"]["silhouette"] > 0.9
    assert first.json()["data"]["profiles"] == second.json()["data"]["profiles"]


def test_missing_dataset_returns_safe_error() -> None:
    response = client.post(
        "/api/analyses/descriptive",
        json={"dataset_id": "a" * 32, "columns": []},
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DATASET_NOT_FOUND"
    assert "path" not in response.text.lower()
