from collections import Counter

import numpy as np


def _safe_corr(left, right) -> float:
    if len(left) < 2:
        return 0.0

    left_arr = np.asarray(left, dtype=float)
    right_arr = np.asarray(right, dtype=float)

    if np.std(left_arr) == 0 or np.std(right_arr) == 0:
        return 0.0

    value = np.corrcoef(left_arr, right_arr)[0, 1]
    return float(value) if np.isfinite(value) else 0.0


def population_diagnostics(customers: list[dict]) -> dict:
    """
    Validate structural properties of a generated population.

    This is a generator-consistency diagnostic, not a claim that synthetic
    data matches a real-world population. Real-world fidelity requires a
    reference dataset supplied by the company.
    """
    n = len(customers)
    if n == 0:
        return {
            "sample_size": 0,
            "score": 0.0,
            "label": "No data",
            "checks": [],
            "summary": {},
        }

    ages = [float(item["age"]) for item in customers]
    incomes = [float(item.get("income", 0.0)) for item in customers]
    orders = [float(item["orders"]) for item in customers]
    aovs = [float(item["aov"]) for item in customers]
    sessions = [float(item["sessions_30d"]) for item in customers]
    recencies = [float(item["recency_days"]) for item in customers]
    abandonments = [float(item["cart_abandonments"]) for item in customers]

    city_count = len({item["city"] for item in customers})
    state_count = len({item["state"] for item in customers})

    type_orders = {}
    for item in customers:
        type_orders.setdefault(item["customer_type"], []).append(item["orders"])

    checks = []

    checks.append(
        {
            "name": "Age coverage",
            "passed": min(ages) >= 18 and max(ages) <= 70 and np.std(ages) > 5,
            "value": f"{min(ages):.0f}–{max(ages):.0f}",
            "reason": "Age spans a broad adult population range.",
        }
    )

    checks.append(
        {
            "name": "Income ↔ AOV relationship",
            "passed": _safe_corr(incomes, aovs) > 0.12,
            "value": f"ρ={_safe_corr(incomes, aovs):.2f}",
            "reason": "Higher-income customers should tend to support higher basket values.",
        }
    )

    checks.append(
        {
            "name": "Orders ↔ sessions relationship",
            "passed": _safe_corr(orders, sessions) > 0.15,
            "value": f"ρ={_safe_corr(orders, sessions):.2f}",
            "reason": "More active buyers should generally have more sessions.",
        }
    )

    checks.append(
        {
            "name": "Engagement ↔ recency relationship",
            "passed": _safe_corr(sessions, recencies) < 0.0,
            "value": f"ρ={_safe_corr(sessions, recencies):.2f}",
            "reason": "More engaged customers should generally be more recent.",
        }
    )

    checks.append(
        {
            "name": "Cart friction signal",
            "passed": _safe_corr(sessions, abandonments) > 0.05,
            "value": f"ρ={_safe_corr(sessions, abandonments):.2f}",
            "reason": "Customers with more sessions have more opportunities to abandon.",
        }
    )

    if type_orders:
        medians = {
            key: float(np.median(values))
            for key, values in type_orders.items()
        }
        new_median = medians.get("New", 0.0)
        repeat_median = medians.get("Repeat", 0.0)
        loyal_median = medians.get("Loyal", 0.0)
        lifecycle_ok = (
            loyal_median >= repeat_median >= new_median
            and len(type_orders) >= 2
        )
    else:
        medians = {}
        lifecycle_ok = False

    checks.append(
        {
            "name": "Customer lifecycle ordering",
            "passed": lifecycle_ok,
            "value": ", ".join(
                f"{name}={value:.1f}"
                for name, value in sorted(medians.items())
            ) or "—",
            "reason": "Repeat/Loyal customers should have progressively higher order activity.",
        }
    )

    checks.append(
        {
            "name": "Geographic diversity",
            "passed": city_count >= 15 and state_count >= 8,
            "value": f"{city_count} cities / {state_count} states & UTs",
            "reason": "A national population should not collapse into a few locations.",
        }
    )

    score = 100.0 * sum(item["passed"] for item in checks) / len(checks)

    # Coarse summaries are intentionally descriptive; they are not compared
    # against real-world data.
    device_counts = Counter(item["device"] for item in customers)
    gender_counts = Counter(item["gender"] for item in customers)
    type_counts = Counter(item["customer_type"] for item in customers)

    return {
        "sample_size": n,
        "score": round(score, 1),
        "label": "Generator consistency",
        "checks": checks,
        "summary": {
            "median_age": round(float(np.median(ages)), 1),
            "median_income": round(float(np.median(incomes)), 2),
            "median_orders": round(float(np.median(orders)), 2),
            "median_aov": round(float(np.median(aovs)), 2),
            "median_sessions": round(float(np.median(sessions)), 2),
            "median_recency_days": round(float(np.median(recencies)), 2),
            "cities": city_count,
            "states_or_uts": state_count,
            "device_mix": {
                key: round(value / n, 4)
                for key, value in device_counts.items()
            },
            "gender_mix": {
                key: round(value / n, 4)
                for key, value in gender_counts.items()
            },
            "customer_type_mix": {
                key: round(value / n, 4)
                for key, value in type_counts.items()
            },
        },
        "caveat": (
            "This validates internal structural relationships in the synthetic "
            "generator. It does not prove that the population matches real-world "
            "customer data. Real-world calibration requires a reference dataset."
        ),
    }
