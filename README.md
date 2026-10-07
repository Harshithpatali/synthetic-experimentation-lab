# Synthetic Experimentation Lab

**Test the experiment before testing it on real customers.**

A Python data-science platform where a company defines an experiment, a synthetic population is randomized into control/treatment, heterogeneous simulated outcomes are generated, and the company inspects uplift, uncertainty and segment behavior before deciding whether to run a real-world pilot.

## Final architecture

```
Streamlit
   │ HTTP
   ▼
Cloudflare Worker
   │
   ▼
Cloudflare Container
   │ FastAPI + Python
   ▼
Neon PostgreSQL
```

The frontend is **Streamlit**. The backend is **FastAPI + Python running inside a Cloudflare Container**. Neon is the only application database/storage system. There is no React frontend and no Cloudflare R2 dependency.

Cloudflare Containers are a good fit here because the backend keeps a normal Linux/Python runtime and Docker image instead of forcing the simulation into the Python Workers WebAssembly runtime.

## Product flow

```
Company experiment idea
        ↓
Synthetic population
        ↓
Observable + simulator-hidden behavior
        ↓
Random control / treatment assignment
        ↓
Simulated customer responses
        ↓
Uplift + uncertainty + segment analysis
        ↓
Company decides whether to run a real-world pilot
```

## Observable vs hidden variables

### Company-observable

- age
- gender
- city/state and approximate location
- device
- customer type
- orders
- AOV
- recency
- sessions
- cart abandonment

### Simulator-internal

- profession
- income
- price sensitivity
- novelty preference
- risk preference
- category affinity

The company-facing population endpoint never returns the hidden simulator fields.

## Graph semantics

The graph represents **measurable evidence of similarity**.

An edge does not prove that two customers are truly similar.

Likewise:

> **No edge ≠ no similarity**

It means that similarity was not sufficiently observable/measurable under the selected graph construction.

The simulator-truth network is an internal diagnostic showing how hidden structure can differ from observable structure.

## Run locally

Install Docker Desktop and run:

```bash
docker build -f Dockerfile.api -t synthetic-lab-api .
docker run --rm -p 8000:8000 -e DATABASE_URL="YOUR_NEON_CONNECTION_STRING" synthetic-lab-api
```

Run Streamlit separately:

```bash
pip install -r requirements.txt
API_BASE_URL=http://localhost:8000 streamlit run streamlit_app.py
```

## Neon setup

Run `schema.sql` against your Neon PostgreSQL database.

Then obtain the Neon connection string.

Do not commit it.

The Cloudflare Container receives it as the `DATABASE_URL` Worker secret.

## Cloudflare backend

This repository uses Cloudflare Containers.

Requirements:

- Cloudflare Workers Paid plan
- Docker-compatible build environment
- Cloudflare API token
- Cloudflare account ID
- Neon PostgreSQL connection string

Cloudflare builds the `Dockerfile.api`, deploys the FastAPI container, and exposes it through the Worker.

The Worker itself is only a thin routing layer. Your actual application backend remains Python/FastAPI.

## GitHub Actions secrets

Add:

```text
CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID
```

Do **not** add `DATABASE_URL` to GitHub unless you deliberately want GitHub Actions to use the database.

The deployment workflow deploys the Worker/container. The Neon credential is a Cloudflare Worker secret.

## Cloudflare secret

Create:

```text
DATABASE_URL
```

Set it to your Neon PostgreSQL connection string.

For example:

```text
postgresql+psycopg://USER:PASSWORD@HOST/DBNAME?sslmode=require
```

Cloudflare passes this secret into the FastAPI container as the `DATABASE_URL` environment variable.

## Deploy

Install dependencies:

```bash
npm install
```

Authenticate Wrangler:

```npx wrangler login
```

Set the database secret:

```npx wrangler secret put DATABASE_URL
```

Deploy:

```npx wrangler deploy
```

Or push to `main` and GitHub Actions will deploy using:

```text
CLOUDFLARE_API_TOKEN
CLOUDFLARE_ACCOUNT_ID
```

After deployment, your API will be available at the Worker URL, for example:

```text
https://synthetic-experimentation-lab.<your-subdomain>.workers.dev
```

FastAPI documentation:

```text
https://synthetic-experimentation-lab.<your-subdomain>.workers.dev/docs
```

Health:

```text
https://synthetic-experimentation-lab.<your-subdomain>.workers.dev/health
```

## Streamlit deployment

Deploy the Streamlit frontend separately.

Set this environment variable in the Streamlit deployment:

```text
API_BASE_URL=https://synthetic-experimentation-lab.<your-subdomain>.workers.dev
```

The Streamlit application calls FastAPI over HTTPS.

No Neon password is needed in Streamlit.

## Security boundary

```
Streamlit
   │
   │ public API requests
   ▼
Cloudflare
   │
   ▼
FastAPI container
   │
   │ DATABASE_URL secret
   ▼
Neon PostgreSQL
```

Only the backend needs database credentials.

Never expose:

- Neon password
- DATABASE_URL
- Cloudflare API token

to Streamlit.

## Statistical warning

The 95% interval describes randomization/sampling variability in the synthetic run. It does **not** capture uncertainty from the simulator assumptions.

A positive simulated uplift is a reason to consider a real-world pilot, not evidence that the real experiment will have the same effect.
