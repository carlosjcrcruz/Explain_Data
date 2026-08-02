"""Dataset upload routes."""

from fastapi import APIRouter, File, UploadFile

from app.core.config import MAX_UPLOAD_BYTES
from app.schemas.datasets import ClassificationRequest
from app.schemas.responses import success_response
from app.services.classification_service import classify
from app.services.dataset_service import dataset_payload, ingest_csv, store

router = APIRouter(prefix="/api/datasets", tags=["datasets"])


@router.post("/upload", status_code=201)
async def upload_dataset(file: UploadFile = File(...)) -> dict:
    """Receive, validate and inspect a CSV dataset."""

    content = await file.read(MAX_UPLOAD_BYTES + 1)
    result = ingest_csv(file.filename or "dados.csv", content)
    warnings = result.pop("warnings")
    return success_response(
        "Arquivo validado e carregado com sucesso.",
        result,
        warnings,
    )


@router.post("/classify", status_code=201)
def classify_dataset(request: ClassificationRequest) -> dict:
    """Create a classified dataset derived from an existing upload."""

    result, warnings = classify(request)
    return success_response(
        "Dataset classificado sem alterar o arquivo original.",
        result,
        warnings,
    )


@router.get("/{dataset_id}")
def get_dataset(dataset_id: str) -> dict:
    """Return safe metadata and preview for an in-memory dataset."""

    dataset = store.get(dataset_id)
    return success_response(
        "Metadados do conjunto de dados carregados.",
        dataset_payload(dataset),
    )
