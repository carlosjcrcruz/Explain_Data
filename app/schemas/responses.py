"""Consistent API response helpers."""

from typing import Any


def success_response(
    message: str,
    data: dict[str, Any],
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    """Build a successful API response."""

    return {
        "success": True,
        "message": message,
        "data": data,
        "warnings": warnings or [],
    }


def error_response(code: str, message: str) -> dict[str, Any]:
    """Build a safe API error response."""

    return {
        "success": False,
        "message": "Não foi possível concluir a operação.",
        "error": {"code": code, "details": message},
    }

