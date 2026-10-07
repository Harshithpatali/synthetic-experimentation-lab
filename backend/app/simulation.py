import math
import uuid
from dataclasses import dataclass

import numpy as np


# Major Indian cities provide a geographically realistic synthetic customer
# distribution. Locations are approximate city-centered coordinates with
# customer-level jitter applied during generation.
CITIES = [
    ("Delhi", "Delhi", 28.6139, 77.2090, 9.0),
    ("Mumbai", "Maharashtra", 19.0760, 72.8777, 9.0),
    ("Bengaluru", "Karnataka", 12.9716, 77.5946, 8.5),
    ("Hyderabad", "Telangana", 17.3850, 78.4867, 6.5),
    ("Chennai", "Tamil Nadu", 13.0827, 80.2707, 6.0),
    ("Kolkata", "West Bengal", 22.5726, 88.3639, 5.5),
    ("Pune", "Maharashtra", 18.5204, 73.8567, 5.5),
    ("Ahmedabad", "Gujarat", 23.0225, 72.5714, 5.0),
    ("Jaipur", "Rajasthan", 26.9124, 75.7873, 4.0),
    ("Surat", "Gujarat", 21.1702, 72.8311, 4.0),
    ("Lucknow", "Uttar Pradesh", 26.8467, 80.9462, 3.5),
    ("Kanpur", "Uttar Pradesh", 26.4499, 80.3319, 3.0),
    ("Nagpur", "Maharashtra", 21.1458, 79.0882, 3.0),
    ("Indore", "Madhya Pradesh", 22.7196, 75.8577, 3.0),
    ("Bhopal", "Madhya Pradesh", 23.2599, 77.4126, 2.5),
    ("Patna", "Bihar", 25.5941, 85.1376, 3.0),
    ("Vadodara", "Gujarat", 22.3072, 73.1812, 2.5),
    ("Coimbatore", "Tamil Nadu", 11.0168, 76.9558, 2.5),
    ("Kochi", "Kerala", 9.9312, 76.2673, 2.5),
    ("Thiruvananthapuram", "Kerala", 8.5241, 76.9366, 1.8),
    ("Visakhapatnam", "Andhra Pradesh", 17.6868, 83.2185, 2.3),
    ("Vijayawada", "Andhra Pradesh", 16.5062, 80.6480, 1.8),
    ("Bhubaneswar", "Odisha", 20.2961, 85.8245, 2.0),
    ("Guwahati", "Assam", 26.1445, 91.7362, 1.8),
    ("Chandigarh", "Chandigarh", 30.7333, 76.7794, 1.8),
    ("Dehradun", "Uttarakhand", 30.3165, 78.0322, 1.4),
    ("Srinagar", "Jammu and Kashmir", 34.0837, 74.7973, 1.2),
    ("Jammu", "Jammu and Kashmir", 32.7266, 74.8570, 1.0),
    ("Ranchi", "Jharkhand", 23.3441, 85.3096, 1.8),
    ("Raipur", "Chhattisgarh", 21.2514, 81.6296, 1.6),
    ("Nashik", "Maharashtra", 19.9975, 73.7898, 1.8),
    ("Mysuru", "Karnataka", 12.2958, 76.6394, 1.5),
    ("Mangaluru", "Karnataka", 12.9141, 74.8560, 1.3),
    ("Madurai", "Tamil Nadu", 9.9252, 78.1198, 1.5),
    ("Salem", "Tamil Nadu", 11.6643, 78.1460, 1.2),
    ("Tiruchirappalli", "Tamil Nadu", 10.7905, 78.7047, 1.2),
    ("Kota", "Rajasthan", 25.2138, 75.8648, 1.2),
    ("Jodhpur", "Rajasthan", 26.2389, 73.0243, 1.1),
    ("Amritsar", "Punjab", 31.6340, 74.8723, 1.3),
    ("Ludhiana", "Punjab", 30.9010, 75.8573, 1.2),
    ("Agra", "Uttar Pradesh", 27.1767, 78.0081, 1.5),
    ("Varanasi", "Uttar Pradesh", 25.3176, 82.9739, 1.5),
    ("Meerut", "Uttar Pradesh", 28.9845, 77.7064, 1.2),
    ("Rajkot", "Gujarat", 22.3039, 70.8022, 1.5),
    ("Aurangabad", "Maharashtra", 19.8762, 75.3433, 1.2),
]

PROFESSIONS = [
    "Engineer",
    "Teacher",
    "Finance",
    "Healthcare",
    "Business",
    "Student",
    "Government",
    "Other",
]


@dataclass
class Population:
    customers: list[dict]
    truth: list[dict]


def sigmoid(x):
    return float(1 / (1 + np.exp(-np.clip(x, -30, 30))))


def generate_population(size, seed):
    r = np.random.default_rng(seed)

    city_weights = np.array([city[4] for city in CITIES], dtype=float)
    city_weights = city_weights / city_weights.sum()
    city_idx = r.choice(len(CITIES), size=size, p=city_weights)

    age = np.clip(r.normal(34, 10, size), 18, 70).round().astype(int)
    gender = r.choice(["Female", "Male"], size=size, p=[0.48, 0.52])
    orders = r.poisson(np.clip(5.5 - (age - 35) * 0.02, 1, 8), size)
    aov = np.round(np.exp(r.normal(np.log(1100), 0.45, size)), 2)
    recency = np.clip(r.gamma(2.2, 18, size), 1, 180).round().astype(int)
    sessions = np.maximum(1, r.poisson(7, size))
    abandon = np.minimum(sessions, r.binomial(sessions, 0.28))

    device = r.choice(
        ["Mobile", "Desktop", "Tablet"],
        size=size,
        p=[0.68, 0.25, 0.07],
    )
    customer_type = np.where(
        orders >= 10,
        "Loyal",
        np.where(orders >= 3, "Repeat", "New"),
    )

    income = np.clip(
        r.lognormal(np.log(65000), 0.55, size),
        18000,
        500000,
    )
    profession = r.choice(
        PROFESSIONS,
        size=size,
        p=[0.20, 0.12, 0.12, 0.12, 0.15, 0.12, 0.09, 0.08],
    )

    price = r.beta(2.2, 2.0, size)
    novelty = r.beta(2, 2, size)
    risk = r.beta(2.5, 2.5, size)

    beauty = np.clip(
        0.45
        + 0.15 * (gender == "Female")
        + 0.20 * novelty
        - 0.10 * price
        + r.normal(0, 0.12, size),
        0,
        1,
    )
    electronics = np.clip(
        0.40
        + 0.15 * (gender == "Male")
        + 0.15 * (age < 35)
        + 0.15 * r.beta(2, 2, size),
        0,
        1,
    )
    grocery = np.clip(
        0.55
        + 0.10 * (age > 40)
        + 0.10 * (income < 70000)
        + r.normal(0, 0.08, size),
        0,
        1,
    )

    customers = []
    truth = []

    for i in range(size):
        city = CITIES[city_idx[i]]
        customer_id = str(uuid.uuid4())

        customers.append(
            {
                "id": customer_id,
                "age": int(age[i]),
                "gender": str(gender[i]),
                "city": city[0],
                "state": city[1],
                "lat": float(city[2] + r.normal(0, 0.035)),
                "lon": float(city[3] + r.normal(0, 0.035)),
                "device": str(device[i]),
                "customer_type": str(customer_type[i]),
                "orders": int(orders[i]),
                "aov": float(aov[i]),
                "recency_days": int(recency[i]),
                "sessions_30d": int(sessions[i]),
                "cart_abandonments": int(abandon[i]),
            }
        )

        truth.append(
            {
                "id": str(uuid.uuid4()),
                "customer_id": customer_id,
                "profession": str(profession[i]),
                "income": float(income[i]),
                "price_sensitivity": float(price[i]),
                "novelty_preference": float(novelty[i]),
                "risk_preference": float(risk[i]),
                "beauty_affinity": float(beauty[i]),
                "electronics_affinity": float(electronics[i]),
                "grocery_affinity": float(grocery[i]),
            }
        )

    return Population(customers, truth)


def build_similarity_edges(
    customers,
    truth,
    view,
    max_edges_per_node=4,
):
    """
    Build a global, feature-level observable similarity network.

    Customers are compared across the full population rather than being
    restricted to the same city. Each observable feature gets its own
    similarity edge type so the frontend can render a different colour for
    gender, device, customer type, age, orders, AOV, recency, sessions, and
    cart-abandonment similarity.

    A customer can therefore connect to another city when the relationship is
    supported by observable evidence. Geographic proximity is intentionally
    NOT used as a prerequisite for an edge.
    """
    feature_specs = {
        "gender": {
            "label": "Same gender",
            "kind": "categorical",
            "threshold": 1.0,
        },
        "device": {
            "label": "Same device",
            "kind": "categorical",
            "threshold": 1.0,
        },
        "customer_type": {
            "label": "Same customer type",
            "kind": "categorical",
            "threshold": 1.0,
        },
        "age": {
            "label": "Similar age",
            "kind": "numeric",
            "threshold": 0.70,
        },
        "orders": {
            "label": "Similar order frequency",
            "kind": "numeric",
            "threshold": 0.65,
        },
        "aov": {
            "label": "Similar AOV",
            "kind": "numeric",
            "threshold": 0.65,
        },
        "recency": {
            "label": "Similar recency",
            "kind": "numeric",
            "threshold": 0.65,
        },
        "sessions": {
            "label": "Similar sessions",
            "kind": "numeric",
            "threshold": 0.65,
        },
        "cart_abandonments": {
            "label": "Similar cart abandonment",
            "kind": "numeric",
            "threshold": 0.65,
        },
    }

    truth_by_customer = (
        {item["customer_id"]: item for item in truth}
        if view == "truth"
        else {}
    )

    n = len(customers)
    if n < 2:
        return []

    rng = np.random.default_rng(11)

    # Sample globally. This is deliberately NOT grouped by city so strong
    # observable similarity can create Delhi↔Mumbai, Bengaluru↔Kolkata, etc.
    candidate_pool_size = min(60, n - 1)

    # Keep the network visually useful and database-friendly:
    # max_edges_per_node is interpreted as a per-feature cap. With the
    # default of 1 there can be at most one strongest neighbour per feature.
    per_feature = max(1, int(max_edges_per_node))

    edges = []
    seen = set()

    # Vector-friendly arrays for the observable features.
    ages = np.asarray([c["age"] for c in customers], dtype=float)
    orders = np.asarray([c["orders"] for c in customers], dtype=float)
    aovs = np.asarray([c["aov"] for c in customers], dtype=float)
    recencies = np.asarray(
        [c["recency_days"] for c in customers],
        dtype=float,
    )
    sessions = np.asarray(
        [c["sessions_30d"] for c in customers],
        dtype=float,
    )
    abandons = np.asarray(
        [c["cart_abandonments"] for c in customers],
        dtype=float,
    )

    for i, customer in enumerate(customers):
        candidates = rng.choice(
            n,
            size=candidate_pool_size,
            replace=False,
        )

        feature_scores: dict[str, list[tuple[float, int]]] = {
            feature: [] for feature in feature_specs
        }

        for raw_j in candidates:
            j = int(raw_j)
            if i == j:
                continue

            other = customers[j]

            feature_scores["gender"].append(
                (float(customer["gender"] == other["gender"]), j)
            )
            feature_scores["device"].append(
                (float(customer["device"] == other["device"]), j)
            )
            feature_scores["customer_type"].append(
                (float(customer["customer_type"] == other["customer_type"]), j)
            )

            feature_scores["age"].append(
                (
                    math.exp(-abs(ages[i] - ages[j]) / 10.0),
                    j,
                )
            )
            feature_scores["orders"].append(
                (
                    math.exp(-abs(orders[i] - orders[j]) / 3.0),
                    j,
                )
            )

            # Compare AOV on the log scale so large spenders do not dominate
            # purely because their raw currency difference is larger.
            log_aov_i = math.log1p(aovs[i])
            log_aov_j = math.log1p(aovs[j])
            feature_scores["aov"].append(
                (
                    math.exp(-abs(log_aov_i - log_aov_j) / 0.35),
                    j,
                )
            )

            feature_scores["recency"].append(
                (
                    math.exp(-abs(recencies[i] - recencies[j]) / 35.0),
                    j,
                )
            )
            feature_scores["sessions"].append(
                (
                    math.exp(-abs(sessions[i] - sessions[j]) / 6.0),
                    j,
                )
            )
            feature_scores["cart_abandonments"].append(
                (
                    math.exp(-abs(abandons[i] - abandons[j]) / 2.5),
                    j,
                )
            )

        for feature, scored in feature_scores.items():
            threshold = feature_specs[feature]["threshold"]
            selected = [
                item
                for item in sorted(scored, reverse=True)[:per_feature]
                if item[0] >= threshold
            ]

            for score, j in selected:
                key = (min(i, j), max(i, j), feature)
                if key in seen:
                    continue

                seen.add(key)

                reasons = {
                    "feature": feature,
                    "label": feature_specs[feature]["label"],
                    "evidence": [feature_specs[feature]["label"]],
                }

                if customer["city"] != customers[j]["city"]:
                    reasons["evidence"].append(
                        f"Cross-city: {customer['city']} ↔ {customers[j]['city']}"
                    )

                if view == "truth":
                    left = truth_by_customer.get(customer["id"], {})
                    right = truth_by_customer.get(customers[j]["id"], {})
                    hidden_similarity = 0.0

                    if left and right:
                        hidden_similarity = (
                            0.30
                            * math.exp(
                                -abs(
                                    left["price_sensitivity"]
                                    - right["price_sensitivity"]
                                )
                            )
                            + 0.20
                            * math.exp(
                                -abs(
                                    left["novelty_preference"]
                                    - right["novelty_preference"]
                                )
                            )
                        )

                    reasons["hidden_similarity"] = round(
                        float(hidden_similarity),
                        4,
                    )

                edges.append(
                    {
                        "id": str(uuid.uuid4()),
                        "source_id": customers[i]["id"],
                        "target_id": customers[j]["id"],
                        "weight": float(min(score, 1.0)),
                        "view": view,
                        "reasons": reasons,
                    }
                )

    return edges

def simulate_outcomes(
    customers,
    truth_by_customer,
    category,
    treatment_share,
    seed,
):
    rng = np.random.default_rng(seed)
    n = len(customers)

    treated = set(
        rng.permutation(n)[: int(n * treatment_share)]
    )

    fields = {
        "Beauty": ("beauty_affinity", 0.10),
        "Electronics": ("electronics_affinity", 0.08),
        "Grocery": ("grocery_affinity", 0.06),
    }

    field, base = fields.get(category, fields["Beauty"])
    outcomes = []
    segments = {}

    for i, customer in enumerate(customers):
        hidden = truth_by_customer[customer["id"]]
        affinity = hidden[field]

        baseline = (
            -2.05
            + 0.18 * np.log1p(customer["orders"])
            + 0.08 * customer["sessions_30d"]
            - 0.012 * customer["recency_days"]
            - 0.55 * hidden["price_sensitivity"]
            + 0.30 * affinity
        )

        effect = (
            base
            * (0.65 + 0.9 * affinity)
            * (1 - 0.45 * hidden["price_sensitivity"])
            + 0.035 * hidden["novelty_preference"]
        )

        if category == "Beauty" and customer["gender"] == "Female":
            effect *= 1.22

        converted = bool(
            rng.random()
            < sigmoid(
                baseline
                + (effect if i in treated else 0)
            )
        )

        arm = "treatment" if i in treated else "control"

        outcomes.append(
            {
                "customer_id": customer["id"],
                "arm": arm,
                "converted": converted,
                "revenue": float(
                    customer["aov"] if converted else 0
                ),
            }
        )

        for segment in (
            customer["gender"],
            customer["customer_type"],
        ):
            segments.setdefault(segment, []).append(
                (arm, converted)
            )

    return outcomes, segments
