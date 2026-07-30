"""Dataset upload routes."""

from fastapi import APIRouter, File, UploadFile

from app.core.config import MAX_UPLOAD_BYTES
from app.schemas.datasets import ClassificationRequest
from app.schemas.responses import success_response
from app.services.classification_service import classify
from app.services.dataset_service import ingest_csv

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
