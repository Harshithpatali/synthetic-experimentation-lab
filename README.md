<div align="center">

# 🧪 Synthetic Experimentation Lab

### *Test the experiment before testing it on real customers.*

A full-stack data-science platform that builds a synthetic Indian customer population, stores it in Neon PostgreSQL, visualizes it as a cyber-intelligence customer network, simulates randomized control/treatment experiments, and produces statistically rigorous experiment reports.

<br/>

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/Neon-PostgreSQL-00E599?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)

![Render](https://img.shields.io/badge/Deploy-Render-46E3B7?style=for-the-badge&logo=render&logoColor=black)
![Streamlit Cloud](https://img.shields.io/badge/Deploy-Streamlit%20Cloud-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![CI](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![LLM](https://img.shields.io/badge/LLM-None%20Required-8A2BE2?style=for-the-badge)

<br/>

[Core Idea](#-the-core-idea) ·
[Architecture](#-architecture) ·
[Workflow](#-product-workflow) ·
[Statistics](#-statistical-engine) ·
[Data Model](#-data-model) ·
[API](#-api-reference) ·
[Deploy](#-deployment) ·
[Limitations](#-statistical-interpretation--limitations)

</div>

---

## 📑 Table of Contents

- [The Core Idea](#-the-core-idea)
- [What the Project Does](#-what-the-project-does)
- [Architecture](#-architecture)
- [Product Workflow](#-product-workflow)
- [Synthetic Population Model](#-synthetic-population-model)
- [Observable vs Hidden Variables](#-observable-vs-hidden-variables)
- [Diagnostics & Real-Data Benchmark](#-diagnostics--real-data-benchmark)
- [India Population Map & Similarity Network](#-india-population-map--similarity-network)
- [Experiment Simulation Engine](#-experiment-simulation-engine)
- [Statistical Engine](#-statistical-engine)
- [Experiment Report](#-experiment-report)
- [Data Model](#-data-model)
- [API Reference](#-api-reference)
- [Repository Structure](#-repository-structure)
- [Local Development](#-local-development)
- [Deployment](#-deployment)
- [CI & Testing](#-ci--testing)
- [Statistical Interpretation & Limitations](#-statistical-interpretation--limitations)
- [Security](#-security--data-boundaries)
- [Project Status](#-project-status)
- [Attribution](#-data-attribution)

---

## 🎯 The Core Idea

> **Business idea → Synthetic population → Randomized experiment → Statistical inference → Decision about a real pilot.**

```mermaid
flowchart TD
    A["💡 Business Idea"] --> B["👥 Synthetic Customer Population"]
    B --> C["👁️ Observable Behavior"]
    B --> D["🔒 Hidden Simulator Behavior"]
    C --> E["🎲 Randomized Treatment / Control"]
    D --> E
    E --> F["📊 Simulated Outcomes"]
    F --> G["📈 Uplift + Uncertainty + Statistical Test"]
    G --> H["✅ Decision About a Real-World Pilot"]
    H -.->|"validate"| I["🧪 Real Controlled A/B Test"]

    style A fill:#1f2937,stroke:#60a5fa,stroke-width:2px,color:#fff
    style B fill:#1f2937,stroke:#a78bfa,stroke-width:2px,color:#fff
    style C fill:#1f2937,stroke:#34d399,stroke-width:2px,color:#fff
    style D fill:#1f2937,stroke:#f87171,stroke-width:2px,color:#fff
    style E fill:#1f2937,stroke:#fbbf24,stroke-width:2px,color:#fff
    style F fill:#1f2937,stroke:#38bdf8,stroke-width:2px,color:#fff
    style G fill:#1f2937,stroke:#c084fc,stroke-width:2px,color:#fff
    style H fill:#1f2937,stroke:#4ade80,stroke-width:2px,color:#fff
    style I fill:#111827,stroke:#94a3b8,stroke-width:2px,stroke-dasharray: 5 5,color:#fff
```

> [!WARNING]
> This application is a **decision-support sandbox**, not a replacement for a real A/B test.

---

## 🚀 What the Project Does

A company can ask questions **before exposing real customers**:

| ❓ Question | 🎯 Experiment Type |
|---|---|
| Should we run this marketing campaign? | Marketing campaign |
| Would a new product promotion improve conversion? | Product promotion |
| Could a checkout redesign reduce abandonment? | Checkout redesign |
| Would a pricing or discount change help? | Pricing / discount |
| Would personalization improve performance? | Recommendation / personalization |
| Should we test a new UI or feature? | New UI / feature |
| Which customer segments appear to respond best? | Segment analysis |
| How large must an effect be to be detectable? | Power / MDE analysis |

The synthetic population is **deliberately structured**, not a set of independent random columns. The generator creates relationships across demographics, economic behavior, engagement, purchasing, lifecycle, device usage, and product affinity.

```mermaid
flowchart LR
    subgraph OBS["👁️ What a Company Can Observe"]
        O1["Age · Gender · City"]
        O2["Device · Lifecycle"]
        O3["Orders · AOV · Recency"]
        O4["Sessions · Cart Abandonments"]
    end

    subgraph HID["🔒 What the Simulator Knows Internally"]
        H1["Income · Profession"]
        H2["Price Sensitivity"]
        H3["Novelty · Risk Preference"]
        H4["Beauty · Electronics · Grocery Affinity"]
    end

    HID ==>|"generates heterogeneous outcomes"| OBS

    style OBS fill:#0f172a,stroke:#34d399,stroke-width:2px,color:#fff
    style HID fill:#0f172a,stroke:#f87171,stroke-width:2px,color:#fff
```

---

## 🏗️ Architecture

```mermaid
flowchart LR
    U["👤 Company User"] --> S["🎨 Streamlit Community Cloud<br/>Frontend"]
    S -->|"HTTPS + JSON"| R["⚡ Render Web Service<br/>FastAPI · Python · Docker"]
    R -->|"PostgreSQL over TLS"| N[("🐘 Neon PostgreSQL<br/>Persistent Store")]

    style U fill:#1e293b,stroke:#60a5fa,stroke-width:2px,color:#fff
    style S fill:#1e293b,stroke:#FF4B4B,stroke-width:2px,color:#fff
    style R fill:#1e293b,stroke:#009688,stroke-width:2px,color:#fff
    style N fill:#1e293b,stroke:#00E599,stroke-width:2px,color:#fff
```

### 🧰 Technology Stack

| Layer | Technology |
|:---|:---|
| 🎨 UI | Streamlit |
| ⚡ API | FastAPI |
| 🐍 Language | Python 3.12 |
| 🔢 Numerical computing | NumPy |
| 🐼 Dataframes | Pandas |
| 📊 Visualization | Plotly |
| 🗃️ ORM | SQLAlchemy |
| 🔌 Database driver | psycopg |
| 🐘 Database | Neon PostgreSQL |
| 📦 Backend packaging | Docker |
| ☁️ Backend hosting | Render |
| 🎨 Frontend hosting | Streamlit Community Cloud |
| 🧪 Testing | Pytest |
| 🔁 CI | GitHub Actions |
| 📦 Optional container runtime | Cloudflare Containers |
| 🤖 LLM | **None** |

> [!NOTE]
> There is deliberately **no Groq dependency, no external LLM generation step, and no React dependency**. The simulator uses numerical and statistical generation rather than text generation.

---

## 🎯 Product Workflow

The application is organized into **five company-facing pages**.

```mermaid
flowchart LR
    P1["1️⃣<br/>👥 Generate<br/>Population"] --> P2["2️⃣<br/>🗺️ India<br/>Population Map"]
    P2 --> P3["3️⃣<br/>📊 Company<br/>Experiment"]
    P3 --> P4["4️⃣<br/>⚖️ Treatment<br/>vs Control"]
    P4 --> P5["5️⃣<br/>📄 Experiment<br/>Report"]

    style P1 fill:#1f2937,stroke:#a78bfa,stroke-width:2px,color:#fff
    style P2 fill:#1f2937,stroke:#38bdf8,stroke-width:2px,color:#fff
    style P3 fill:#1f2937,stroke:#fbbf24,stroke-width:2px,color:#fff
    style P4 fill:#1f2937,stroke:#f87171,stroke-width:2px,color:#fff
    style P5 fill:#1f2937,stroke:#4ade80,stroke-width:2px,color:#fff
```

### 1️⃣ Generate Population

| Control | Behavior |
|---|---|
| **Population size** | 5,000 → 30,000 customers |
| **Reproducible seed** | Same seed → same generated values and structure |
| **Generation** | One-click synthetic population generation |

> UUID identifiers are generated as identifiers and are **not** expected to be identical across separate runs.

**Company-facing fields:**

```text
age · gender · city · state · latitude · longitude · device
customer_type · order_frequency · average_order_value · recency
sessions_30d · cart_abandonments
```

A separate **hidden behavioral state** is also generated (see [Observable vs Hidden Variables](#-observable-vs-hidden-variables)).

### 2️⃣ India Population Map
Geographic visualization of the population and similarity network. See [India Population Map & Similarity Network](#-india-population-map--similarity-network).

### 3️⃣ Company Experiment
Configure the business experiment. See [Experiment Simulation Engine](#-experiment-simulation-engine).

### 4️⃣ Treatment vs Control
Detailed statistical analysis. See [Statistical Engine](#-statistical-engine).

### 5️⃣ Experiment Report
Executive-style report with downloadable outputs. See [Experiment Report](#-experiment-report).

---

## 🧬 Synthetic Population Model

The population is **not** generated by independently sampling each column. The generator starts from a **correlated latent-factor model** using a correlation matrix and Cholesky decomposition.

```mermaid
flowchart TD
    CM["🔗 Correlation Matrix<br/>+ Cholesky Decomposition"] --> L1["💼 Socioeconomic"]
    CM --> L2["🔥 Engagement"]
    CM --> L3["📱 Digital"]
    CM --> L4["💰 Price"]
    CM --> L5["✨ Novelty"]
    CM --> L6["🛡️ Risk"]

    L1 --> A1["Age · Income · Orders · AOV"]
    L2 --> A2["Orders · Sessions · Recency"]
    L3 --> A3["Device · Sessions · Novelty"]
    L4 --> A4["Price Sensitivity · Recency · Cart Abandonment"]
    L5 --> A5["Novelty Preference · Risk Preference"]
    L6 --> A6["Risk Preference"]

    style CM fill:#0f172a,stroke:#c084fc,stroke-width:3px,color:#fff
    style L1 fill:#1e293b,stroke:#60a5fa,stroke-width:2px,color:#fff
    style L2 fill:#1e293b,stroke:#fbbf24,stroke-width:2px,color:#fff
    style L3 fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#fff
    style L4 fill:#1e293b,stroke:#34d399,stroke-width:2px,color:#fff
    style L5 fill:#1e293b,stroke:#a78bfa,stroke-width:2px,color:#fff
    style L6 fill:#1e293b,stroke:#f87171,stroke-width:2px,color:#fff
```

### 🔗 Behavioral Relationships

| Attribute | Depends On |
|---|---|
| **Age** | Socioeconomic position + stochastic variation (bounded to adult range) |
| **Income** 🔒 | Socioeconomic behavior + age + stochastic variation |
| **Orders** | Socioeconomic position + engagement + age |
| **AOV** | Socioeconomic behavior + purchase frequency + age + stochastic variation |
| **Sessions** | Engagement + order activity + digital behavior |
| **Price sensitivity** 🔒 | Bounded stochastic behavior + latent price factor + age-related behavior |
| **Novelty preference** 🔒 | Stochastic variation + novelty behavior + digital behavior |
| **Risk preference** 🔒 | Stochastic variation + latent risk behavior + novelty preference |
| **Recency** | Engagement + price sensitivity *(not an independent random number)* |
| **Device** | Age + digital behavior |
| **Cart abandonment** | Price sensitivity + device + engagement + number of sessions |
| **Customer lifecycle** | Derived from order activity + recency → `New` / `Repeat` / `Loyal` |
| **Product affinity** 🔒 | Heterogeneous hidden affinities for Beauty / Electronics / Grocery |

---

## 🔐 Observable vs Hidden Variables

> **A key architectural boundary.**

```mermaid
flowchart LR
    G["🧬 Latent Factor Generator<br/>Correlated Behavioral Engine"]

    G -->|"exposed"| API["🌐 Population API"]
    G -->|"withheld"| TRUTH["🔒 simulator_truth table"]

    API --> V1["age · gender · city · state<br/>lat · lon · device · customer_type<br/>orders · aov · recency_days<br/>sessions_30d · cart_abandonments"]
    TRUTH --> V2["profession · income<br/>price_sensitivity · novelty_preference<br/>risk_preference<br/>beauty / electronics / grocery affinity"]

    style G fill:#0f172a,stroke:#a78bfa,stroke-width:2px,color:#fff
    style API fill:#0f172a,stroke:#34d399,stroke-width:2px,color:#fff
    style TRUTH fill:#0f172a,stroke:#f87171,stroke-width:2px,color:#fff
```

| 👁️ Company-Observable | 🔒 Hidden Simulator Fields |
|---|---|
| age, gender, city, state | profession, income |
| lat, lon | price_sensitivity |
| device, customer_type | novelty_preference |
| orders, aov, recency_days | risk_preference |
| sessions_30d, cart_abandonments | beauty / electronics / grocery affinity |

Hidden variables create **heterogeneous treatment response** and are **never returned** by the normal company-facing population endpoint. The company experiences an experimentation environment, not a cheat sheet of the simulator's internal ground truth.

---

## 🧪 Diagnostics & Real-Data Benchmark

### Population Diagnostics

A **generator-consistency diagnostic** answers one question: *is the generator behaving consistently with the relationships it was designed to model?*

```mermaid
mindmap
  root((Population Diagnostics))
    Age coverage
    Income and AOV
    Orders and Sessions
    Engagement and Recency
    Cart-friction behavior
    Lifecycle ordering
    Geographic diversity
```

> [!IMPORTANT]
> It does **not** claim the synthetic population is statistically identical to real people. Real-world realism requires calibration against appropriate real customer data.

### Real-Data Behavioral Benchmark

The repository includes a real, non-synthetic sample:

```text
data/reference/online_retail_real_sample.csv
```

| Field | Value |
|---|---|
| **Rows** | 1,950 real transactions |
| **Source** | Daqing Chen, *Online Retail II* |
| **Repository** | UCI Machine Learning Repository |
| **DOI** | [10.24432/C5CG6D](https://doi.org/10.24432/C5CG6D) |
| **License** | CC BY 4.0 |
| **Origin** | UK-based non-store online retailer |

**Metrics compared** (via empirical distribution distance): order frequency, relative AOV distribution shape, recency, and lifecycle composition.

**AOV normalization:** the source is GBP-denominated while the app uses INR, so the benchmark compares *relative AOV shape* rather than pretending the currencies are directly comparable.

> [!CAUTION]
> This is a **behavioral reference benchmark**, not an Indian population-representativeness test. It does **not** establish that the synthetic population matches Indian demographics, geography, device usage, currency behavior, or customer composition. A future release can add a verified Indian customer dataset when suitable data and redistribution rights are available.

---

## 🗺️ India Population Map & Similarity Network

Customer locations are generated around major Indian city centers with customer-level geographic jitter, spread across many cities:

```text
Delhi · Mumbai · Bengaluru · Hyderabad · Chennai · Kolkata · Pune
Ahmedabad · Jaipur · Surat · Lucknow · Kanpur · Nagpur · Indore
Bhopal · Patna · Vadodara · Coimbatore · Kochi · Visakhapatnam · …
```

### 🛰️ Cyber-Intelligence Design

The UI is styled as a command-center visualization (`CUSTOMER INTELLIGENCE GRID // INDIA`) rather than a typical dashboard map:

- 🌑 Dark geographic base map
- 💫 Neon network links and glowing customer nodes
- 🌈 Feature-specific signal colors
- 🃏 Dark hover cards and subtle grid styling
- 📡 `LIVE SIGNAL` status indicator, technical header, and command-center footer

### 🕸️ Customer Similarity Network

Synthetic customers are **nodes**; observable behavioral similarity forms **edges**.

| Feature | Signal Meaning |
|---|---|
| `gender` | Same gender |
| `device` | Same device |
| `customer_type` | Same lifecycle |
| `age` | Similar age |
| `orders` | Similar order frequency |
| `aov` | Similar AOV |
| `recency` | Similar recency |
| `sessions` | Similar sessions |
| `cart_abandonments` | Similar cart abandonment |

The network is **global across the population**, not restricted to same-city relationships. City is a geographic attribute; similarity is computed independently of city boundaries.

```mermaid
flowchart LR
    B["🏙️ Bengaluru"] -->|"similar behavior"| M["🏙️ Mumbai"]
    M -->|"similar AOV"| D["🏙️ Delhi"]
    D -->|"similar sessions"| C["🏙️ Chennai"]

    style B fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#fff
    style M fill:#1e293b,stroke:#a78bfa,stroke-width:2px,color:#fff
    style D fill:#1e293b,stroke:#fbbf24,stroke-width:2px,color:#fff
    style C fill:#1e293b,stroke:#34d399,stroke-width:2px,color:#fff
```

> [!IMPORTANT]
> **Network semantics are intentionally conservative.** An edge means *measurable observable similarity*. It does **not** prove true behavioral identity, causal similarity, social influence, common cause, or peer effects. **No edge does not mean no similarity**, only that it was not sufficiently observable under the selected graph construction. Network centrality is descriptive, not causal influence.

### ⚡ On-Demand Network Construction

The network is deliberately **separated** from population generation, reducing peak memory and latency on the small Render deployment.

```mermaid
sequenceDiagram
    autonumber
    participant UI as 🎨 Streamlit UI
    participant API as ⚡ FastAPI
    participant DB as 🐘 Neon PostgreSQL

    rect rgb(15, 23, 42)
    Note over UI,DB: Fast population path
    UI->>API: POST /population/generate
    API->>API: Generate customers + hidden behavior
    API->>DB: Batch-write customers
    API->>DB: Batch-write simulator truth
    API-->>UI: Return population ID
    end

    rect rgb(30, 41, 59)
    Note over UI,DB: Map / network path
    UI->>API: Open India map
    UI->>API: Enable similarity network
    API->>DB: Build / rebuild observable graph
    API->>DB: Store graph edges
    UI->>API: GET /network (strongest edges)
    API-->>UI: Render intelligence network
    end
```

### 🧠 Graph Performance Engineering

An earlier implementation accumulated a large graph in Python before inserting into PostgreSQL. For 30,000 customers × 9 features, that created many dictionaries, UUID strings, JSON objects, and temporary arrays. Current optimizations:

```mermaid
flowchart LR
    O1["On-demand graph build"] --> R
    O2["Batched customer inserts"] --> R
    O3["Batched truth inserts"] --> R
    O4["Feature-by-feature generation"] --> R
    O5["Batched edge inserts"] --> R
    O6["Feature-local duplicate tracking"] --> R
    O7["Bounded API payloads"] --> R
    O8["Native-library thread limits"] --> R
    O9["Explicit cache invalidation"] --> R
    R["⚡ Reduced Peak Memory"]

    style R fill:#065f46,stroke:#4ade80,stroke-width:3px,color:#fff
```

The UI also requests a **bounded strongest-edge budget** rather than every possible edge.

---

## 📊 Experiment Simulation Engine

The experiment page is intentionally **generalized**, not tied to one industry.

### 🧪 Supported Experiment Types

| # | Type | # | Type |
|:-:|---|:-:|---|
| 1 | 📣 Marketing campaign | 6 | 🎯 Recommendation / personalization |
| 2 | 🛍️ Product promotion | 7 | ✉️ Messaging / copy |
| 3 | 🖥️ New UI / feature | 8 | 🔁 Retention / loyalty |
| 4 | 💳 Checkout redesign | 9 | 🔍 Search / discovery |
| 5 | 💰 Pricing / discount | 10 | ➕ Other |

**Product categories:** `General` · `Beauty` · `Electronics` · `Grocery` · `Fashion` · `Home` · `Sports` · `Travel` · `Finance` · `SaaS`

### 📝 Business Inputs

| Input | Description |
|---|---|
| Experiment / campaign name | Identifier for the run |
| Product / service / experience | What is being tested |
| Category | Vertical context |
| Business hypothesis | The belief under test |
| Control / current experience | Baseline |
| Treatment / proposed experience | Variant |
| Primary success metric | KPI |
| Target segment | Audience |
| Treatment share | Randomization ratio |
| Experiment seed | Reproducibility |

**Primary metrics:** `conversion_rate` · `revenue_per_customer` · `average_order_value` · `retention_rate` · `checkout_completion` · `click_through_rate` · `add_to_cart_rate`

> [!NOTE]
> The current statistical test is based on **conversion proportions**. The selected business metric is preserved as experiment context for reporting.

### 🎲 Randomization & Heterogeneous Response

Customers are assigned to treatment/control using a **seeded random permutation**. The response model is **heterogeneous**: customers do not all receive the same treatment effect.

**Baseline response drivers:** order history, session activity, recency, 🔒 price sensitivity, 🔒 product affinity.

| Experiment Type | Response Mechanism Uses |
|---|---|
| 📣 Marketing campaign | Heterogeneous affinity + price sensitivity |
| 🛍️ Product promotion | Category affinity + behavioral heterogeneity |
| 🖥️ New UI / feature | Mobile behavior + novelty preference |
| 💳 Checkout redesign | Cart abandonment + session activity |
| 💰 Pricing / discount | Price sensitivity |
| 🎯 Recommendation / personalization | Product affinity + novelty preference |
| ✉️ Messaging / copy | Novelty preference |
| 🔁 Retention / loyalty | `Repeat` and `Loyal` lifecycle states |
| 🔍 Search / discovery | Novelty preference |

> [!WARNING]
> These are **simulator priors**, not claims about measured real-world effect sizes.

---

## 📈 Statistical Engine

### Core Metrics

| Metric | Definition |
|---|---|
| Control / treatment conversion | Conversion rate per arm |
| **Absolute uplift** | `treatment_rate − control_rate` |
| **Relative uplift** | `(treatment_rate − control_rate) / control_rate` (when control rate ≠ 0) |
| Control / treatment revenue | Total revenue per arm |
| Revenue per customer | Normalized revenue |
| Revenue delta | Difference between arms |
| 95% confidence interval | Uncertainty band on the difference |

```math
\text{absolute uplift} = p_{\text{treatment}} - p_{\text{control}}
\qquad
\text{relative uplift} = \frac{p_{\text{treatment}} - p_{\text{control}}}{p_{\text{control}}}
```

### 📐 95% Confidence Interval

A **two-sided** interval for the difference in conversion proportions, using a **normal approximation**.

```mermaid
flowchart LR
    CI["📐 95% Confidence Interval"] --> W["✅ Represents<br/>randomization / sampling variability<br/>within the synthetic experiment"]
    CI --> X["❌ Does NOT include<br/>uncertainty about whether<br/>simulator assumptions are correct"]

    style W fill:#065f46,stroke:#4ade80,stroke-width:2px,color:#fff
    style X fill:#7f1d1d,stroke:#f87171,stroke-width:2px,color:#fff
```

This distinction is explicitly communicated in the UI and report.

### 🧪 Hypothesis Testing

| Component | Definition |
|---|---|
| **H₀** | treatment conversion = control conversion |
| **H₁** | treatment conversion ≠ control conversion |
| **Test** | Two-sided two-proportion **z-test** |
| **Default α** | `0.05` |
| **Reported** | z-statistic · p-value · significance decision |

```mermaid
flowchart LR
    P["📊 p-value"] --> D{"p < 0.05 ?"}
    D -->|"Yes"| R["🚫 Reject H₀"]
    D -->|"No"| F["🤝 Do not reject H₀"]

    style R fill:#065f46,stroke:#4ade80,stroke-width:2px,color:#fff
    style F fill:#78350f,stroke:#fbbf24,stroke-width:2px,color:#fff
```

> [!IMPORTANT]
> The p-value does **not** mean "there is a 95% probability that treatment will work on real customers." It measures the compatibility of the observed simulated difference with the null hypothesis **under the assumptions of the selected test**.

### 📏 Power & Minimum Detectable Effect

The platform computes an **approximate 80% power MDE**.

| Input | Source |
|---|---|
| Control / treatment sample size | From the experiment |
| Baseline conversion | From control |
| Alpha | `0.05` |
| Target power | `0.80` |

The MDE estimates the smallest positive absolute conversion uplift expected to be detectable with the current design under a normal approximation. It answers: *"How large would the effect need to be for the current sample size to reliably detect it?"* It is a **design-sensitivity measure, not a guarantee**.

### 🧩 Segment Analysis

Segment results are produced for **gender** and **customer lifecycle**, each with control rate, treatment rate, uplift, and sample size.

> These are useful for spotting potentially heterogeneous response patterns, but should be treated as **exploratory** unless a future real experiment is explicitly designed and powered for subgroup analysis.

---

## 📄 Experiment Report

An executive-style report containing:

- **Business setup:** experiment type, product/experience, category, population size, treatment share, target segment, primary metric, hypothesis, control experience, proposed treatment
- **Results:** control/treatment conversion, absolute and relative uplift, 95% CI, p-value, significance decision, approximate 80% power MDE, revenue and revenue per customer

### 🧭 Decision Recommendation

```mermaid
flowchart TD
    CI{"95% CI of the<br/>simulated uplift"}
    CI -->|"entirely above 0"| RP["🟢 POSITIVE<br/>Consider a real pilot"]
    CI -->|"entirely below 0"| RN["🔴 NEGATIVE<br/>Do not pursue"]
    CI -->|"crosses 0"| RI["🟡 INCONCLUSIVE<br/>Insufficient signal"]

    style CI fill:#0f172a,stroke:#c084fc,stroke-width:2px,color:#fff
    style RP fill:#065f46,stroke:#4ade80,stroke-width:3px,color:#fff
    style RN fill:#7f1d1d,stroke:#f87171,stroke-width:3px,color:#fff
    style RI fill:#78350f,stroke:#fbbf24,stroke-width:3px,color:#fff
```

> These are recommendations about whether a **real pilot should be considered**, not claims that the same effect will appear with real customers.

### 🧾 Downloadable Outputs

| Format | Purpose |
|---|---|
| 📝 Markdown | Executive report |
| 🧾 JSON | Experiment result for archiving, inspection, or sharing |

---

## 🗄️ Data Model

Neon is the **only persistent application database**. The schema contains seven principal tables.

```mermaid
erDiagram
    population_runs ||--o{ customers : has
    customers ||--|| simulator_truth : "hidden state"
    customers ||--o{ customer_edges : "linked by"
    population_runs ||--o{ experiments : has
    experiments ||--o{ experiment_outcomes : produces
    customers ||--o{ experiment_outcomes : "assigned to"
    experiments ||--o{ segment_results : aggregates

    population_runs {
        uuid population_id PK
        int seed
        int population_size
        timestamp created_at
        json generator_config
    }

    customers {
        uuid id PK
        uuid population_id FK
        int age
        string gender
        string city
        string state
        float latitude
        float longitude
        string device
        string customer_type
        int orders
        float aov
        int recency
        int sessions
        int cart_abandonment
    }

    simulator_truth {
        uuid customer_id FK
        string profession
        float income
        float price_sensitivity
        float novelty_preference
        float risk_preference
        float beauty_affinity
        float electronics_affinity
        float grocery_affinity
    }

    customer_edges {
        uuid source_customer FK
        uuid target_customer FK
        float similarity_weight
        string view
        json explanation
    }

    experiments {
        uuid experiment_id PK
        uuid population_id FK
        string experiment_name
        string category
        float treatment_share
        int seed
        json business_config
    }

    experiment_outcomes {
        uuid experiment_id FK
        uuid customer_id FK
        string arm
        boolean conversion
        float revenue
    }

    segment_results {
        uuid experiment_id FK
        string segment
        float control_rate
        float treatment_rate
        float uplift
        int sample_size
    }
```

<details>
<summary><b>📚 Table reference</b></summary>

<br/>

| Table | Contents |
|---|---|
| `population_runs` | Population ID, seed, size, timestamp, generator configuration |
| `customers` | Company-observable synthetic population (demographics, geography, device, lifecycle, orders, AOV, recency, sessions, cart abandonment) |
| `simulator_truth` | Hidden state: profession, income, price/novelty/risk preference, product affinities |
| `customer_edges` | Source/target customer, similarity weight, `view` (`observable` \| `truth`), JSON explanation. The normal map uses the `observable` view |
| `experiments` | Identity, population, name, category, treatment share, seed, business configuration |
| `experiment_outcomes` | Customer-level experiment, customer, arm, conversion, revenue |
| `segment_results` | Segment-level control/treatment rates, uplift, sample size |

> 💡 Experiment business setup is stored as **JSON** so the simulator can evolve without a schema migration for every new field.

</details>

---

## 🔌 API Reference

| Method | Endpoint | Purpose |
|:---:|:---|:---|
| `GET` | `/health` | API and database health |
| `POST` | `/population/generate` | Generate and persist a population |
| `GET` | `/population/{id}` | Read a customer sample |
| `GET` | `/population/{id}/map` | Geographic map payload |
| `GET` | `/population/{id}/diagnostics` | Generator-consistency diagnostics |
| `GET` | `/population/{id}/reference-behavior` | Real-data behavioral benchmark |
| `POST` | `/population/{id}/network/rebuild` | Build observable customer network |
| `GET` | `/network` | Strongest selected edges |
| `GET` | `/graph/analytics` | Network analytics |
| `POST` | `/experiments/simulate` | Run a synthetic experiment |
| `GET` | `/experiments/{id}` | Retrieve an experiment |
| `GET` | `/experiments` | List experiments |
| `GET` | `/reference-behavior/summary` | Benchmark metadata |

📖 Interactive Swagger documentation is served at **`/docs`**.

---

## 🧱 Repository Structure

```text
synthetic-experimentation-lab/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── simulation.py
│   │   ├── analytics.py
│   │   ├── population_quality.py
│   │   ├── reference_behavior.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── db.py
│   │   └── config.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── data/
│   └── reference/
│       ├── README.md
│       └── online_retail_real_sample.csv
├── tests/
│   └── test_simulation.py
├── cloudflare_backend/
│   ├── README.md
│   └── src/index.js
├── .github/workflows/ci.yml
├── schema.sql
├── docker-compose.yml
├── wrangler.toml
├── package.json
├── pytest.ini
├── .env.example
└── README.md
```

---

## ⚙️ Local Development

**Prerequisites:** Python 3.12 · Docker · Git · a PostgreSQL connection (preferably Neon)

### 🔐 Environment

Create local settings from `.env.example`:

```env
APP_ENV=development
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DBNAME?sslmode=require
CORS_ORIGINS=*
DB_POOL_SIZE=3
DB_MAX_OVERFLOW=2
API_BASE_URL=http://localhost:8000
```

### 🐳 Run with Docker Compose

```bash
docker compose up --build
```

| Service | URL |
|:---|:---|
| 🎨 Streamlit | https://synthetic-experimentation-lab.streamlit.app |
| ⚡ FastAPI | https://synthetic-experimentation-lab.onrender.com |
| 📖 Swagger | https://synthetic-experimentation-lab.onrender.com/docs |

### 🧪 Run Tests

```bash
pip install -r backend/requirements.txt pytest
pytest -q
```

### 🗃️ Neon Configuration

The backend accepts either URL form:

```text
postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require
postgresql+psycopg://USER:PASSWORD@HOST/DBNAME?sslmode=require
```

```mermaid
flowchart LR
    A["Standard Neon URL<br/>postgresql://…"] --> B["⚙️ Backend normalizer"]
    B --> C["SQLAlchemy psycopg form<br/>postgresql+psycopg://…"]
    C --> D[("🐘 Neon PostgreSQL")]

    style B fill:#0f172a,stroke:#c084fc,stroke-width:2px,color:#fff
```

- ✅ The standard Neon URL is **automatically normalized** to the SQLAlchemy `psycopg` form.
- ✅ Missing ORM tables are **created on startup**, so a fresh Neon database works without a separate migration service.
- 📄 `schema.sql` is included as a human-readable SQL reference.

---

## ☁️ Deployment

```mermaid
flowchart LR
    S["🎨 Streamlit<br/>Community Cloud"] --> R["⚡ Render<br/>FastAPI"] --> N[("🐘 Neon<br/>PostgreSQL")]

    style S fill:#1e293b,stroke:#FF4B4B,stroke-width:2px,color:#fff
    style R fill:#1e293b,stroke:#46E3B7,stroke-width:2px,color:#fff
    style N fill:#1e293b,stroke:#00E599,stroke-width:2px,color:#fff
```

### ⚡ Backend: Render (primary)

Create a standard **Render Web Service**:

| Setting | Value |
|---|---|
| Runtime | Docker |
| Dockerfile | `./backend/Dockerfile` |
| Docker context | `./backend` |
| Health check path | `/health` |
| `APP_ENV` | `production` |
| `DATABASE_URL` | Your Neon connection string |

Verify the deployment:

```bash
curl https://YOUR-SERVICE.onrender.com/health
```

Expected response:

```json
{"status": "ok", "database": "connected"}
```

> [!NOTE]
> Render free services can spin down after inactivity, so cold starts may be slower. Graph construction is separated from population generation to reduce memory and latency pressure.

### 🎨 Frontend: Streamlit Community Cloud

| Setting | Value |
|---|---|
| Branch | `main` |
| Entrypoint | `frontend/app.py` |
| Dependencies | `frontend/requirements.txt` |
| Python | 3.12 |

Add this secret (an environment variable named `API_BASE_URL` also works):

```toml
API_BASE_URL = "https://YOUR-SERVICE.onrender.com"
```

### ☁️ Optional: Cloudflare Containers

Included as an **optional** backend path via `wrangler.toml`, `cloudflare_backend/src/index.js`, and `cloudflare_backend/README.md`.

- 🐳 Runs the existing backend Dockerfile.
- 📦 The container profile is larger than the normal Workers runtime, suited to the Python/NumPy workload.
- 💳 Requires a **Workers Paid plan**, so the recommended free path remains **Streamlit → Render → Neon**.

---

## 🔁 CI & Testing

```mermaid
flowchart LR
    C1["1️⃣ Python<br/>compilation"] --> C2["2️⃣ Pytest"] --> C3["3️⃣ Backend<br/>Docker build"] --> C4["4️⃣ Frontend<br/>Docker build"]

    style C1 fill:#1e293b,stroke:#60a5fa,stroke-width:2px,color:#fff
    style C2 fill:#1e293b,stroke:#a78bfa,stroke-width:2px,color:#fff
    style C3 fill:#1e293b,stroke:#2496ED,stroke-width:2px,color:#fff
    style C4 fill:#1e293b,stroke:#FF4B4B,stroke-width:2px,color:#fff
```

CI build contexts match deployment build contexts, providing a basic release gate before changes reach hosting.

| Area | What Is Verified |
|---|---|
| 🔁 Reproducibility | Same seed → same population values and structure |
| 🔒 Hidden boundary | Income absent from the company-facing customer object, present in simulator truth |
| 📊 Statistics | Confidence intervals, two-proportion z-test, p-values, significance, approximate MDE / power |
| 🕸️ Network | Cross-city, feature-based similarity |
| 🧬 Correlated structure | Income/AOV and orders/sessions relationships |
| 🧪 Diagnostics | Valid consistency score |
| 📏 Real-data benchmark | Dataset loading, source metadata, alignment outputs, metric score ranges |
| 🎲 Experiment mechanisms | Multiple experiment types produce treatment/control outcomes |

---

## 🧠 Statistical Interpretation & Limitations

The platform deliberately distinguishes **three different sources of uncertainty**:

```mermaid
flowchart TD
    U["🧠 Sources of Uncertainty"] --> U1["1️⃣ Sampling /<br/>randomization variability"]
    U --> U2["2️⃣ Experiment-design<br/>sensitivity"]
    U --> U3["3️⃣ Simulator-assumption<br/>uncertainty"]

    U1 --> M1["📐 Captured approximately by<br/>confidence interval · p-value"]
    U2 --> M2["📏 Summarized approximately by<br/>power · MDE"]
    U3 --> M3["🚨 NOT captured by the current<br/>p-value or confidence interval"]

    style U3 fill:#7f1d1d,stroke:#f87171,stroke-width:3px,color:#fff
    style M3 fill:#7f1d1d,stroke:#f87171,stroke-width:2px,color:#fff
```

> [!CAUTION]
> **This is the most important limitation.** A highly significant synthetic result can still be wrong for the real world if the simulator mechanisms are misspecified.

### ✅ Intended Workflow

```mermaid
flowchart LR
    A["🧪 Synthetic<br/>result"] --> B["📶 Decision<br/>signal"] --> C["🧑‍🤝‍🧑 Real controlled<br/>pilot"] --> D["🌍 Real-world<br/>evidence"]

    style A fill:#1e293b,stroke:#a78bfa,stroke-width:2px,color:#fff
    style B fill:#1e293b,stroke:#fbbf24,stroke-width:2px,color:#fff
    style C fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#fff
    style D fill:#1e293b,stroke:#4ade80,stroke-width:2px,color:#fff
```

---

## 🔒 Security & Data Boundaries

```mermaid
flowchart LR
    F["🎨 Frontend"] -->|"API calls only"| A["⚡ FastAPI"]
    A -->|"DATABASE_URL"| D[("🐘 Neon")]
    F -.-x|"no DB credentials"| D

    style F fill:#1e293b,stroke:#FF4B4B,stroke-width:2px,color:#fff
    style A fill:#1e293b,stroke:#009688,stroke-width:2px,color:#fff
    style D fill:#1e293b,stroke:#00E599,stroke-width:2px,color:#fff
```

- ✅ The frontend **never receives database credentials**.
- ✅ Only FastAPI owns `DATABASE_URL`; the Streamlit app only knows the API base URL.
- ✅ Use `.env.example` as the environment template.

> [!CAUTION]
> **Never commit** `DATABASE_URL`, Neon passwords, private credentials, or production secrets.

---

## 📌 Project Status

<table>
<tr>
<td valign="top" width="50%">

**🧬 Data & Simulation**
- ✅ Up to 30,000 synthetic customers
- ✅ Correlated latent-factor generation
- ✅ Hidden simulator truth
- ✅ Observable customer boundary
- ✅ Indian geographic distribution
- ✅ Interactive India map
- ✅ Cyber-intelligence visual theme
- ✅ Cross-city observable similarity network
- ✅ On-demand network construction
- ✅ Population structure diagnostics
- ✅ Real-data behavioral benchmark

</td>
<td valign="top" width="50%">

**📊 Experimentation & Statistics**
- ✅ Generalized experiment design
- ✅ Randomized control/treatment assignment
- ✅ Heterogeneous simulation mechanisms
- ✅ Conversion uplift and revenue analysis
- ✅ 95% confidence intervals
- ✅ Two-proportion hypothesis test and p-values
- ✅ Alpha-based significance decisions
- ✅ Approximate 80% power MDE
- ✅ Segment analysis
- ✅ Executive decision report
- ✅ Markdown and JSON downloads

</td>
</tr>
<tr>
<td valign="top" width="50%">

**🏗️ Infrastructure**
- ✅ Neon PostgreSQL persistence
- ✅ FastAPI backend
- ✅ Streamlit frontend

</td>
<td valign="top" width="50%">

**🚀 Deployment & CI**
- ✅ Docker deployment
- ✅ Render deployment path
- ✅ Streamlit Community Cloud path
- ✅ Optional Cloudflare Container packaging
- ✅ GitHub Actions CI

</td>
</tr>
</table>

---

## 🏁 Portfolio Positioning

```mermaid
mindmap
  root((Synthetic Experimentation Lab))
    Synthetic Data Generation
    Probabilistic Modeling
    Behavioral Simulation
    Experiment Design
    Randomization
    Statistical Inference
    Power Analysis
    Graph Analytics
    Geospatial Visualization
    Real-Data Benchmarking
    PostgreSQL Data Modeling
    FastAPI
    Docker
    CI/CD
    Cloud Deployment
```

> **A synthetic experimentation platform that lets companies test experiment mechanisms, estimate simulated uplift, quantify statistical uncertainty, and identify potentially responsive segments, before spending real customer traffic on a pilot.**

---

## 📚 Data Attribution

The real-data benchmark is derived from:

> Chen, D. (2012). *Online Retail II* [Dataset]. UCI Machine Learning Repository.

| Field | Value |
|---|---|
| **DOI** | [10.24432/C5CG6D](https://doi.org/10.24432/C5CG6D) |
| **License** | CC BY 4.0 |

See [`data/reference/README.md`](data/reference/README.md) for sample provenance and scope.

---

## ⚠️ Final Interpretation

<div align="center">

### Use synthetic experimentation to decide what deserves a real experiment.

</div>

**The platform can help reveal:**

- 🔍 Whether an experiment mechanism is internally plausible
- 🎯 Which segments appear sensitive in the simulator
- 📈 How large a simulated uplift could be
- 📉 How uncertain that simulated estimate is
- 📏 Whether the current sample size can detect a meaningful effect
- 🚀 Whether the idea appears worth piloting

**It cannot prove** that real customers will behave identically.

> A synthetic result is a **pre-experiment decision signal**, not a substitute for controlled real-world experimentation.

---

<div align="center">

### ⭐ [github.com/Harshithpatali/synthetic-experimentation-lab](https://github.com/Harshithpatali/synthetic-experimentation-lab)

**Built with 🧪 statistics, 🧬 simulation, and 🐘 PostgreSQL**

*Star the repo if it helped you think about experimentation differently.*

</div>
