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
    schema.sql
    render.yaml
    docker-compose.yml

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

## Deploy the backend to Render

The repository includes render.yaml so the backend can be created as a Render Blueprint.

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
2. Create a new Blueprint from this GitHub repository, or create a Web Service manually.
3. If using the Blueprint, Render will ask for the DATABASE_URL secret because it is marked sync: false.
4. Deploy the service.
5. Verify:

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

## Statistical warning

The 95% confidence interval describes randomization/sampling variability in the synthetic run. It does not capture uncertainty from simulator assumptions.

A positive simulated uplift is a reason to consider a real-world pilot, not evidence that the real experiment will achieve the same effect.

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

Only the FastAPI service holds the database connection string.

This keeps the Streamlit layer stateless and prevents database credentials from reaching the browser or Streamlit users.
