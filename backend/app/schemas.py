from typing import Literal

from pydantic import BaseModel, Field


Category = Literal[
    "General",
    "Beauty",
    "Electronics",
    "Grocery",
    "Fashion",
    "Home",
    "Sports",
    "Travel",
    "Finance",
    "SaaS",
]

ExperimentType = Literal[
    "Marketing campaign",
    "Product promotion",
    "New UI / feature",
    "Checkout redesign",
    "Pricing / discount",
    "Recommendation / personalization",
    "Messaging / copy",
    "Retention / loyalty",
    "Search / discovery",
    "Other",
]


class PopulationCreate(BaseModel):
    size: int = Field(30000, ge=100, le=30000)
    seed: int = Field(42, ge=0)


class ExperimentCreate(BaseModel):
    population_id: str = Field(min_length=1, max_length=36)
    name: str = Field("Virtual Experiment", min_length=1, max_length=160)
    experiment_type: ExperimentType = "Marketing campaign"
    product: str = Field("General product", min_length=1, max_length=160)
    hypothesis: str = Field("", max_length=500)
    control_experience: str = Field(
        "Current customer experience.",
        max_length=500,
    )
    offer: str = Field(
        "Proposed treatment, campaign, UI, checkout, pricing, or product change.",
        max_length=500,
    )
    success_metric: str = Field("Conversion rate", max_length=160)
    target_segment: str = Field("All customers", max_length=160)
    category: Category = "General"
    treatment_share: float = Field(0.5, gt=0.1, lt=0.9)
    seed: int = Field(42, ge=0)
