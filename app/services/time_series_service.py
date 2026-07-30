"""Time-series preparation, trend and simple forecast analysis."""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

from app.core.config import MAX_CHART_POINTS
from app.core.exceptions import AppError
from app.schemas.analysis import TimeSeriesRequest
from app.services.dataset_service import store
from app.utils.preprocessing import apply_filters, require_columns


def analyze(request: TimeSeriesRequest) -> tuple[dict, list[str]]:
    """Analyze a validated date/value series without shuffling observations."""

    dataframe = store.get(request.dataset_id).dataframe
    filtered, warnings = apply_filters(dataframe, request.filters)
    require_columns(filtered, [request.date_column, request.value_column])
    dates = pd.to_datetime(filtered[request.date_column], errors="coerce")
    values = pd.to_numeric(filtered[request.value_column], errors="coerce")
    invalid = int((dates.isna() | values.isna()).sum())
    series = pd.DataFrame({"date": dates, "value": values}).dropna().sort_values("date")
    if invalid:
        warnings.append(
            f"Foram ignoradas {invalid} linhas com data ou valor inválido para esta análise."
        )
    if len(series) < 3:
        raise AppError(
            "INSUFFICIENT_TIME_SERIES",
            "São necessárias ao menos 3 observações temporais válidas.",
        )
    duplicate_dates = int(series["date"].duplicated().sum())
    if duplicate_dates:
        warnings.append(
            f"Há {duplicate_dates} datas repetidas; elas foram agregadas por "
            f"{request.aggregation}."
        )

    grouped = series.set_index("date")["value"]
    frequency = request.frequency
    if frequency == "auto":
        inferred = pd.infer_freq(series["date"].drop_duplicates())
        frequency = inferred if inferred in {"D", "W", "ME", "QE", "YE"} else ""
    if frequency:
        grouped = getattr(grouped.resample(frequency), request.aggregation)().dropna()
    else:
        grouped = getattr(grouped.groupby(level=0), request.aggregation)().sort_index()
        warnings.append(
            "A frequência não pôde ser identificada automaticamente; os pontos foram mantidos por data."
        )

    rolling = grouped.rolling(request.rolling_window, min_periods=1).mean()
    pct_change = grouped.pct_change().replace([np.inf, -np.inf], np.nan)
    x = np.arange(len(grouped)).reshape(-1, 1)
    trend_model = LinearRegression().fit(x, grouped.to_numpy())
    trend = trend_model.predict(x)

    metrics = {
        "observations": int(len(grouped)),
        "start": grouped.index.min().isoformat(),
        "end": grouped.index.max().isoformat(),
        "average": float(grouped.mean()),
        "minimum": float(grouped.min()),
        "maximum": float(grouped.max()),
        "total_change_percentage": (
            float((grouped.iloc[-1] / grouped.iloc[0] - 1) * 100)
            if grouped.iloc[0] != 0
            else None
        ),
        "average_period_change_percentage": (
            float(pct_change.mean() * 100) if pct_change.notna().any() else None
        ),
        "trend_per_period": float(trend_model.coef_[0]),
    }

    forecast: list[dict] = []
    evaluation = None
    if request.forecast_horizon:
        if len(grouped) < 8:
            warnings.append(
                "A previsão não foi gerada: são necessárias ao menos 8 observações."
            )
        else:
            test_count = max(2, min(len(grouped) // 5, 10))
            train_x = x[:-test_count]
            test_x = x[-test_count:]
            train_y = grouped.to_numpy()[:-test_count]
            test_y = grouped.to_numpy()[-test_count:]
            validation_model = LinearRegression().fit(train_x, train_y)
            predicted_test = validation_model.predict(test_x)
            evaluation = {
                "mae": float(mean_absolute_error(test_y, predicted_test)),
                "rmse": float(root_mean_squared_error(test_y, predicted_test)),
                "test_observations": test_count,
            }
            future_x = np.arange(
                len(grouped), len(grouped) + request.forecast_horizon
            ).reshape(-1, 1)
            future_values = trend_model.predict(future_x)
            offset = pd.tseries.frequencies.to_offset(frequency or "D")
            future_dates = pd.date_range(
                grouped.index.max() + offset,
                periods=request.forecast_horizon,
                freq=offset,
            )
            forecast = [
                {"date": date.isoformat(), "value": float(value)}
                for date, value in zip(future_dates, future_values, strict=True)
            ]
            warnings.append(
                "A previsão usa tendência linear simples e serve como referência, não como certeza sobre o futuro."
            )

    chart = pd.DataFrame(
        {
            "date": grouped.index,
            "value": grouped.values,
            "rolling": rolling.values,
            "trend": trend,
        }
    )
    if len(chart) > MAX_CHART_POINTS:
        indexes = np.linspace(0, len(chart) - 1, MAX_CHART_POINTS, dtype=int)
        chart = chart.iloc[indexes]
        warnings.append(
            f"O gráfico foi reduzido para {MAX_CHART_POINTS:,} pontos; as métricas usam a série completa."
        )

    return (
        {
            "metrics": metrics,
            "series": [
                {
                    "date": row.date.isoformat(),
                    "value": float(row.value),
                    "rolling": float(row.rolling),
                    "trend": float(row.trend),
                }
                for row in chart.itertuples(index=False)
            ],
            "forecast": forecast,
            "evaluation": evaluation,
            "settings": {
                "frequency": frequency or "por data",
                "aggregation": request.aggregation,
                "rolling_window": request.rolling_window,
            },
            "interpretation": [
                "A média móvel reduz oscilações de curto prazo e ajuda a enxergar o comportamento geral.",
                "A tendência por período resume a direção linear observada dentro da amostra.",
                "Erros de validação foram calculados preservando a ordem do tempo, sem embaralhar os dados.",
            ],
        },
        warnings,
    )

