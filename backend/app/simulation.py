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


def _sigmoid_array(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))


def _sample_correlated_latents(rng, size):
    """
    Low-dimensional Gaussian factor model used to induce realistic
    dependencies between customer attributes.

    This is intentionally lightweight: no external statistical dependency is
    required, and the existing database schema remains unchanged.
    """
    correlation = np.array(
        [
            [1.00, 0.28, 0.15, -0.20, 0.15, 0.08],
            [0.28, 1.00, 0.22, -0.10, 0.28, 0.12],
            [0.15, 0.22, 1.00, -0.18, 0.42, 0.18],
            [-0.20, -0.10, -0.18, 1.00, -0.15, 0.04],
            [0.15, 0.28, 0.42, -0.15, 1.00, 0.22],
            [0.08, 0.12, 0.18, 0.04, 0.22, 1.00],
        ],
        dtype=float,
    )

    # Numerical safety in case tiny floating-point differences make the
    # intended positive-definite matrix marginally invalid.
    eigenvalues = np.linalg.eigvalsh(correlation)
    if eigenvalues.min() <= 1e-8:
        correlation += np.eye(correlation.shape[0]) * (
            1e-8 - eigenvalues.min()
        )

    chol = np.linalg.cholesky(correlation)
    normals = rng.normal(size=(size, 6)) @ chol.T
    return {
        "socioeconomic": normals[:, 0],
        "engagement": normals[:, 1],
        "digital": normals[:, 2],
        "price": normals[:, 3],
        "novelty": normals[:, 4],
        "risk": normals[:, 5],
    }


def generate_population(size, seed):
    r = np.random.default_rng(seed)

    city_weights = np.array([city[4] for city in CITIES], dtype=float)
    city_weights = city_weights / city_weights.sum()
    city_idx = r.choice(len(CITIES), size=size, p=city_weights)

    latents = _sample_correlated_latents(r, size)
    socioeconomic = latents["socioeconomic"]
    engagement = latents["engagement"]
    digital = latents["digital"]
    price_latent = latents["price"]
    novelty_latent = latents["novelty"]
    risk_latent = latents["risk"]

    age = np.clip(
        np.round(34 + 9.5 * socioeconomic + 7.0 * r.normal(size=size)),
        18,
        70,
    ).astype(int)

    gender = r.choice(
        ["Female", "Male"],
        size=size,
        p=[0.48, 0.52],
    )

    # Correlated economic behaviour: income depends on age and a latent
    # socioeconomic factor rather than being independent of the customer.
    income = np.clip(
        np.exp(
            np.log(65000)
            + 0.42 * socioeconomic
            + 0.18 * ((age - 34) / 10.0)
            + 0.28 * r.normal(size=size)
        ),
        18000,
        500000,
    )

    # Digital engagement influences sessions and purchase frequency.
    order_lambda = np.exp(
        np.clip(
            np.log(5.0)
            + 0.20 * socioeconomic
            + 0.48 * engagement
            - 0.014 * (age - 35),
            np.log(0.8),
            np.log(18.0),
        )
    )
    orders = r.poisson(order_lambda)

    # AOV is linked to income and purchasing activity.
    aov = np.exp(
        np.log(850.0)
        + 0.30 * socioeconomic
        + 0.065 * np.log1p(orders)
        + 0.10 * ((age - 34) / 10.0)
        + 0.20 * r.normal(size=size)
    )
    aov = np.clip(aov, 250, 50000).round(2)

    session_lambda = np.exp(
        np.clip(
            np.log(5.0)
            + 0.42 * engagement
            + 0.20 * np.log1p(orders)
            + 0.20 * digital,
            np.log(1.0),
            np.log(40.0),
        )
    )
    sessions = np.maximum(1, r.poisson(session_lambda))

    # Latent price sensitivity is bounded and correlated with income and
    # engagement rather than being a completely independent random variable.
    price_sensitivity = np.clip(
        0.62 * r.beta(2.2, 2.0, size)
        + 0.38 * _sigmoid_array(-0.80 * price_latent + 0.20 * (age < 30)),
        0,
        1,
    )

    novelty_preference = np.clip(
        0.60 * r.beta(2.0, 2.0, size)
        + 0.40 * _sigmoid_array(0.90 * novelty_latent + 0.22 * digital),
        0,
        1,
    )

    risk_preference = np.clip(
        0.60 * r.beta(2.5, 2.5, size)
        + 0.40 * _sigmoid_array(0.75 * risk_latent + 0.18 * novelty_latent),
        0,
        1,
    )

    # Recency is a behavioural outcome: engaged customers tend to have more
    # recent activity, while price-sensitive customers tend to return less often.
    recency_scale = np.exp(
        np.clip(
            np.log(19.0)
            - 0.36 * engagement
            + 0.18 * price_sensitivity,
            np.log(5.0),
            np.log(55.0),
        )
    )
    recency = np.clip(
        r.gamma(2.2, recency_scale),
        1,
        180,
    ).round().astype(int)

    # Device mix depends on age and digital behaviour.
    p_mobile = np.clip(
        0.68
        - 0.010 * ((age - 34) / 10.0)
        + 0.07 * _sigmoid_array(digital),
        0.50,
        0.86,
    )
    p_desktop = np.clip(
        0.24
        + 0.025 * ((age - 34) / 10.0)
        - 0.04 * _sigmoid_array(digital),
        0.10,
        0.36,
    )
    p_tablet = np.clip(1.0 - p_mobile - p_desktop, 0.03, 0.20)

    # Renormalise the three probabilities row-by-row.
    total = p_mobile + p_desktop + p_tablet
    p_mobile /= total
    p_desktop /= total
    p_tablet /= total

    u_device = r.random(size)
    device = np.where(
        u_device < p_mobile,
        "Mobile",
        np.where(
            u_device < p_mobile + p_desktop,
            "Desktop",
            "Tablet",
        ),
    )

    # Cart abandonment is explicitly linked to friction, price sensitivity and
    # engagement. This gives checkout experiments a meaningful behavioural base.
    abandon_probability = np.clip(
        _sigmoid_array(
            -1.30
            + 0.85 * price_sensitivity
            + 0.28 * ((device == "Mobile") == False)
            - 0.38 * engagement
        ),
        0.08,
        0.70,
    )
    abandon = np.minimum(
        sessions,
        r.binomial(sessions, abandon_probability),
    )

    # Customer lifecycle is a function of accumulated orders and recent activity.
    customer_type = np.where(
        (orders >= 8) & (recency <= 70),
        "Loyal",
        np.where(
            (orders >= 2) & (recency <= 120),
            "Repeat",
            "New",
        ),
    )

    # Profession is hidden, but its distribution is conditioned on age and
    # socioeconomic context to avoid an independent one-hot draw.
    profession_scores = np.array(
        [
            0.18 * np.ones(size),  # Engineer
            0.10 * np.ones(size),  # Teacher
            0.11 * np.ones(size),  # Finance
            0.10 * np.ones(size),  # Healthcare
            0.14 * np.ones(size),  # Business
            0.11 * np.ones(size),  # Student
            0.09 * np.ones(size),  # Government
            0.07 * np.ones(size),  # Other
        ]
    )

    profession_scores[5] += 0.36 * (age < 24)
    profession_scores[6] += 0.10 * (age > 38)
    profession_scores[1] += 0.06 * (age > 30)
    profession_scores[4] += 0.07 * _sigmoid_array(socioeconomic)
    profession_scores[0] += 0.05 * _sigmoid_array(digital)

    profession_scores = np.maximum(profession_scores, 0.01)
    profession_scores /= profession_scores.sum(axis=0, keepdims=True)

    u_profession = r.random(size)
    cumulative_profession = np.cumsum(profession_scores, axis=0)
    profession_idx = (u_profession[None, :] > cumulative_profession).sum(axis=0)
    profession = np.asarray(PROFESSIONS)[profession_idx]

    # Category affinity uses the latent behavioural factors, creating
    # interpretable heterogeneity across products.
    beauty = np.clip(
        _sigmoid_array(
            -0.15
            + 0.55 * novelty_preference
            - 0.40 * price_sensitivity
            + 0.25 * (gender == "Female")
            + 0.10 * socioeconomic
            + 0.18 * r.normal(size=size)
        ),
        0,
        1,
    )
    electronics = np.clip(
        _sigmoid_array(
            -0.10
            + 0.42 * novelty_preference
            + 0.30 * _sigmoid_array(digital)
            + 0.18 * (age < 35)
            + 0.10 * risk_preference
            + 0.18 * r.normal(size=size)
        ),
        0,
        1,
    )
    grocery = np.clip(
        _sigmoid_array(
            0.20
            + 0.22 * (age > 40)
            + 0.18 * (income < 70000)
            + 0.12 * (customer_type == "Loyal")
            + 0.15 * r.normal(size=size)
        ),
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
                "price_sensitivity": float(price_sensitivity[i]),
                "novelty_preference": float(novelty_preference[i]),
                "risk_preference": float(risk_preference[i]),
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
    max_edges_per_node=1,
):
    """
    Build a global, feature-level observable similarity network.

    No city is used as a hard partition. For every observable feature we find
    the strongest globally similar neighbours, so a Bengaluru customer can
    connect to a Mumbai, Delhi, Kolkata, or any other city when the feature
    provides measurable similarity.

    Numeric features use exact nearest-neighbour relationships in sorted
    feature space. Categorical features connect customers within the same
    category. The resulting graph remains compact because the number of
    neighbours is capped per feature.
    """
    feature_specs = {
        "gender": {
            "label": "Same gender",
            "kind": "categorical",
            "values": lambda c: c["gender"],
            "threshold": 1.0,
            "scale": None,
        },
        "device": {
            "label": "Same device",
            "kind": "categorical",
            "values": lambda c: c["device"],
            "threshold": 1.0,
            "scale": None,
        },
        "customer_type": {
            "label": "Same customer type",
            "kind": "categorical",
            "values": lambda c: c["customer_type"],
            "threshold": 1.0,
            "scale": None,
        },
        "age": {
            "label": "Similar age",
            "kind": "numeric",
            "values": lambda c: float(c["age"]),
            "threshold": 0.70,
            "scale": 10.0,
        },
        "orders": {
            "label": "Similar order frequency",
            "kind": "numeric",
            "values": lambda c: float(c["orders"]),
            "threshold": 0.65,
            "scale": 3.0,
        },
        "aov": {
            "label": "Similar AOV",
            "kind": "numeric",
            "values": lambda c: math.log1p(float(c["aov"])),
            "threshold": 0.65,
            "scale": 0.35,
        },
        "recency": {
            "label": "Similar recency",
            "kind": "numeric",
            "values": lambda c: float(c["recency_days"]),
            "threshold": 0.65,
            "scale": 35.0,
        },
        "sessions": {
            "label": "Similar sessions",
            "kind": "numeric",
            "values": lambda c: float(c["sessions_30d"]),
            "threshold": 0.65,
            "scale": 6.0,
        },
        "cart_abandonments": {
            "label": "Similar cart abandonment",
            "kind": "numeric",
            "values": lambda c: float(c["cart_abandonments"]),
            "threshold": 0.65,
            "scale": 2.5,
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

    per_feature = max(1, int(max_edges_per_node))
    edges = []
    seen = set()

    def add_edge(i: int, j: int, feature: str, base_score: float) -> None:
        if i == j:
            return

        key = (min(i, j), max(i, j), feature)
        if key in seen:
            return

        score = float(min(max(base_score, 0.0), 1.0))
        reasons = {
            "feature": feature,
            "label": feature_specs[feature]["label"],
            "evidence": [feature_specs[feature]["label"]],
        }

        if customers[i]["city"] != customers[j]["city"]:
            reasons["evidence"].append(
                f"Cross-city: {customers[i]['city']} ↔ {customers[j]['city']}"
            )

        if view == "truth":
            left = truth_by_customer.get(customers[i]["id"], {})
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

            score = float(min(1.0, score + hidden_similarity))
            reasons["hidden_similarity"] = round(
                float(hidden_similarity),
                4,
            )

        seen.add(key)
        edges.append(
            {
                "id": str(uuid.uuid4()),
                "source_id": customers[i]["id"],
                "target_id": customers[j]["id"],
                "weight": score,
                "view": view,
                "reasons": reasons,
            }
        )

    for feature, spec in feature_specs.items():
        values = np.asarray(
            [spec["values"](customer) for customer in customers],
        )

        if spec["kind"] == "categorical":
            groups = {}
            for index, value in enumerate(values.tolist()):
                groups.setdefault(value, []).append(index)

            for indices in groups.values():
                if len(indices) < 2:
                    continue

                # Circular neighbour assignment gives every customer in the
                # category a feature edge without creating a giant clique.
                for pos, i in enumerate(indices):
                    for offset in range(1, min(per_feature, len(indices) - 1) + 1):
                        j = indices[(pos + offset) % len(indices)]
                        add_edge(i, j, feature, 1.0)

        else:
            order = np.argsort(values, kind="mergesort")

            for position, i_raw in enumerate(order):
                i = int(i_raw)
                candidate_positions = set()

                for offset in range(1, per_feature + 1):
                    left = position - offset
                    right = position + offset

                    if left >= 0:
                        candidate_positions.add(left)
                    if right < n:
                        candidate_positions.add(right)

                ranked = []
                for candidate_position in candidate_positions:
                    j = int(order[candidate_position])
                    if j == i:
                        continue

                    distance = abs(float(values[i]) - float(values[j]))
                    score = math.exp(-distance / spec["scale"])
                    ranked.append((score, j))

                ranked.sort(reverse=True)

                for score, j in ranked[:per_feature]:
                    if score >= spec["threshold"]:
                        add_edge(i, j, feature, score)

    return edges

def simulate_outcomes(
    customers,
    truth_by_customer,
    category,
    experiment_type,
    treatment_share,
    seed,
):
    rng = np.random.default_rng(seed)
    n = len(customers)

    treated = set(
        rng.permutation(n)[: int(n * treatment_share)]
    )

    affinity_fields = {
        "Beauty": "beauty_affinity",
        "Electronics": "electronics_affinity",
        "Grocery": "grocery_affinity",
    }

    affinity = {}
    for customer in customers:
        hidden = truth_by_customer[customer["id"]]
        field = affinity_fields.get(category)
        if field:
            value = hidden[field]
        else:
            value = (
                hidden["beauty_affinity"]
                + hidden["electronics_affinity"]
                + hidden["grocery_affinity"]
            ) / 3.0
        affinity[customer["id"]] = float(value)

    # Different business experiments should not all behave like a beauty offer.
    # These are simulator priors, not claims about real-world effect sizes.
    effect_base = {
        "Marketing campaign": 0.075,
        "Product promotion": 0.085,
        "New UI / feature": 0.055,
        "Checkout redesign": 0.080,
        "Pricing / discount": 0.095,
        "Recommendation / personalization": 0.070,
        "Messaging / copy": 0.045,
        "Retention / loyalty": 0.060,
        "Search / discovery": 0.050,
        "Other": 0.050,
    }.get(experiment_type, 0.060)

    outcomes = []
    segments = {}

    for i, customer in enumerate(customers):
        hidden = truth_by_customer[customer["id"]]
        customer_affinity = affinity[customer["id"]]

        baseline = (
            -2.05
            + 0.18 * np.log1p(customer["orders"])
            + 0.08 * customer["sessions_30d"]
            - 0.012 * customer["recency_days"]
            - 0.55 * hidden["price_sensitivity"]
            + 0.30 * customer_affinity
        )

        effect = (
            effect_base
            * (0.70 + 0.85 * customer_affinity)
            * (1 - 0.35 * hidden["price_sensitivity"])
        )

        # Scenario-specific response mechanisms make the simulator useful for
        # different business questions instead of treating every change as an
        # offer campaign.
        if experiment_type == "New UI / feature":
            mobile_lift = 1.0 + 0.18 * (customer["device"] == "Mobile")
            effect *= mobile_lift + 0.12 * hidden["novelty_preference"]

        elif experiment_type == "Checkout redesign":
            abandonment_factor = 1.0 + 0.20 * (
                customer["cart_abandonments"] / max(customer["sessions_30d"], 1)
            )
            effect *= abandonment_factor

        elif experiment_type == "Pricing / discount":
            effect *= 1.0 + 0.45 * hidden["price_sensitivity"]

        elif experiment_type == "Recommendation / personalization":
            effect *= 1.0 + 0.30 * customer_affinity + 0.15 * hidden["novelty_preference"]

        elif experiment_type == "Messaging / copy":
            effect *= 0.85 + 0.35 * hidden["novelty_preference"]

        elif experiment_type == "Retention / loyalty":
            effect *= (
                0.85
                + 0.20 * (customer["customer_type"] == "Repeat")
                + 0.30 * (customer["customer_type"] == "Loyal")
            )

        elif experiment_type == "Search / discovery":
            effect *= 0.90 + 0.25 * hidden["novelty_preference"]

        else:
            effect *= 0.95 + 0.10 * hidden["novelty_preference"]

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
