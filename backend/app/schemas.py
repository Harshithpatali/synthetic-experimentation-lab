from typing import Literal

from pydantic import BaseModel, Field


Category = Literal["Beauty", "Electronics", "Grocery"]


class PopulationCreate(BaseModel):
    size: int = Field(1500, ge=100, le=5000)
    seed: int = Field(42, ge=0)


class ExperimentCreate(BaseModel):
    population_id: str = Field(min_length=1, max_length=36)
    name: str = Field("Virtual Experiment", min_length=1, max_length=160)
    category: Category = "Beauty"
    treatment_share: float = Field(0.5, gt=0.1, lt=0.9)
    seed: int = Field(42, ge=0)
