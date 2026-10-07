# Cloudflare backend

This project deploys only the FastAPI backend as a Cloudflare Container.

The Streamlit frontend remains separate and continues to call the backend through
API_BASE_URL.

## Why Containers

The FastAPI service generates large synthetic populations and uses NumPy,
SQLAlchemy and PostgreSQL. A normal Cloudflare Worker has a 128 MiB memory
limit, so the existing backend should not be moved unchanged into a Python
Worker. Cloudflare Containers provide configurable memory up to 12 GiB per
instance; this deployment uses the standard-1 instance type with 4 GiB.

## Cloudflare configuration

The root wrangler.toml:

- builds backend/Dockerfile
- runs one ApiContainer instance
- listens on container port 8000
- passes DATABASE_URL from a Cloudflare Worker Secret into the container
- keeps the PostgreSQL pool intentionally small

## Required Cloudflare secret

Create this Worker secret before the first deployment:

DATABASE_URL

Use the same Neon PostgreSQL connection string currently used by the backend.

Optional Worker variable:

CORS_ORIGINS=*

## Deployment

Cloudflare Containers are available on Workers Paid. Connect this GitHub
repository under Workers & Pages -> Workers Builds, use the repository root as
the build root, and deploy with:

npx wrangler deploy

After the first deployment, wait for the container to provision and then test:

https://YOUR-WORKER.YOUR-SUBDOMAIN.workers.dev/health

Expected response:

{"status":"ok","database":"connected"}

Then set the Streamlit Cloud secret:

API_BASE_URL = "https://YOUR-WORKER.YOUR-SUBDOMAIN.workers.dev"

No frontend code change is required.
