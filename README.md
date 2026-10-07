# Synthetic Experimentation Lab

**A virtual customer population laboratory for testing experiment designs before exposing real customers.**

Live architecture: **Cloudflare Worker + D1 + GitHub Actions**.

## What this project is

A company can bring an experiment idea to the lab:

> "What might happen if we show this customer population a different offer, interface, recommendation, advertisement, or product experience?"

The lab creates a realistic synthetic population, randomly assigns control and treatment, simulates customer responses, and reports the simulated result.

The goal is **not** to predict individual customers or replace a real A/B test.

The goal is:

> **Test the experiment before testing it on real customers.**

## Product model

```
Business question
      ↓
Synthetic population
      ↓
Observable customer information
      +
Simulator-only hidden behaviour
      ↓
Experiment design
      ↓
Random control / treatment assignment
      ↓
Simulated customer responses
      ↓
Uplift + uncertainty + segment analysis
      ↓
Decision: refine, reject, or take to a real-world pilot
```

## Why hidden variables exist

A real company never observes every factor that affects a customer's response.

The simulator therefore keeps some variables private, such as:

- income
- profession
- price sensitivity
- product affinity
- novelty preference
- risk preference

These variables are used **inside the simulator** to create heterogeneous and correlated behaviour.

They are not exposed through the company-facing population API.

This lets the lab test an important question:

> Can an experiment look convincing using observable information while hidden customer behaviour creates uncertainty underneath?

## The graph is partial knowledge, not ground truth

The customer graph represents **measurable similarity**.

An edge means:

> "We found enough observable evidence to represent a relationship between these two synthetic customers."

For example, customers may share:

- city
- device
- gender
- age band
- customer type

The absence of an edge does **not** mean the customers are dissimilar.

It means the current observable information did not provide enough measurable evidence to create an edge.

```
No edge ≠ no similarity

No edge = similarity not sufficiently observable/measurable
```

The simulator can still contain hidden similarities between customers that have no observable edge.

The optional **Simulator Truth** view is an internal diagnostic view showing how hidden simulator information changes the measurable structure. It is not presented as customer knowledge.

## What a company can test

Examples:

- UI/UX changes
- discounts
- advertising treatments
- product launches
- recommendations
- shipping experiences

The company chooses the experiment scenario and target category. The simulator supplies heterogeneous responses based on the synthetic population.

## Experiment outputs

The lab reports:

- control and treatment sample sizes
- conversion rates
- absolute uplift
- relative uplift
- approximate 95% confidence interval
- simulated revenue difference
- segment-level results
- observable similarity/network structure

These are **simulated results**. They are not evidence that a treatment will work in the real world.

## Graph analytics

The graph is useful because customers can have correlated observable characteristics.

The lab currently provides:

- measurable similarity edges
- degree
- weighted degree
- PageRank-style centrality
- community detection
- influence score
- observable vs simulator-truth comparison
- graph-aware simulated response analysis

The graph should be interpreted as a partial measurement of population structure, not as a complete map of behavioural similarity.

## Privacy boundary

Company-facing data contains observable fields:

- age
- gender
- state/city
- location
- device
- customer type
- orders
- AOV
- recency
- sessions
- cart abandonment

Hidden simulator variables are kept in memory during population generation and are not written into the customer table.

## Cloudflare architecture

```
Browser
  ↓
Cloudflare Worker
  ├── Population API
  ├── Experiment API
  ├── Network API
  └── Analysis API
       ↓
     D1
  ├── customers
  ├── customer_edges
  ├── graph_metrics
  ├── experiments
  ├── segment_results
  └── population_runs
```

GitHub Actions deploys the Worker and applies the D1 schema.

## Local development

```bash
npm install
npm run dev
```

Initialize/update the remote D1 schema:

```bash
npm run db:init
```

Deploy:

```bash
npm run deploy
```

## Environment

GitHub Actions expects:

- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

## Important interpretation

This is a **synthetic experimentation environment**.

A simulated uplift answers:

> "Under the simulator's assumptions, what happened when this experiment was applied to this synthetic population?"

It does **not** answer:

> "What will definitely happen to real customers?"

That distinction is fundamental to the product.