import math

from backend.app.analytics import difference_in_proportions
from backend.app.config import normalize_database_url
from backend.app.simulation import generate_population


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


def test_confidence_interval():
    result = difference_in_proportions(100, 20, 100, 30)

    assert math.isclose(result["uplift"], 0.1)
    assert result["ci_low"] < 0.1 < result["ci_high"]


def test_neon_url_normalization():
    raw = "postgresql://user:password@host/neondb?sslmode=require"
    normalized = normalize_database_url(raw)

    assert normalized.startswith("postgresql+psycopg://")
    assert normalized.endswith("sslmode=require")
