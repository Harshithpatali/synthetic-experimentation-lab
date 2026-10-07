from pydantic import BaseModel, Field

class PopulationCreate(BaseModel):
    size: int = Field(1500, ge=100, le=10000)
    seed: int = 42

class ExperimentCreate(BaseModel):
    population_id: str
    name: str = "Virtual Experiment"
    category: str = "Beauty"
    treatment_share: float = Field(.5, gt=.1, lt=.9)
    seed: int = 42
