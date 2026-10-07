# Synthetic Experimentation Lab

**Test the experiment before testing it on real customers.**

A Python-based virtual customer population laboratory. A company defines an experiment, a synthetic population is randomized into control/treatment, heterogeneous simulated outcomes are generated, and the company inspects uplift, uncertainty and segment behavior before deciding whether to run a real-world pilot.

## Architecture

Streamlit -> FastAPI -> Neon PostgreSQL

The application is intentionally **Python + FastAPI + Streamlit + Docker**. There is no React frontend and no Cloudflare Worker runtime.

## Model boundary

**Observable:** age, gender, city/state, location, device, customer type, orders, AOV, recency, sessions and cart abandonment.

**Hidden:** profession, income, price sensitivity, novelty/risk preference and category affinity.

Hidden variables drive heterogeneous behavior but are never returned by the company-facing population API.

## Graph semantics

The customer graph represents **measurable evidence of similarity** from available variables. An edge does not prove two customers are truly similar, and no edge does not prove they are dissimilar. The simulator-truth graph is an internal diagnostic.

## Run locally

```bash
docker compose up --build
```

Open http://localhost:8501 for Streamlit and http://localhost:8000/docs for FastAPI.

For Neon, set `DATABASE_URL` to your Neon PostgreSQL connection string. For local Docker Compose, the compose file supplies its own database URL.

## Secrets

The CI workflow needs no application secrets. Never commit the Neon password. Add deployment credentials only when you choose a container host.

Cloudflare is not required for this Python architecture. If Cloudflare proxies a container host, configure DNS/proxy there. Do not put database credentials into Cloudflare Pages/Workers unless a Cloudflare runtime actually needs them.

If you later use Cloudflare R2, keep its endpoint, bucket, access key and secret on the backend only.

## Statistical warning

The 95% interval describes randomization/sampling variability in the synthetic run. It does not capture uncertainty from simulator assumptions. A positive simulated uplift is a reason to consider a real-world pilot, not evidence that the real experiment will have the same effect.
