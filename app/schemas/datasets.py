"""Schemas for dataset transformations and user-defined labels."""

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ClassificationRule(BaseModel):
    """A transparent rule that assigns one label to matching rows."""

    source_column: str = Field(min_length=1, max_length=200)
    kind: Literal["range", "categories", "contains"]
    label: str = Field(min_length=1, max_length=100)
    minimum: float | None = None
    maximum: float | None = None
    values: list[str] = Field(default_factory=list, max_length=100)
    text: str | None = Field(default=None, max_length=500)
    case_sensitive: bool = False

    @model_validator(mode="after")
    def validate_rule_parameters(self) -> "ClassificationRule":
        if self.kind == "range":
            if self.minimum is None and self.maximum is None:
                raise ValueError("Informe ao menos um limite para a faixa numérica.")
            if (
                self.minimum is not None
                and self.maximum is not None
                and self.minimum > self.maximum
            ):
                raise ValueError("O limite mínimo não pode superar o máximo.")
        elif self.kind == "categories" and not self.values:
            raise ValueError("Selecione ao menos uma categoria.")
        elif self.kind == "contains" and not (self.text or "").strip():
            raise ValueError("Informe o texto que identifica os registros.")
        return self


class ClassificationRequest(BaseModel):
    """Parameters for creating a classified dataset derived from an upload."""

    dataset_id: str = Field(min_length=8, max_length=64)
    classification_column: str = Field(min_length=1, max_length=100)
    rules: list[ClassificationRule] = Field(min_length=1, max_length=50)
    default_label: str | None = Field(default=None, max_length=100)

