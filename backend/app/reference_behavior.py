"""
Real-data behavioral benchmark for the synthetic population.

The bundled CSV is a small, openly licensed sample of the real UCI Online
Retail II transaction dataset. It contains real transaction rows, not
synthetic observations.

The reference retailer is UK-based, so this benchmark measures transferable
transaction behavior only. It does not validate India-specific demographics,
geography, device mix, or currency levels.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime
from functools import lru_cache
from pathlib import Path

import numpy as np


REFERENCE_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "reference"
    / "online_retail_real_sample.csv"
)

REFERENCE_SOURCE = {
    "name": "UCI Online Retail II",
    "creator": "Daqing Chen",
    "citation": (
        "Chen, D. (2012). Online Retail II [Dataset]. "
        "UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D"
    ),
    "license": "CC BY 4.0",
    "scope": "UK-based non-store online retailer",
    "sample_rows": 1950,
    "sample_selection": "Small real-data benchmark sample; no synthetic rows added.",
}


def _is_valid_transaction(row: dict) -> bool:
    """Keep identifiable, positive product transactions from the real sample."""
    invoice = str(row.get("Invoice", "")).strip()
    stock_code = str(row.get("StockCode", "")).strip().upper()
    customer_id = str(row.get("CustomerID", "")).strip()

    if not customer_id or customer_id.lower() in {"nan", "none"}:
        return False

    # The source fixture uses the Online Retail II column name Invoice.
    # C-prefixed invoices are cancellations.
    if not invoice or invoice.upper().startswith("C"):
        return False

    if stock_code in {
        "POST",
        "D",
        "M",
        "DOT",
        "C2",
        "BANK CHARGES",
        "AMAZONFEE",
        "CRUK",
        "TEST001",
    }:
        return False

    try:
        quantity = float(row["Quantity"])
        unit_price = float(row["Price"])
        datetime.strptime(str(row["InvoiceDate"]), "%Y-%m-%d %H:%M:%S")
    except (KeyError, TypeError, ValueError):
        return False

    return quantity > 0 and unit_price > 0


@lru_cache(maxsize=1)
def load_reference_profiles() -> tuple[dict, ...]:
    if not REFERENCE_PATH.exists():
        raise FileNotFoundError(
            f"Reference dataset not found at {REFERENCE_PATH}. "
            "The repository must contain "
            "data/reference/online_retail_real_sample.csv."
        )

    invoices_by_customer: dict[str, set[str]] = defaultdict(set)
    revenue_by_customer: dict[str, float] = defaultdict(float)
    items_by_customer: dict[str, float] = defaultdict(float)
    last_date_by_customer: dict[str, datetime] = {}
    all_dates: list[datetime] = []
    countries_by_customer: dict[str, str] = {}

    with REFERENCE_PATH.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not _is_valid_transaction(row):
                continue

            customer_id = str(row["CustomerID"]).strip()
            invoice = str(row["Invoice"]).strip()
            quantity = float(row["Quantity"])
            unit_price = float(row["Price"])
            timestamp = datetime.strptime(
                str(row["InvoiceDate"]),
                "%Y-%m-%d %H:%M:%S",
            )

            invoices_by_customer[customer_id].add(invoice)
            revenue_by_customer[customer_id] += quantity * unit_price
            items_by_customer[customer_id] += quantity
            last_date_by_customer[customer_id] = max(
                last_date_by_customer.get(customer_id, timestamp),
                timestamp,
            )
            countries_by_customer.setdefault(
                customer_id,
                str(row.get("Country", "Unknown")),
            )
            all_dates.append(timestamp)

    if not all_dates or not invoices_by_customer:
        raise ValueError("Reference sample contains no usable customer transactions.")

    cutoff = max(all_dates)
    profiles = []

    for customer_id, invoices in invoices_by_customer.items():
        order_count = len(invoices)
        revenue = revenue_by_customer[customer_id]
        profiles.append(
            {
                "customer_id": customer_id,
                "orders": order_count,
                "aov": revenue / max(order_count, 1),
                "recency_days": max(
                    0,
                    (cutoff - last_date_by_customer[customer_id]).days,
                ),
                "items_per_order": items_by_customer[customer_id] / max(order_count, 1),
                "country": countries_by_customer.get(customer_id, "Unknown"),
            }
        )

    return tuple(profiles)


def _quantile(values: list[float] | np.ndarray, q: float) -> float:
    if not values:
        return 0.0
    return float(np.quantile(np.asarray(values, dtype=float), q))


def _ks_distance(
    left: list[float] | np.ndarray,
    right: list[float] | np.ndarray,
) -> float:
    """Empirical CDF distance (two-sample KS statistic)."""
    if len(left) == 0 or len(right) == 0:
        return 1.0

    a = np.sort(np.asarray(left, dtype=float))
    b = np.sort(np.asarray(right, dtype=float))
    points = np.sort(np.concatenate([a, b]))

    a_cdf = np.searchsorted(a, points, side="right") / len(a)
    b_cdf = np.searchsorted(b, points, side="right") / len(b)
    return float(np.max(np.abs(a_cdf - b_cdf)))


def _distribution_score(
    real: list[float],
    synthetic: list[float],
    *,
    metric: str,
) -> dict:
    """
    Compare a shared metric with the two-sample KS distance.

    AOV is compared by shape after each dataset is normalized by its own
    median in log space. This avoids falsely penalising the comparison because
    the real reference is priced in GBP while the synthetic app uses INR.
    Orders and recency retain their native units.
    """
    if metric == "aov":
        real_median = max(_quantile(real, 0.50), 1e-9)
        synthetic_median = max(_quantile(synthetic, 0.50), 1e-9)
        real_for_ks = np.log(np.asarray(real, dtype=float) / real_median)
        synthetic_for_ks = np.log(
            np.asarray(synthetic, dtype=float) / synthetic_median
        )
        distance = _ks_distance(real_for_ks, synthetic_for_ks)
        comparison = "relative AOV shape"
    else:
        distance = _ks_distance(real, synthetic)
        comparison = f"{metric} distribution"

    return {
        "score": round(max(0.0, 100.0 * (1.0 - distance)), 1),
        "ks_distance": round(distance, 4),
        "comparison": comparison,
        "real_median": round(_quantile(real, 0.50), 2),
        "synthetic_median": round(_quantile(synthetic, 0.50), 2),
        "real_p25": round(_quantile(real, 0.25), 2),
        "synthetic_p25": round(_quantile(synthetic, 0.25), 2),
        "real_p75": round(_quantile(real, 0.75), 2),
        "synthetic_p75": round(_quantile(synthetic, 0.75), 2),
    }


def _customer_type(orders: float, recency_days: float) -> str:
    if orders >= 8 and recency_days <= 70:
        return "Loyal"
    if orders >= 2 and recency_days <= 120:
        return "Repeat"
    return "New"


def _category_shares(values: list[str]) -> dict[str, float]:
    if not values:
        return {}
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    n = len(values)
    return {key: round(count / n, 4) for key, count in counts.items()}


def compare_to_real_reference(customers: list[dict]) -> dict:
    """
    Compare synthetic customer behavior to real transaction-derived behavior.

    The comparison is deliberately limited to fields the reference data can
    support directly: order frequency, relative AOV distribution shape,
    recency, and lifecycle composition.
    """
    reference = list(load_reference_profiles())
    if not reference:
        raise ValueError("No reference customer profiles available.")

    synthetic_orders = [float(row["orders"]) for row in customers if "orders" in row]
    synthetic_aov = [float(row["aov"]) for row in customers if "aov" in row]
    synthetic_recency = [
        float(row["recency_days"])
        for row in customers
        if "recency_days" in row
    ]

    if not synthetic_orders or not synthetic_aov or not synthetic_recency:
        raise ValueError("Synthetic population is missing shared behavior fields.")

    real_orders = [float(row["orders"]) for row in reference]
    real_aov = [float(row["aov"]) for row in reference]
    real_recency = [float(row["recency_days"]) for row in reference]

    distributions = {
        "orders": _distribution_score(
            real_orders, synthetic_orders, metric="orders"
        ),
        "aov": _distribution_score(
            real_aov, synthetic_aov, metric="aov"
        ),
        "recency": _distribution_score(
            real_recency, synthetic_recency, metric="recency"
        ),
    }

    real_types = [
        _customer_type(row["orders"], row["recency_days"]) for row in reference
    ]
    synthetic_types = [
        _customer_type(row["orders"], row["recency_days"]) for row in customers
    ]

    real_shares = _category_shares(real_types)
    synthetic_shares = _category_shares(synthetic_types)
    all_types = sorted(set(real_shares) | set(synthetic_shares))
    type_distance = 0.5 * sum(
        abs(real_shares.get(label, 0.0) - synthetic_shares.get(label, 0.0))
        for label in all_types
    )
    lifecycle_score = round(max(0.0, 100.0 * (1.0 - type_distance)), 1)

    overall = round(
        0.30 * distributions["orders"]["score"]
        + 0.40 * distributions["aov"]["score"]
        + 0.20 * distributions["recency"]["score"]
        + 0.10 * lifecycle_score,
        1,
    )

    return {
        "label": "Real-data behavioral alignment",
        "score": overall,
        "classification": (
            "Strong alignment"
            if overall >= 80
            else "Moderate alignment"
            if overall >= 60
            else "Low alignment"
        ),
        "population_size": len(customers),
        "reference_customers": len(reference),
        "reference_source": REFERENCE_SOURCE,
        "metrics": distributions,
        "lifecycle": {
            "score": lifecycle_score,
            "real_shares": real_shares,
            "synthetic_shares": synthetic_shares,
        },
        "caveat": (
            "This benchmark uses real UK online-retail transactions as a "
            "transaction-behavior reference. It does not establish that the "
            "synthetic Indian population matches Indian demographics, geography, "
            "device usage, or currency levels."
        ),
    }


def reference_summary() -> dict:
    reference = list(load_reference_profiles())
    return {
        "source": REFERENCE_SOURCE,
        "customers": len(reference),
        "median_orders": round(
            _quantile([row["orders"] for row in reference], 0.50),
            2,
        ),
        "median_aov": round(
            _quantile([row["aov"] for row in reference], 0.50),
            2,
        ),
        "median_recency_days": round(
            _quantile([row["recency_days"] for row in reference], 0.50),
            2,
        ),
    }
