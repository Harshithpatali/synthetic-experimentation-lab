# Synthetic Experimentation Lab

Cloudflare Worker + D1 synthetic customer experimentation and graph intelligence lab.

Features: synthetic populations, randomized experiments, customer similarity graphs, observable vs ground-truth views, community detection, PageRank, influence scores, and graph-aware synthetic uplift analysis.

## Deployment

1. `npm install`
2. `npx wrangler d1 execute synthetic-experimentation-lab --file=./schema.sql --remote`
3. `npx wrangler deploy`

The app uses Cloudflare Workers + D1 and Leaflet/OpenStreetMap for the customer map.
