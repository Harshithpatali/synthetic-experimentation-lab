CREATE TABLE IF NOT EXISTS experiments (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 created_at TEXT NOT NULL,
 experiment_type TEXT NOT NULL,
 category TEXT NOT NULL,
 sample_size INTEGER NOT NULL,
 treatment_size INTEGER NOT NULL,
 control_size INTEGER NOT NULL,
 conversions_treatment INTEGER NOT NULL,
 conversions_control INTEGER NOT NULL,
 revenue_treatment REAL NOT NULL,
 revenue_control REAL NOT NULL,
 aov_treatment REAL NOT NULL,
 aov_control REAL NOT NULL,
 conversion_rate_treatment REAL NOT NULL,
 conversion_rate_control REAL NOT NULL,
 absolute_uplift REAL NOT NULL,
 relative_uplift REAL NOT NULL,
 ci_low REAL NOT NULL,
 ci_high REAL NOT NULL,
 revenue_uplift REAL NOT NULL,
 treatment_share REAL NOT NULL DEFAULT 0.5
);
CREATE TABLE IF NOT EXISTS segment_results (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 experiment_id INTEGER NOT NULL,
 segment TEXT NOT NULL,
 segment_value TEXT NOT NULL,
 control_n INTEGER NOT NULL,
 treatment_n INTEGER NOT NULL,
 control_rate REAL NOT NULL,
 treatment_rate REAL NOT NULL,
 uplift REAL NOT NULL,
 FOREIGN KEY(experiment_id) REFERENCES experiments(id)
);
CREATE TABLE IF NOT EXISTS customers (
 customer_id TEXT PRIMARY KEY,
 age INTEGER NOT NULL,
 gender TEXT NOT NULL,
 state TEXT NOT NULL,
 city TEXT NOT NULL,
 lat REAL NOT NULL,
 lon REAL NOT NULL,
 device TEXT NOT NULL,
 customer_type TEXT NOT NULL,
 orders INTEGER NOT NULL,
 aov REAL NOT NULL,
 recency_days INTEGER NOT NULL,
 sessions_30d INTEGER NOT NULL,
 cart_abandonments INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS customer_edges (
 customer_id TEXT NOT NULL,
 neighbor_id TEXT NOT NULL,
 weight REAL NOT NULL,
 reasons TEXT NOT NULL,
 PRIMARY KEY(customer_id,neighbor_id)
);
CREATE INDEX IF NOT EXISTS idx_edges_customer ON customer_edges(customer_id);
CREATE INDEX IF NOT EXISTS idx_edges_neighbor ON customer_edges(neighbor_id);
CREATE TABLE IF NOT EXISTS graph_metrics (
 customer_id TEXT PRIMARY KEY,
 degree INTEGER NOT NULL DEFAULT 0,
 weighted_degree REAL NOT NULL DEFAULT 0,
 pagerank REAL NOT NULL DEFAULT 0,
 community_id INTEGER NOT NULL DEFAULT 0,
 influence_score REAL NOT NULL DEFAULT 0,
 updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_graph_metrics_community ON graph_metrics(community_id);
CREATE INDEX IF NOT EXISTS idx_graph_metrics_pagerank ON graph_metrics(pagerank);

-- Product metadata is deliberately separate from customer data.
-- It records the simulator configuration without storing hidden customer attributes.
CREATE TABLE IF NOT EXISTS population_runs (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 created_at TEXT NOT NULL,
 population_size INTEGER NOT NULL,
 observable_features TEXT NOT NULL,
 hidden_features TEXT NOT NULL,
 graph_definition TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_population_runs_created_at ON population_runs(created_at);