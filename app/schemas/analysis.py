"""Schemas for data analysis requests."""

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class DataFilter(BaseModel):
    """Filter applied to a dataset without mutating its original data."""

    column: str
    kind: Literal["range", "categories", "date"]
    minimum: float | None = None
    maximum: float | None = None
    values: list[str] = Field(default_factory=list)
    start: str | None = None
    end: str | None = None


class AnalysisBase(BaseModel):
    """Fields shared by analysis requests."""

    dataset_id: str = Field(min_length=8, max_length=64)
    filters: list[DataFilter] = Field(default_factory=list, max_length=20)


class DescriptiveRequest(AnalysisBase):
    """Descriptive analysis parameters."""

    columns: list[str] = Field(default_factory=list, max_length=50)
    metrics: list[
        Literal[
            "count",
            "missing",
            "unique",
            "mean",
            "median",
            "mode",
            "std",
            "variance",
            "min_max",
            "quartiles",
            "outliers",
        ]
    ] = Field(
        default_factory=lambda: [
            "count",
            "missing",
            "unique",
            "mean",
            "median",
            "mode",
            "std",
            "variance",
            "min_max",
            "quartiles",
            "outliers",
        ],
        min_length=1,
        max_length=11,
    )
    include_histograms: bool = True
    include_correlations: bool = True
    include_missing_chart: bool = True


class TimeSeriesRequest(AnalysisBase):
    """Time-series analysis parameters."""

    date_column: str
    value_column: str
    frequency: Literal["auto", "D", "W", "ME", "QE", "YE"] = "auto"
    aggregation: Literal["mean", "sum", "median"] = "mean"
    rolling_window: int = Field(default=7, ge=2, le=365)
    forecast_horizon: int = Field(default=0, ge=0, le=90)


class SupervisedRequest(AnalysisBase):
    """Supervised learning parameters."""

    target_column: str
    feature_columns: list[str] = Field(min_length=1, max_length=50)
    problem_type: Literal["classification", "regression"]
    model: Literal["logistic", "linear", "decision_tree", "random_forest"]
    test_size: float = Field(default=0.2, ge=0.1, le=0.4)

    @model_validator(mode="after")
    def validate_model_problem(self) -> "SupervisedRequest":
        valid = {
            "classification": {"logistic", "decision_tree", "random_forest"},
            "regression": {"linear", "decision_tree", "random_forest"},
        }
        if self.model not in valid[self.problem_type]:
            raise ValueError("O modelo selecionado não é compatível com o problema.")
        if self.target_column in self.feature_columns:
            raise ValueError("A variável alvo não pode ser usada como preditora.")
        return self


class ClusteringRequest(AnalysisBase):
    """K-Means clustering parameters."""

    feature_columns: list[str] = Field(min_length=2, max_length=20)
    n_clusters: int = Field(default=3, ge=2, le=10)
