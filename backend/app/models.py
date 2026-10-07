from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class PopulationRun(Base):
    __tablename__="population_runs"
    id:Mapped[str]=mapped_column(String(36),primary_key=True)
    seed:Mapped[int]=mapped_column(Integer)
    size:Mapped[int]=mapped_column(Integer)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))
    config:Mapped[dict]=mapped_column(JSON)

class Customer(Base):
    __tablename__="customers"
    id:Mapped[str]=mapped_column(String(36),primary_key=True)
    population_id:Mapped[str]=mapped_column(ForeignKey("population_runs.id",ondelete="CASCADE"),index=True)
    age:Mapped[int]=mapped_column(Integer); gender:Mapped[str]=mapped_column(String(20)); city:Mapped[str]=mapped_column(String(80)); state:Mapped[str]=mapped_column(String(80))
    lat:Mapped[float]=mapped_column(Float); lon:Mapped[float]=mapped_column(Float); device:Mapped[str]=mapped_column(String(20)); customer_type:Mapped[str]=mapped_column(String(30))
    orders:Mapped[int]=mapped_column(Integer); aov:Mapped[float]=mapped_column(Float); recency_days:Mapped[int]=mapped_column(Integer); sessions_30d:Mapped[int]=mapped_column(Integer); cart_abandonments:Mapped[int]=mapped_column(Integer)

class SimulatorTruth(Base):
    __tablename__="simulator_truth"
    id:Mapped[str]=mapped_column(String(36),primary_key=True)
    population_id:Mapped[str]=mapped_column(ForeignKey("population_runs.id",ondelete="CASCADE"),index=True)
    customer_id:Mapped[str]=mapped_column(ForeignKey("customers.id",ondelete="CASCADE"),index=True)
    profession:Mapped[str]=mapped_column(String(40)); income:Mapped[float]=mapped_column(Float); price_sensitivity:Mapped[float]=mapped_column(Float); novelty_preference:Mapped[float]=mapped_column(Float); risk_preference:Mapped[float]=mapped_column(Float)
    beauty_affinity:Mapped[float]=mapped_column(Float); electronics_affinity:Mapped[float]=mapped_column(Float); grocery_affinity:Mapped[float]=mapped_column(Float)

class CustomerEdge(Base):
    __tablename__="customer_edges"
    id:Mapped[str]=mapped_column(String(36),primary_key=True)
    population_id:Mapped[str]=mapped_column(ForeignKey("population_runs.id",ondelete="CASCADE"),index=True)
    source_id:Mapped[str]=mapped_column(String(36),index=True); target_id:Mapped[str]=mapped_column(String(36),index=True); weight:Mapped[float]=mapped_column(Float); view:Mapped[str]=mapped_column(String(20)); reasons:Mapped[list]=mapped_column(JSON)

class Experiment(Base):
    __tablename__="experiments"
    id:Mapped[str]=mapped_column(String(36),primary_key=True)
    population_id:Mapped[str]=mapped_column(ForeignKey("population_runs.id",ondelete="CASCADE"),index=True)
    name:Mapped[str]=mapped_column(String(160)); category:Mapped[str]=mapped_column(String(40)); treatment_share:Mapped[float]=mapped_column(Float); seed:Mapped[int]=mapped_column(Integer)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc)); config:Mapped[dict]=mapped_column(JSON)

class ExperimentOutcome(Base):
    __tablename__="experiment_outcomes"
    id:Mapped[str]=mapped_column(String(36),primary_key=True)
    experiment_id:Mapped[str]=mapped_column(ForeignKey("experiments.id",ondelete="CASCADE"),index=True)
    customer_id:Mapped[str]=mapped_column(String(36),index=True); arm:Mapped[str]=mapped_column(String(12)); converted:Mapped[bool]=mapped_column(Boolean); revenue:Mapped[float]=mapped_column(Float)

class SegmentResult(Base):
    __tablename__="segment_results"
    id:Mapped[str]=mapped_column(String(36),primary_key=True)
    experiment_id:Mapped[str]=mapped_column(ForeignKey("experiments.id",ondelete="CASCADE"),index=True)
    segment:Mapped[str]=mapped_column(String(80)); control_rate:Mapped[float]=mapped_column(Float); treatment_rate:Mapped[float]=mapped_column(Float); uplift:Mapped[float]=mapped_column(Float); n:Mapped[int]=mapped_column(Integer)
