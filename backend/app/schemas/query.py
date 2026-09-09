from datetime import date
from typing import Any
from pydantic import BaseModel, Field, model_validator


class Filters(BaseModel):
    start: date | None = None
    end: date | None = None
    region: str | None = Field(default=None,max_length=128)
    state: str | None = Field(default=None,max_length=128)
    city: str | None = Field(default=None,max_length=128)
    category: str | None = Field(default=None,max_length=128)
    brand: str | None = Field(default=None,max_length=128)
    product_id: str | None = Field(default=None,max_length=64)
    promotion_id: str | None = Field(default=None,max_length=64)

    @model_validator(mode='after')
    def ordered(self):
        if self.start and self.end and self.start > self.end:
            raise ValueError('Start date must not follow end date')
        return self


class CopilotQuery(BaseModel):
    question: str = Field(min_length=3,max_length=1000)
    filters: Filters = Field(default_factory=Filters)


class AnalyticsResponse(BaseModel):
    data: Any
    total: int | None = None
    rows: int
    source: list[str]


class CopilotResponse(BaseModel):
    answer: str
    key_metrics: dict
    supporting_evidence: list | dict
    recommendation: str
    caveats: list[str]
    mode: str
    operation: str | None = None
    filters: dict | None = None
