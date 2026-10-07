import math

import numpy as np

from backend.app.analytics import difference_in_proportions
from backend.app.config import normalize_database_url
from backend.app.population_quality import population_diagnostics
from backend.app.reference_behavior import compare_to_real_reference, load_reference_profiles
from backend.app.simulation import (
    build_similarity_edges,
    generate_population,
    simulate_outcomes,
)


def test_population_reproducible():
    a = generate_population(100, 42)
    b = generate_population(100, 42)

    assert len(a.customers) == 100
    assert a.customers[0]["age"] == b.customers[0]["age"]
    assert a.customers[0]["city"] == b.customers[0]["city"]


def test_hidden_boundary():
    population = generate_population(20, 7)

    assert "income" not in population.customers[0]
    assert "income" in population.truth[0]


def test_confidence_interval_and_hypothesis_test():
    result = difference_in_proportions(100, 20, 100, 35)

    assert math.isclose(result["uplift"], 0.1)
    assert result["ci_low"] < 0.1 < result["ci_high"]

    hypothesis = result["hypothesis_test"]
    assert hypothesis["test"] == "Two-proportion z-test"
    assert 0 <= hypothesis["p_value"] <= 1
    assert hypothesis["p_value"] < 0.05
    assert hypothesis["significant"] is True

    power = result["power_analysis"]
    assert 0 < power["mde_absolute"] < 1
    assert 0 < power["target_power"] <= 1


def test_neon_url_normalization():
    raw = "postgresql://user:password@host/neondb?sslmode=require"
    normalized = normalize_database_url(raw)

    assert normalized.startswith("postgresql+psycopg://")
    assert normalized.endswith("sslmode=require")


def test_global_feature_network_can_connect_across_cities():
    customers = [
        {
            "id": "a",
            "age": 30,
            "gender": "Female",
            "city": "Bengaluru",
            "state": "Karnataka",
            "lat": 12.97,
            "lon": 77.59,
            "device": "Mobile",
            "customer_type": "Repeat",
            "orders": 5,
            "aov": 1100.0,
            "recency_days": 20,
            "sessions_30d": 7,
            "cart_abandonments": 2,
        },
        {
            "id": "b",
            "age": 30,
            "gender": "Female",
            "city": "Mumbai",
            "state": "Maharashtra",
            "lat": 19.07,
            "lon": 72.87,
            "device": "Mobile",
            "customer_type": "Repeat",
            "orders": 5,
            "aov": 1100.0,
            "recency_days": 20,
            "sessions_30d": 7,
            "cart_abandonments": 2,
        },
    ]

    edges = build_similarity_edges(customers, [], "observable", max_edges_per_node=1)

    assert edges
    assert any(
        edge["reasons"]["feature"] in {
            "gender",
            "device",
            "customer_type",
            "age",
            "orders",
            "aov",
            "recency",
            "sessions",
            "cart_abandonments",
        }
        for edge in edges
    )

def test_correlated_population_has_expected_structure():
    population = generate_population(2000, 123)

    income_by_id = {truth["customer_id"]: truth["income"] for truth in population.truth}
    incomes = [income_by_id[item["id"]] for item in population.customers]
    aovs = [item["aov"] for item in population.customers]
    orders = [item["orders"] for item in population.customers]
    sessions = [item["sessions_30d"] for item in population.customers]

    corr_income_aov = float(np.corrcoef(incomes, aovs)[0, 1])
    corr_orders_sessions = float(np.corrcoef(orders, sessions)[0, 1])

    assert corr_income_aov > 0.05
    assert corr_orders_sessions > 0.10


def test_population_diagnostics():
    population = generate_population(1000, 321)
    truth_by_customer = {truth["customer_id"]: truth for truth in population.truth}

    rows = [
        {**customer, "income": truth_by_customer[customer["id"]]["income"]}
        for customer in population.customers
    ]

    diagnostics = population_diagnostics(rows)

    assert diagnostics["sample_size"] == 1000
    assert 0 <= diagnostics["score"] <= 100
    assert diagnostics["checks"]


def test_real_reference_behavior_benchmark():
    population = generate_population(500, 2026)

    reference_profiles = load_reference_profiles()
    assert reference_profiles
    assert len(reference_profiles) > 0

    result = compare_to_real_reference(population.customers)

    assert result["reference_source"]["name"] == "UCI Online Retail II"
    assert result["reference_source"]["license"] == "CC BY 4.0"
    assert result["reference_source"]["sample_rows"] == 1950
    assert 0 <= result["score"] <= 100

    for metric in ("orders", "aov", "recency"):
        assert metric in result["metrics"]
        assert 0 <= result["metrics"][metric]["score"] <= 100
        assert 0 <= result["metrics"][metric]["ks_distance"] <= 1


def test_multiple_experiment_types_produce_outcomes():
    population = generate_population(150, 55)
    truth = {
        item["customer_id"]: {
            "price_sensitivity": item["price_sensitivity"],
            "novelty_preference": item["novelty_preference"],
            "beauty_affinity": item["beauty_affinity"],
            "electronics_affinity": item["electronics_affinity"],
            "grocery_affinity": item["grocery_affinity"],
        }
        for item in population.truth
    }

    customers = [
        {
            "id": item["id"],
            "age": item["age"],
            "gender": item["gender"],
            "orders": item["orders"],
            "aov": item["aov"],
            "recency_days": item["recency_days"],
            "sessions_30d": item["sessions_30d"],
            "cart_abandonments": item["cart_abandonments"],
            "device": item["device"],
            "customer_type": item["customer_type"],
        }
        for item in population.customers
    ]

    for experiment_type in (
        "Marketing campaign",
        "New UI / feature",
        "Checkout redesign",
        "Pricing / discount",
    ):
        outcomes, _ = simulate_outcomes(
            customers,
            truth,
            "General",
            experiment_type,
            0.5,
            77,
        )
        assert len(outcomes) == 150
        assert {row["arm"] for row in outcomes} == {"control", "treatment"}
