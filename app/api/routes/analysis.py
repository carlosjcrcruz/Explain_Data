"""Analysis endpoints."""

from fastapi import APIRouter

from app.schemas.analysis import (
    ClusteringRequest,
    DescriptiveRequest,
    SupervisedRequest,
    TimeSeriesRequest,
)
from app.schemas.responses import success_response
from app.services import (
    clustering_service,
    descriptive_service,
    supervised_service,
    time_series_service,
)

router = APIRouter(prefix="/api/analyses", tags=["analyses"])


@router.post("/descriptive")
def descriptive(request: DescriptiveRequest) -> dict:
    data, warnings = descriptive_service.analyze(request)
    return success_response("Análise descritiva concluída com sucesso.", data, warnings)


@router.post("/time-series")
def time_series(request: TimeSeriesRequest) -> dict:
    data, warnings = time_series_service.analyze(request)
    return success_response("Análise temporal concluída com sucesso.", data, warnings)


@router.post("/supervised")
def supervised(request: SupervisedRequest) -> dict:
    data, warnings = supervised_service.analyze(request)
    return success_response("Modelo avaliado com sucesso.", data, warnings)


@router.post("/clustering")
def clustering(request: ClusteringRequest) -> dict:
    data, warnings = clustering_service.analyze(request)
    return success_response("Segmentação concluída com sucesso.", data, warnings)

