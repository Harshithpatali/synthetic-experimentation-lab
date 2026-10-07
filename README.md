# Synthetic Experimentation Lab

**Test the experiment before testing it on real customers.**

A Python data-science platform that creates a synthetic customer population, randomizes customers into control/treatment, simulates heterogeneous outcomes, and lets a company inspect uplift, uncertainty, segments, and observable similarity structure before running a real-world pilot.

## Production architecture

    Streamlit Community Cloud
             |
             | HTTPS
             v
    Render Web Service
      Docker + FastAPI
             |
             | SSL
             v
       Neon PostgreSQL

- Frontend: Streamlit
- Backend: FastAPI + Python
- Backend packaging: Docker
- Backend hosting: Render
- Database: Neon PostgreSQL
- Frontend hosting: Streamlit Community Cloud
- No React
- No Cloudflare runtime required
- No R2
- No D1

## Product flow

    Company experiment idea
             |
             v
    Synthetic population
             |
             v
    Observable + hidden simulator behavior
             |
             v
    Random control / treatment assignment
             |
             v
    Simulated customer responses
             |
             v
    Uplift + uncertainty + segment analysis
             |
             v
    Decision about a real-world pilot

## Population generation model

The population generator uses a correlated latent-factor model rather than
independent random draws. Latent socioeconomic, engagement, digital, price,
novelty, and risk factors induce relationships among age, income, order
frequency, AOV, sessions, recency, device usage, cart abandonment, lifecycle
state, and product affinity.

This improves internal behavioural coherence while keeping the generator
lightweight: it uses NumPy only and does not call an LLM or external
generation API.

The application also provides an on-demand **Population Diagnostics** view.
It checks structural relationships such as income↔AOV, orders↔sessions,
engagement↔recency, lifecycle ordering, cart-friction behaviour, and geographic
diversity.

The diagnostics score is explicitly a **generator-consistency score**. It is
not a claim that the synthetic population matches real people. Real-world
fidelity requires calibration against a reference dataset supplied by the
company.

## Real-data behavioral benchmark

The repository now includes a small **real, non-synthetic reference sample**
at:

    data/reference/online_retail_real_sample.csv

It contains 1,950 transaction rows from the public **UCI Online Retail II**
dataset. UCI describes that dataset as real transaction data from a UK-based
registered non-store online retailer and licenses it under **CC BY 4.0**.

Citation:

    Chen, D. (2012). Online Retail II [Dataset].
    UCI Machine Learning Repository.
    https://doi.org/10.24432/C5CG6D

The application reconstructs customer-level reference behavior from the sample
and compares the generated population on metrics that both datasets actually
support:

- order frequency
- relative AOV distribution shape
- recency
- lifecycle composition

The comparison uses empirical distribution distance. AOV is compared by
relative shape rather than raw currency because the reference is priced in GBP
while the synthetic application uses INR.

This is deliberately a **behavioral benchmark**, not an Indian population
representativeness claim. The source is UK retail transaction data, so it does
not validate India-specific demographics, geography, device mix, or currency
levels. A future calibration release can replace or supplement this benchmark
with a verified Indian customer dataset when one with clear provenance and
redistribution terms is available.

## Observable vs hidden variables

Observable:
- age
- gender
- city/state
- approximate location
- device
- customer type
- orders
- AOV
- recency
- sessions
- cart abandonment

Hidden simulator variables:
- profession
- income
- price sensitivity
- novelty preference
- risk preference
- category affinity

Hidden variables create heterogeneous behavior but are never returned by the company-facing population endpoint.

## Graph semantics

The graph represents measurable evidence of similarity.

An edge does not prove two customers are truly similar.

No edge does not mean no similarity.

It means similarity was not sufficiently observable/measurable under the selected graph construction.

The simulator-truth network is an internal diagnostic that uses hidden behavioral structure.

Network centrality is descriptive. It is not causal influence.

## Repository layout

    backend/
      app/
        main.py
        simulation.py
        analytics.py
        models.py
        schemas.py
        db.py
        config.py
      Dockerfile
      requirements.txt

    frontend/
      app.py
      Dockerfile
      requirements.txt

    tests/
    data/
      reference/
        README.md
        online_retail_real_sample.csv
    schema.sql
    docker-compose.yml


## Streamlit workflow

The production frontend is organized as five company-facing pages:

1. Generate Population — create up to 30,000 synthetic customers.
2. India Population Map — plot the synthetic population on a geographic India map and connect the strongest observable-similarity edges.
3. Company Experiment — choose an experiment type such as a marketing campaign, product promotion, new UI/feature, checkout redesign, pricing, personalization, messaging, retention, or search; then define the product/experience, control, treatment, target segment, success metric, treatment share, and seed.
4. Treatment vs Control — inspect conversion, uplift, confidence interval, revenue, arm sizes, and segment results.
5. Experiment Report — produce an executive recommendation and download a Markdown report.

The map shows synthetic customer locations distributed around major Indian cities. The full 30,000-customer population is stored in Neon, while the frontend draws a bounded number of the strongest edges to keep the browser responsive.

The default India map uses a dark technical theme with neon feature-specific
network signals and a subtle glow layer. Users can switch to light or street
maps when geographic context is more important than network visualization.


### Frontend performance

The Streamlit frontend uses a layered cache strategy:
- population map data is cached for 30 minutes;
- network queries are cached for 30 minutes per population, edge budget, and selected feature set;
- backend health is cached briefly rather than checked on every rerun;
- HTTP connections are reused across Streamlit reruns;
- cached population/network data is explicitly invalidated when a new population or rebuilt network is created.

This keeps UI changes such as filters, map styling, and chart tabs from repeatedly downloading the same 30,000-customer payloads.


## Local development

Create a .env file from .env.example and provide a PostgreSQL connection string.

    docker compose up --build

Open:

    http://localhost:8501

FastAPI:

    http://localhost:8000/docs

Run tests:

    pip install -r backend/requirements.txt pytest
    pytest -q

The backend Docker image is built with backend/ as its Docker context. The same context is configured for Render and CI.

## Neon

Neon is the only persistent application database.

The API accepts both the standard Neon URL:

    postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require

and the SQLAlchemy psycopg form:

    postgresql+psycopg://USER:PASSWORD@HOST/DBNAME?sslmode=require

The backend normalizes the standard Neon URL automatically.

The application creates any missing ORM tables on startup, so a fresh Neon database can be used without a separate migration service. schema.sql is kept as a human-readable SQL reference for the database structure.

Never commit the Neon connection string to GitHub.

## Cloudflare backend deployment

The production backend can run as a **Cloudflare Container** while the
Streamlit frontend remains on Streamlit Community Cloud.

This is the recommended deployment target for the current simulator because
the backend can exceed the 512 MiB memory limit of the previous runtime during
30,000-customer generation. Cloudflare Containers support configurable instance
memory; this repository uses the standard-1 profile (4 GiB).

Cloudflare Containers are available on Workers Paid.

The repository includes:

    wrangler.toml
    cloudflare_backend/src/index.js
    cloudflare_backend/README.md

The container builds the existing backend/Dockerfile, listens on port 8000,
and passes DATABASE_URL from a Cloudflare Worker Secret into the FastAPI
container.

Deployment from Cloudflare Workers Builds:

1. Connect the GitHub repository under Workers & Pages -> Workers Builds.
2. Use the repository root as the build root.
3. Deploy with:

    npx wrangler deploy

4. Add the Worker Secret DATABASE_URL with the existing Neon PostgreSQL URL.
5. Optionally add CORS_ORIGINS with a comma-separated list of allowed origins,
   or leave it as *.
6. After the container provisions, verify /health.
7. Set the Streamlit Community Cloud secret API_BASE_URL to the resulting
   workers.dev URL.

The first container deployment can take several minutes to provision.

## Deploy the backend to Render

Create the backend as a normal Render Web Service. Do not use a Blueprint for this deployment.

The Render service is configured as:

- Runtime: Docker
- Dockerfile: ./backend/Dockerfile
- Docker context: ./backend
- Health check: /health
- Plan: free
- Environment: APP_ENV=production
- Database secret: DATABASE_URL

### Render deployment

1. Open the Render Dashboard.
2. Create a normal Web Service from this GitHub repository.
3. Select the main branch and Docker runtime.
4. Set the backend root directory / Docker context as documented above, then add DATABASE_URL.
5. Deploy the service.
6. Verify:

    https://YOUR-SERVICE.onrender.com/health

A successful response is:

    {"status":"ok","database":"connected"}

The service listens on Render's PORT environment variable when present, and falls back to port 8000 for local Docker runs.

Render free web services can spin down after inactivity, so the first request after idle time may take longer.

## Deploy the frontend to Streamlit Community Cloud

Use:

    frontend/app.py

Keep the frontend/requirements.txt file next to the Streamlit entrypoint.

In Streamlit Community Cloud:

1. Create a new app from this repository.
2. Choose branch main.
3. Set the entrypoint to frontend/app.py.
4. Select Python 3.12 in Advanced settings.
5. In Secrets, add:

    API_BASE_URL = "https://YOUR-SERVICE.onrender.com"

The frontend checks both the API_BASE_URL environment variable and Streamlit secrets, so the same code works locally and in Community Cloud.

The Streamlit app never receives the Neon password.

The Streamlit UI intentionally does not expose the Render service URL or database
connection details; those remain deployment configuration rather than product UI.

## Environment variables

Backend:

    APP_ENV=production
    DATABASE_URL=postgresql://...
    CORS_ORIGINS=*
    DB_POOL_SIZE=3
    DB_MAX_OVERFLOW=2

Frontend:

    API_BASE_URL=https://YOUR-SERVICE.onrender.com

.env.example contains the local development version.

## CI

GitHub Actions checks:

1. Python compilation
2. Pytest
3. Backend Docker build
4. Frontend Docker build

The Docker build contexts in CI match the contexts used by the deployment configuration.

## Statistical methodology

The experiment report includes:

- **Absolute and relative uplift** between treatment and control.
- **95% confidence interval** for the difference in conversion proportions using a normal approximation.
- **Two-sided two-proportion z-test** with H0: treatment conversion = control conversion and H1: treatment conversion != control conversion.
- **p-value and alpha=0.05 decision** for the simulated conversion-rate difference.
- **Approximate 80% power MDE** showing the smallest positive conversion-rate uplift expected to be detectable with the current arm sizes under a normal approximation.

The p-value and confidence interval describe randomization/sampling variability **within the synthetic run**. They do not capture uncertainty from simulator assumptions.

The MDE is a design-sensitivity measure, not a guarantee that a real experiment will detect an effect of that size.

A positive or statistically significant synthetic uplift is a reason to consider a controlled real-world pilot, not evidence that the real experiment will achieve the same effect.

## Current deployment boundary

The deployed system has a deliberately simple boundary:

    Streamlit
       |
       | HTTPS + JSON
       v
    FastAPI
       |
       | SQL over TLS
       v
    Neon PostgreSQL

Population generation is intentionally separated from graph construction: the
30,000-customer population is persisted first, and the observable similarity
network is built on demand when the map network layer is activated. This keeps
the initial generation path fast and reduces peak memory usage on the small
Render instance.

Only the FastAPI service holds the database connection string.

This keeps the Streamlit layer stateless and prevents database credentials from reaching the browser or Streamlit users.
