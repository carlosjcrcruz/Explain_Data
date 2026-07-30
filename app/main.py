"""FastAPI entry point for Explica Dados."""

import logging
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import analysis, upload
from app.core.exceptions import AppError
from app.schemas.responses import error_response

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
LOGGER = logging.getLogger(__name__)
STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title="Explica Dados",
    description="Análises de dados claras, visuais e responsáveis.",
    version="1.0.0",
)
app.include_router(upload.router)
app.include_router(analysis.router)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.middleware("http")
async def operation_logging(request: Request, call_next):
    """Log safe operational metadata without dataset contents."""

    started = time.perf_counter()
    response = await call_next(request)
    duration = (time.perf_counter() - started) * 1000
    LOGGER.info(
        "%s %s status=%s duration_ms=%.1f",
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )
    return response


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(exc.code, exc.message),
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    _: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    details = "; ".join(
        f"{'.'.join(str(part) for part in error['loc'][1:])}: {error['msg']}"
        for error in exc.errors()[:5]
    )
    return JSONResponse(
        status_code=422,
        content=error_response(
            "INVALID_PARAMETERS",
            "Revise os parâmetros informados. " + details,
        ),
    )


@app.exception_handler(Exception)
async def unexpected_error_handler(_: Request, exc: Exception) -> JSONResponse:
    LOGGER.exception("Unexpected internal error: %s", type(exc).__name__)
    return JSONResponse(
        status_code=500,
        content=error_response(
            "INTERNAL_ERROR",
            "Ocorreu um erro interno inesperado. Tente novamente.",
        ),
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")

