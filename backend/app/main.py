from contextlib import asynccontextmanager
import uuid

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import insert, text
from sqlalchemy.orm import Session

from .analytics import difference_in_proportions, segment_results
from .config import CORS_ORIGINS
from .db import Base, engine, get_db
from .models import (
    Customer,
    CustomerEdge,
    Experiment,
    ExperimentOutcome,
    PopulationRun,
    SegmentResult,
    SimulatorTruth,
)
from .schemas import ExperimentCreate, PopulationCreate
from .simulation import build_similarity_edges, generate_population, simulate_outcomes


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Keep schema initialization automatic so a fresh Neon database can deploy
    # without a separate migration runner on the free Render plan.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Synthetic Experimentation Lab API",
    version="2.1.0",
    description="Test experiments on a synthetic population before exposing real customers.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if CORS_ORIGINS == ["*"] else CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "service": "synthetic-experimentation-lab",
        "backend": "FastAPI",
        "database": "Neon PostgreSQL",
        "deployment": "Render",
        "status": "ok",
    }


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}


@app.post("/population/generate")
def create_population(req: PopulationCreate, db: Session = Depends(get_db)):
    population_id = str(uuid.uuid4())
    population = generate_population(req.size, req.seed)

    db.add(
        PopulationRun(
            id=population_id,
            seed=req.seed,
            size=req.size,
            config={"hidden_variables_internal": True},
        )
    )

    # Core/PostgreSQL executemany inserts are much faster than creating
    # thousands of SQLAlchemy ORM objects one at a time.
    db.execute(
        insert(Customer),
        [{**customer, "population_id": population_id} for customer in population.customers],
    )
    db.execute(
        insert(SimulatorTruth),
        [{**truth, "population_id": population_id} for truth in population.truth],
    )

    for view in ("observable", "truth"):
        edges = build_similarity_edges(population.customers, population.truth, view)
        db.execute(
            insert(CustomerEdge),
            [{**edge, "population_id": population_id} for edge in edges],
        )

    db.commit()

    return {
        "population_id": population_id,
        "size": req.size,
        "seed": req.seed,
    }


@app.get("/population/{population_id}")
def get_population(
    population_id: str,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Customer)
        .filter(Customer.population_id == population_id)
        .limit(limit)
        .all()
    )

    if not rows:
        raise HTTPException(status_code=404, detail="Population not found")

    fields = [
        "id",
        "age",
        "gender",
        "city",
        "state",
        "lat",
        "lon",
        "device",
        "customer_type",
        "orders",
        "aov",
        "recency_days",
        "sessions_30d",
        "cart_abandonments",
    ]

    return {
        "population_id": population_id,
        "rows": [{field: getattr(row, field) for field in fields} for row in rows],
    }


@app.get("/network")
def network(
    population_id: str,
    view: str = Query("observable", pattern="^(observable|truth)$"),
    limit: int = Query(3000, ge=1, le=10000),
    db: Session = Depends(get_db),
):
    edges = (
        db.query(CustomerEdge)
        .filter(
            CustomerEdge.population_id == population_id,
            CustomerEdge.view == view,
        )
        .limit(limit)
        .all()
    )

    return {
        "population_id": population_id,
        "view": view,
        "semantic": (
            "An edge means measurable evidence of similarity. "
            "No edge does not mean no similarity."
        ),
        "edges": [
            {
                "source": edge.source_id,
                "target": edge.target_id,
                "weight": edge.weight,
                "reasons": edge.reasons,
            }
            for edge in edges
        ],
    }


@app.get("/graph/analytics")
def graph_analytics(
    population_id: str,
    view: str = Query("observable", pattern="^(observable|truth)$"),
    db: Session = Depends(get_db),
):
    edges = (
        db.query(CustomerEdge)
        .filter(
            CustomerEdge.population_id == population_id,
            CustomerEdge.view == view,
        )
        .all()
    )

    weighted_degree: dict[str, float] = {}
    nodes: set[str] = set()

    for edge in edges:
        nodes.add(edge.source_id)
        nodes.add(edge.target_id)
        weighted_degree[edge.source_id] = (
            weighted_degree.get(edge.source_id, 0.0) + edge.weight
        )
        weighted_degree[edge.target_id] = (
            weighted_degree.get(edge.target_id, 0.0) + edge.weight
        )

    node_count = len(nodes)
    edge_count = len(edges)
    density = (
        edge_count / (node_count * (node_count - 1))
        if node_count > 1
        else 0.0
    )
    top = sorted(
        weighted_degree.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:10]

    return {
        "population_id": population_id,
        "view": view,
        "nodes": node_count,
        "edges": edge_count,
        "density": density,
        "top_influence": [
            {"customer_id": customer_id, "weighted_degree": degree}
            for customer_id, degree in top
        ],
        "note": "Network centrality is not causal influence.",
    }


@app.post("/experiments/simulate")
def run_experiment(req: ExperimentCreate, db: Session = Depends(get_db)):
    customers = (
        db.query(Customer)
        .filter(Customer.population_id == req.population_id)
        .all()
    )
    truths = (
        db.query(SimulatorTruth)
        .filter(SimulatorTruth.population_id == req.population_id)
        .all()
    )

    if not customers:
        raise HTTPException(status_code=404, detail="Population not found")

    truth_by_customer = {
        truth.customer_id: {
            "price_sensitivity": truth.price_sensitivity,
            "novelty_preference": truth.novelty_preference,
            "beauty_affinity": truth.beauty_affinity,
            "electronics_affinity": truth.electronics_affinity,
            "grocery_affinity": truth.grocery_affinity,
        }
        for truth in truths
    }

    customer_dicts = [
        {
            "id": customer.id,
            "age": customer.age,
            "gender": customer.gender,
            "orders": customer.orders,
            "aov": customer.aov,
            "recency_days": customer.recency_days,
            "sessions_30d": customer.sessions_30d,
            "customer_type": customer.customer_type,
        }
        for customer in customers
    ]

    missing_truth = [customer.id for customer in customers if customer.id not in truth_by_customer]
    if missing_truth:
        raise HTTPException(
            status_code=500,
            detail="Population is missing simulator truth rows.",
        )

    outcomes, segments = simulate_outcomes(
        customer_dicts,
        truth_by_customer,
        req.category,
        req.treatment_share,
        req.seed,
    )

    experiment_id = str(uuid.uuid4())

    db.add(
        Experiment(
            id=experiment_id,
            population_id=req.population_id,
            name=req.name,
            category=req.category,
            treatment_share=req.treatment_share,
            seed=req.seed,
            config={
                "synthetic": True,
                "hidden_variables_used": True,
            },
        )
    )

    db.execute(
        insert(ExperimentOutcome),
        [
            {
                "id": str(uuid.uuid4()),
                "experiment_id": experiment_id,
                **outcome,
            }
            for outcome in outcomes
        ],
    )

    segment_rows = segment_results(segments)
    if segment_rows:
        db.execute(
            insert(SegmentResult),
            [
                {
                    "id": str(uuid.uuid4()),
                    "experiment_id": experiment_id,
                    **row,
                }
                for row in segment_rows
            ],
        )

    control = [outcome for outcome in outcomes if outcome["arm"] == "control"]
    treatment = [outcome for outcome in outcomes if outcome["arm"] == "treatment"]

    stats = difference_in_proportions(
        len(control),
        sum(outcome["converted"] for outcome in control),
        len(treatment),
        sum(outcome["converted"] for outcome in treatment),
    )

    db.commit()

    control_revenue = sum(outcome["revenue"] for outcome in control)
    treatment_revenue = sum(outcome["revenue"] for outcome in treatment)

    return {
        "experiment_id": experiment_id,
        "population_id": req.population_id,
        "control": {
            "n": len(control),
            "conversion_rate": stats["control_rate"],
            "revenue": control_revenue,
            "revenue_per_customer": (
                control_revenue / len(control) if control else 0.0
            ),
        },
        "treatment": {
            "n": len(treatment),
            "conversion_rate": stats["treatment_rate"],
            "revenue": treatment_revenue,
            "revenue_per_customer": (
                treatment_revenue / len(treatment) if treatment else 0.0
            ),
        },
        "absolute_uplift": stats["uplift"],
        "relative_uplift": (
            stats["uplift"] / stats["control_rate"]
            if stats["control_rate"]
            else None
        ),
        "ci_95": [stats["ci_low"], stats["ci_high"]],
        "segments": segment_rows,
        "interpretation": (
            "The 95% interval reflects randomization/sampling variability in "
            "the synthetic run, not simulator-assumption uncertainty. "
            "A positive synthetic result supports considering a real-world "
            "pilot; it does not prove the same effect will occur on real customers."
        ),
    }


@app.get("/experiments")
def experiments(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Experiment)
        .order_by(Experiment.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "experiment_id": row.id,
            "name": row.name,
            "category": row.category,
            "population_id": row.population_id,
            "seed": row.seed,
            "created_at": row.created_at,
        }
        for row in rows
    ]
