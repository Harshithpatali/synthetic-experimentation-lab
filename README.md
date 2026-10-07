# Synthetic Experimentation Lab

**Test the experiment before testing it on real customers.**

A Python data-science platform that creates a synthetic customer population, randomizes customers into control/treatment, simulates heterogeneous outcomes, and lets a company inspect uplift, uncertainty, segments, and observable similarity structure before running a real-world pilot.

## Final architecture

    Streamlit Cloud
          |
          | HTTPS
          v
    Cloudflare Container
          |
          v
    FastAPI + Python
          |
          v
    Neon PostgreSQL

- Frontend: Streamlit
- Backend: FastAPI + Python
- Database: Neon PostgreSQL
- Backend packaging: Docker
- Production backend: Cloudflare Containers
- Production frontend: Streamlit Community Cloud
- No React
- No R2
- No D1

## Repository

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

    src/
      index.js              # Cloudflare routing only

    schema.sql
    docker-compose.yml
    wrangler.toml
    package.json
    tests/

The actual application backend is Python/FastAPI. The small JavaScript file only connects Cloudflare's container runtime to the FastAPI container.

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

Hidden variables create heterogeneous behavior but are never returned by the company-facing population API.

## Graph semantics

The graph represents measurable evidence of similarity.

An edge does not prove two customers are truly similar.

No edge does not mean no similarity.

It means similarity was not sufficiently observable/measurable under the selected graph construction.

The simulator-truth network is an internal diagnostic that uses hidden behavioral structure.

## Local development

Create a .env file from .env.example and put your Neon connection string in DATABASE_URL.

    docker compose up --build

Open:

    http://localhost:8501

FastAPI:

    http://localhost:8000/docs

Run tests:

    pip install -r backend/requirements.txt pytest
    pytest -q

## Neon

Neon is the only persistent application database.

Run schema.sql once against your Neon PostgreSQL database.

Then use:

    DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DBNAME?sslmode=require

Do not commit this value.

## Manual Cloudflare deployment

The production backend is the Dockerized FastAPI application.

Prerequisites:
1. Cloudflare account with Containers enabled.
2. Docker installed and running.
3. Node.js and npm installed.
4. Neon PostgreSQL connection string.

Install the Cloudflare deployment tooling:

    npm install
    npx wrangler login

Store the Neon connection string as a Cloudflare Worker secret:

    npx wrangler secret put DATABASE_URL

Deploy manually:

    npx wrangler deploy

Cloudflare builds backend/Dockerfile, starts FastAPI on port 8000, and passes the DATABASE_URL Worker secret into the container.

After deployment, verify:

    https://YOUR-WORKER.workers.dev/health

FastAPI docs:

    https://YOUR-WORKER.workers.dev/docs

Cloudflare's current Containers documentation recommends the Durable Object Container API for new applications and supports passing environment variables into the container at startup. The repository uses that pattern for the Neon connection string.

## Streamlit Cloud deployment

Deploy the frontend application from:

    frontend/app.py

Set this Streamlit environment variable:

    API_BASE_URL=https://YOUR-WORKER.workers.dev

Streamlit only talks to FastAPI over HTTPS.

Streamlit does not receive the Neon password.

## Secrets

Cloudflare:

    DATABASE_URL

Streamlit Cloud:

    API_BASE_URL

GitHub Actions does not need Cloudflare credentials because this project is intended to be deployed manually to Cloudflare.

If you later automate deployment, add:
- CLOUDFLARE_API_TOKEN
- CLOUDFLARE_ACCOUNT_ID

## Statistical warning

The 95% confidence interval describes randomization/sampling variability in the synthetic run. It does not capture uncertainty from simulator assumptions.

A positive simulated uplift is a reason to consider a real-world pilot, not evidence that the real experiment will achieve the same effect.
