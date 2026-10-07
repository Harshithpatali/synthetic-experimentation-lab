from contextlib import asynccontextmanager
import gc
import uuid

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import insert, text
from sqlalchemy.orm import Session

from .analytics import difference_in_proportions, segment_results
from .population_quality import population_diagnostics
from .reference_behavior import compare_to_real_reference, reference_summary
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
from .simulation import generate_population, iter_similarity_edges, simulate_outcomes


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Keep schema initialization automatic so a fresh Neon database can deploy
    # without a separate migration runner on the free Render plan.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Synthetic Experimentation Lab API",
    version="2.2.0",
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
            config={
                "hidden_variables_internal": True,
                "generator_version": "latent-correlated-v2",
                "network_mode": "on-demand",
            },
        )
    )
    db.flush()

    # Keep database writes bounded. The synthetic population is generated in
    # NumPy arrays, then inserted in small batches to avoid a second large
    # Python heap spike.
    def insert_in_batches(model, rows, batch_size=2000):
        batch = []
        for row in rows:
            payload = dict(row)
            payload["population_id"] = population_id
            batch.append(payload)

            if len(batch) >= batch_size:
                db.execute(insert(model), batch)
                batch.clear()

        if batch:
            db.execute(insert(model), batch)

    insert_in_batches(Customer, population.customers)
    insert_in_batches(SimulatorTruth, population.truth)

    db.commit()

    return {
        "population_id": population_id,
        "size": req.size,
        "seed": req.seed,
        "network_edges": 0,
        "network_status": "on-demand",
    }


@app.post("/population/{population_id}/network/rebuild")
def rebuild_population_network(
    population_id: str,
    db: Session = Depends(get_db),
):
    """
    Rebuild the observable network for an existing population.

    Rows and graph edges are processed with bounded memory so older 30k
    populations can be rebuilt on the small Render instance as well.
    """
    rows = (
        db.query(
            Customer.id,
            Customer.age,
            Customer.gender,
            Customer.city,
            Customer.state,
            Customer.device,
            Customer.customer_type,
            Customer.orders,
            Customer.aov,
            Customer.recency_days,
            Customer.sessions_30d,
            Customer.cart_abandonments,
        )
        .filter(Customer.population_id == population_id)
        .yield_per(2000)
    )

    customer_dicts = [
        {
            "id": row.id,
            "age": row.age,
            "gender": row.gender,
            "city": row.city,
            "state": row.state,
            "device": row.device,
            "customer_type": row.customer_type,
            "orders": row.orders,
            "aov": row.aov,
            "recency_days": row.recency_days,
            "sessions_30d": row.sessions_30d,
            "cart_abandonments": row.cart_abandonments,
        }
        for row in rows
    ]

    if not customer_dicts:
        raise HTTPException(status_code=404, detail="Population not found")

    db.query(CustomerEdge).filter(
        CustomerEdge.population_id == population_id,
        CustomerEdge.view == "observable",
    ).delete(synchronize_session=False)

    edge_batch = []
    edges_inserted = 0

    for edge in iter_similarity_edges(
        customer_dicts,
        [],
        "observable",
        max_edges_per_node=1,
    ):
        edge["population_id"] = population_id
        edge_batch.append(edge)

        if len(edge_batch) >= 2000:
            db.execute(insert(CustomerEdge), edge_batch)
            edges_inserted += len(edge_batch)
            edge_batch.clear()

    if edge_batch:
        db.execute(insert(CustomerEdge), edge_batch)
        edges_inserted += len(edge_batch)

    del customer_dicts
    gc.collect()
    db.commit()

    return {
        "population_id": population_id,
        "edges_rebuilt": edges_inserted,
        "network": "global cross-city feature similarity",
    }


@app.get("/population/{population_id}/diagnostics")
def population_diagnostics_endpoint(
    population_id: str,
    db: Session = Depends(get_db),
):
    """
    Return generator-consistency diagnostics for an existing population.

    Income is joined internally because it is part of the hidden simulator
    state; it is used only for diagnostics and is never returned to the
    company-facing population payload.
    """
    rows = (
        db.query(
            Customer,
            SimulatorTruth.income,
        )
        .join(
            SimulatorTruth,
            SimulatorTruth.customer_id == Customer.id,
        )
        .filter(Customer.population_id == population_id)
        .all()
    )

    if not rows:
        raise HTTPException(status_code=404, detail="Population not found")

    customers = []
    for customer, income in rows:
        customers.append(
            {
                "age": customer.age,
                "city": customer.city,
                "state": customer.state,
                "device": customer.device,
                "gender": customer.gender,
                "customer_type": customer.customer_type,
                "orders": customer.orders,
                "aov": customer.aov,
                "recency_days": customer.recency_days,
                "sessions_30d": customer.sessions_30d,
                "cart_abandonments": customer.cart_abandonments,
                "income": income,
            }
        )

    diagnostics = population_diagnostics(customers)
    diagnostics["population_id"] = population_id
    diagnostics["generator_version"] = "latent-correlated-v2"
    return diagnostics


@app.get("/population/{population_id}/reference-behavior")
def population_reference_behavior(
    population_id: str,
    db: Session = Depends(get_db),
):
    """
    Compare shared transaction behavior with the bundled real-data reference.

    The endpoint deliberately uses only observable fields shared by the
    reference dataset: orders, AOV and recency. It never exposes simulator
    truth variables.
    """
    rows = (
        db.query(Customer)
        .filter(Customer.population_id == population_id)
        .all()
    )

    if not rows:
        raise HTTPException(status_code=404, detail="Population not found")

    customers = [
        {
            "orders": customer.orders,
            "aov": customer.aov,
            "recency_days": customer.recency_days,
        }
        for customer in rows
    ]

    result = compare_to_real_reference(customers)
    result["population_id"] = population_id
    return result


@app.get("/reference-behavior/summary")
def reference_behavior_summary():
    """Return metadata for the bundled real behavioral reference."""
    return reference_summary()


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



@app.get("/population/{population_id}/map")
def population_map(
    population_id: str,
    limit: int = Query(30000, ge=1, le=30000),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(
            Customer.id,
            Customer.lat,
            Customer.lon,
            Customer.city,
            Customer.state,
            Customer.gender,
            Customer.customer_type,
        )
        .filter(Customer.population_id == population_id)
        .limit(limit)
        .all()
    )

    if not rows:
        raise HTTPException(status_code=404, detail="Population not found")

    return {
        "population_id": population_id,
        "rows": [
            {
                "id": row.id,
                "lat": row.lat,
                "lon": row.lon,
                "city": row.city,
                "state": row.state,
                "gender": row.gender,
                "customer_type": row.customer_type,
            }
            for row in rows
        ],
    }


@app.get("/network")
def network(
    population_id: str,
    view: str = Query("observable", pattern="^(observable|truth)$"),
    limit: int = Query(9000, ge=1, le=30000),
    features: str | None = Query(
        None,
        description="Comma-separated observable edge features to include.",
    ),
    db: Session = Depends(get_db),
):
    all_features = [
        "gender",
        "device",
        "customer_type",
        "age",
        "orders",
        "aov",
        "recency",
        "sessions",
        "cart_abandonments",
    ]

    selected_features = (
        [item.strip() for item in features.split(",") if item.strip()]
        if features
        else all_features
    )
    selected_features = [
        feature for feature in selected_features if feature in all_features
    ]

    if not selected_features:
        return {
            "population_id": population_id,
            "view": view,
            "semantic": (
                "An edge means measurable evidence of similarity. "
                "No edge does not mean no similarity."
            ),
            "edges": [],
        }

    per_feature_limit = max(
        1,
        (limit + len(selected_features) - 1) // len(selected_features),
    )

    edges = []
    for feature in selected_features:
        feature_edges = (
            db.query(CustomerEdge)
            .filter(
                CustomerEdge.population_id == population_id,
                CustomerEdge.view == view,
                CustomerEdge.reasons["feature"].as_string() == feature,
            )
            .order_by(CustomerEdge.weight.desc())
            .limit(per_feature_limit)
            .all()
        )
        edges.extend(feature_edges)

    edges = sorted(
        edges,
        key=lambda edge: float(edge.weight),
        reverse=True,
    )[:limit]

    payload = []
    for edge in edges:
        reason = edge.reasons if isinstance(edge.reasons, dict) else {}
        payload.append(
            {
                "source": edge.source_id,
                "target": edge.target_id,
                "weight": edge.weight,
                "feature": reason.get("feature", "unknown"),
                "feature_label": reason.get("label", "Similarity"),
                "reasons": reason.get("evidence", edge.reasons),
            }
        )

    return {
        "population_id": population_id,
        "view": view,
        "features": selected_features,
        "semantic": (
            "An edge means measurable evidence of observable similarity. "
            "Edges are global across the full customer population and are "
            "not restricted to customers in the same city."
        ),
        "edges": payload,
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
            "cart_abandonments": customer.cart_abandonments,
            "device": customer.device,
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
        req.experiment_type,
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
                "experiment_type": req.experiment_type,
                "product": req.product,
                "hypothesis": req.hypothesis,
                "control_experience": req.control_experience,
                "offer": req.offer,
                "success_metric": req.success_metric,
                "target_segment": req.target_segment,
            },
        )
    )
    db.flush()

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



@app.get("/experiments/{experiment_id}")
def experiment_detail(
    experiment_id: str,
    db: Session = Depends(get_db),
):
    experiment = (
        db.query(Experiment)
        .filter(Experiment.id == experiment_id)
        .first()
    )
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    outcomes = (
        db.query(ExperimentOutcome)
        .filter(ExperimentOutcome.experiment_id == experiment_id)
        .all()
    )
    segment_rows = (
        db.query(SegmentResult)
        .filter(SegmentResult.experiment_id == experiment_id)
        .order_by(SegmentResult.uplift.desc())
        .all()
    )

    control = [item for item in outcomes if item.arm == "control"]
    treatment = [item for item in outcomes if item.arm == "treatment"]

    stats = difference_in_proportions(
        len(control),
        sum(item.converted for item in control),
        len(treatment),
        sum(item.converted for item in treatment),
    )

    control_revenue = sum(item.revenue for item in control)
    treatment_revenue = sum(item.revenue for item in treatment)

    return {
        "experiment_id": experiment.id,
        "name": experiment.name,
        "category": experiment.category,
        "population_id": experiment.population_id,
        "treatment_share": experiment.treatment_share,
        "seed": experiment.seed,
        "created_at": experiment.created_at,
        "config": experiment.config,
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
                treatment_revenue / len(treatment)
                if treatment else 0.0
            ),
        },
        "absolute_uplift": stats["uplift"],
        "relative_uplift": (
            stats["uplift"] / stats["control_rate"]
            if stats["control_rate"] else None
        ),
        "ci_95": [stats["ci_low"], stats["ci_high"]],
        "segments": [
            {
                "segment": row.segment,
                "control_rate": row.control_rate,
                "treatment_rate": row.treatment_rate,
                "uplift": row.uplift,
                "n": row.n,
            }
            for row in segment_rows
        ],
        "interpretation": (
            "The 95% interval reflects randomization/sampling variability "
            "in the synthetic run, not simulator-assumption uncertainty. "
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
