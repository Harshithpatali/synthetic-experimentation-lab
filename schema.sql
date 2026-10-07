CREATE TABLE IF NOT EXISTS population_runs (
  id VARCHAR(36) PRIMARY KEY,
  seed INTEGER NOT NULL,
  size INTEGER NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  config JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS customers (
  id VARCHAR(36) PRIMARY KEY,
  population_id VARCHAR(36) NOT NULL REFERENCES population_runs(id) ON DELETE CASCADE,
  age INTEGER NOT NULL,
  gender TEXT NOT NULL,
  city TEXT NOT NULL,
  state TEXT NOT NULL,
  lat DOUBLE PRECISION NOT NULL,
  lon DOUBLE PRECISION NOT NULL,
  device TEXT NOT NULL,
  customer_type TEXT NOT NULL,
  orders INTEGER NOT NULL,
  aov DOUBLE PRECISION NOT NULL,
  recency_days INTEGER NOT NULL,
  sessions_30d INTEGER NOT NULL,
  cart_abandonments INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS simulator_truth (
  id VARCHAR(36) PRIMARY KEY,
  population_id VARCHAR(36) NOT NULL REFERENCES population_runs(id) ON DELETE CASCADE,
  customer_id VARCHAR(36) NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
  profession TEXT NOT NULL,
  income DOUBLE PRECISION NOT NULL,
  price_sensitivity DOUBLE PRECISION NOT NULL,
  novelty_preference DOUBLE PRECISION NOT NULL,
  risk_preference DOUBLE PRECISION NOT NULL,
  beauty_affinity DOUBLE PRECISION NOT NULL,
  electronics_affinity DOUBLE PRECISION NOT NULL,
  grocery_affinity DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS customer_edges (
  id VARCHAR(36) PRIMARY KEY,
  population_id VARCHAR(36) NOT NULL REFERENCES population_runs(id) ON DELETE CASCADE,
  source_id VARCHAR(36) NOT NULL,
  target_id VARCHAR(36) NOT NULL,
  weight DOUBLE PRECISION NOT NULL,
  view TEXT NOT NULL CHECK (view IN ('observable','truth')),
  reasons JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS experiments (
  id VARCHAR(36) PRIMARY KEY,
  population_id VARCHAR(36) NOT NULL REFERENCES population_runs(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  treatment_share DOUBLE PRECISION NOT NULL,
  seed INTEGER NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  config JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS experiment_outcomes (
  id VARCHAR(36) PRIMARY KEY,
  experiment_id VARCHAR(36) NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
  customer_id VARCHAR(36) NOT NULL,
  arm TEXT NOT NULL CHECK (arm IN ('control','treatment')),
  converted BOOLEAN NOT NULL,
  revenue DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS segment_results (
  id VARCHAR(36) PRIMARY KEY,
  experiment_id VARCHAR(36) NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
  segment TEXT NOT NULL,
  control_rate DOUBLE PRECISION NOT NULL,
  treatment_rate DOUBLE PRECISION NOT NULL,
  uplift DOUBLE PRECISION NOT NULL,
  n INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_customers_population ON customers(population_id);
CREATE INDEX IF NOT EXISTS idx_truth_population ON simulator_truth(population_id);
CREATE INDEX IF NOT EXISTS idx_edges_population_view ON customer_edges(population_id, view);
CREATE INDEX IF NOT EXISTS idx_outcomes_experiment ON experiment_outcomes(experiment_id);
CREATE INDEX IF NOT EXISTS idx_segments_experiment ON segment_results(experiment_id);
