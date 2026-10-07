import json
import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

# -----------------------------------------------------------------------------
# Page configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Synthetic Experimentation Lab",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAGE_NAMES = [
    "Generate Population",
    "India Population Map",
    "Company Experiment",
    "Treatment vs Control",
    "Experiment Report",
]

CUSTOMER_COLORS = {
    "New": "#6366f1",
    "Repeat": "#8b5cf6",
    "Loyal": "#f59e0b",
}

PALETTE = [
    "#6366f1", "#06b6d4", "#f59e0b", "#ec4899",
    "#10b981", "#8b5cf6", "#ef4444", "#0ea5e9",
]

EXPERIMENT_TYPES = [
    "Marketing campaign",
    "Product promotion",
    "New UI / feature",
    "Checkout redesign",
    "Pricing / discount",
    "Recommendation / personalization",
    "Messaging / copy",
    "Retention / loyalty",
    "Search / discovery",
    "Other",
]

EXPERIMENT_TYPE_HELP = {
    "Marketing campaign": "Test a campaign, promotion, audience strategy, or channel message.",
    "Product promotion": "Test how promoting a product, collection, bundle, or launch changes behaviour.",
    "New UI / feature": "Test a new interface, feature, navigation, layout, or interaction.",
    "Checkout redesign": "Test a redesigned cart or checkout flow to reduce abandonment.",
    "Pricing / discount": "Test price, discount, bundle, or incentive changes.",
    "Recommendation / personalization": "Test personalized products, recommendations, or ranking.",
    "Messaging / copy": "Test headlines, copy, notifications, email, or in-app messaging.",
    "Retention / loyalty": "Test loyalty benefits, win-back journeys, or retention interventions.",
    "Search / discovery": "Test search, filters, sorting, discovery, or browse experiences.",
    "Other": "Describe any other business change you want to simulate.",
}

PRODUCT_CATEGORIES = [
    "General",
    "Beauty",
    "Electronics",
    "Grocery",
    "Fashion",
    "Home",
    "Sports",
    "Travel",
    "Finance",
    "SaaS",
]

SUCCESS_METRICS = [
    "Conversion rate",
    "Revenue per customer",
    "Average order value",
    "Checkout completion",
    "Click-through rate",
    "Add-to-cart rate",
    "Retention rate",
]

# -----------------------------------------------------------------------------
# Styling
# -----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root{
  --ink:#0b1220;
  --muted:#64748b;
  --line:rgba(15,23,42,.09);
  --brand:#6366f1;
  --brand-2:#8b5cf6;
  --cyan:#06b6d4;
  --shadow: 0 1px 2px rgba(16,24,40,.05), 0 14px 34px -16px rgba(16,24,40,.28);
}

html, body, [class*="css"], .stApp, button, input, textarea, select{
  font-family:'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.stApp{
  background:
    radial-gradient(1100px 520px at 8% -10%, #eef2ff 0%, rgba(238,242,255,0) 60%),
    radial-gradient(900px 460px at 100% 0%, #ecfeff 0%, rgba(236,254,255,0) 55%),
    #f6f7fb;
}

header[data-testid="stHeader"]{background:transparent;}
#MainMenu{visibility:hidden;}
footer{visibility:hidden;}

.block-container{padding-top:1.1rem; padding-bottom:3rem; max-width:1550px;}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#ffffff 0%, #f8fafc 100%);
  border-right:1px solid var(--line);
}
section[data-testid="stSidebar"] .block-container{padding-top:1.4rem;}

.brand{
  display:flex; align-items:center; gap:10px;
  font-weight:800; font-size:1.12rem; color:var(--ink);
  letter-spacing:-.02em; margin-bottom:.2rem;
}
.brand span{
  background:linear-gradient(120deg,#6366f1,#8b5cf6 60%,#06b6d4);
  -webkit-background-clip:text; background-clip:text; color:transparent;
}
.side-label{
  font-size:.7rem; font-weight:800; letter-spacing:.14em;
  text-transform:uppercase; color:#94a3b8; margin:.9rem 0 .35rem;
}

/* ---------- Hero ---------- */
.hero{
  position:relative; overflow:hidden;
  padding:28px 30px; border-radius:24px;
  background:linear-gradient(120deg,#eef2ff 0%, #f5f3ff 45%, #ecfeff 100%);
  border:1px solid rgba(99,102,241,.15);
  box-shadow:var(--shadow);
  margin-bottom:1.35rem;
}
.hero:after{
  content:""; position:absolute; right:-90px; top:-110px;
  width:320px; height:320px; border-radius:50%;
  background:radial-gradient(circle, rgba(99,102,241,.28), rgba(99,102,241,0) 68%);
}
.hero h1{
  margin:.5rem 0 .45rem; font-size:2.05rem; line-height:1.14;
  font-weight:800; color:#0b1220; letter-spacing:-.03em; max-width:26ch;
}
.hero p{margin:0; color:#475569; font-size:1rem; max-width:78ch; line-height:1.55;}
.pill{
  display:inline-flex; align-items:center; gap:7px; padding:6px 13px;
  border-radius:999px; background:rgba(255,255,255,.8);
  border:1px solid rgba(99,102,241,.2); font-size:.72rem; font-weight:800;
  color:#4f46e5; text-transform:uppercase; letter-spacing:.1em;
}
.chips{display:flex; flex-wrap:wrap; gap:8px; margin-top:14px;}
.chip{
  padding:7px 13px; border-radius:999px; background:rgba(255,255,255,.72);
  border:1px solid rgba(15,23,42,.07); font-size:.79rem; font-weight:600; color:#334155;
}

/* ---------- KPI cards ---------- */
.kpi{
  position:relative; overflow:hidden; height:100%;
  background:#fff; border:1px solid var(--line); border-radius:18px;
  padding:16px 18px 15px; box-shadow:var(--shadow);
}
.kpi:before{
  content:""; position:absolute; left:0; top:0; bottom:0; width:4px;
  background:linear-gradient(180deg,#6366f1,#06b6d4);
}
.kpi .label{
  font-size:.7rem; font-weight:800; letter-spacing:.11em;
  text-transform:uppercase; color:#94a3b8;
}
.kpi .value{
  font-size:1.68rem; font-weight:800; color:#0b1220;
  margin-top:7px; letter-spacing:-.03em; line-height:1.1;
}
.kpi .sub{font-size:.8rem; color:#64748b; margin-top:5px; font-weight:500;}

/* ---------- Panels ---------- */
.panel{
  background:#fff; border:1px solid var(--line); border-radius:20px;
  padding:18px 20px; box-shadow:var(--shadow); height:100%;
}
.panel h4{margin:0 0 4px; font-size:1rem; font-weight:800; color:#0b1220; letter-spacing:-.02em;}
.panel .desc{color:#64748b; font-size:.85rem; margin-bottom:10px;}
.section-title{
  font-size:1.12rem; font-weight:800; color:#0b1220; letter-spacing:-.02em;
  margin:1.4rem 0 .2rem;
}
.section-sub{color:#64748b; font-size:.87rem; margin-bottom:.7rem;}

/* ---------- Badges ---------- */
.badge{
  display:inline-flex; align-items:center; gap:8px;
  padding:8px 12px; border-radius:12px; font-size:.8rem; font-weight:700;
  border:1px solid var(--line); width:100%; justify-content:flex-start;
}
.badge.ok{background:#ecfdf5; color:#047857; border-color:#a7f3d0;}
.badge.bad{background:#fef2f2; color:#b91c1c; border-color:#fecaca;}
.dot{width:8px; height:8px; border-radius:50%; background:currentColor;}

/* ---------- Widgets ---------- */
.stButton > button, .stDownloadButton > button{
  border-radius:13px; border:1px solid var(--line); background:#fff;
  color:var(--ink); font-weight:700; padding:.6rem 1.05rem;
  transition:all .18s ease; box-shadow:0 1px 2px rgba(16,24,40,.05);
}
.stButton > button:hover, .stDownloadButton > button:hover{
  transform:translateY(-1px); border-color:rgba(99,102,241,.5); color:#4f46e5;
}
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"]{
  background:linear-gradient(135deg,#6366f1,#8b5cf6 58%,#06b6d4 145%);
  border:none; color:#fff;
  box-shadow:0 14px 30px -14px rgba(99,102,241,.9);
}
.stButton > button[kind="primary"]:hover{color:#fff; opacity:.95;}

.stTextInput input, .stNumberInput input, .stTextArea textarea{
  border-radius:12px !important;
}
div[data-baseweb="select"] > div{border-radius:12px !important;}

.stTabs [data-baseweb="tab-list"]{
  gap:6px; background:rgba(255,255,255,.75); padding:6px;
  border-radius:14px; border:1px solid var(--line);
}
.stTabs [data-baseweb="tab"]{
  border-radius:10px; padding:8px 16px; font-weight:700; font-size:.86rem;
}
.stTabs [aria-selected="true"]{
  background:linear-gradient(135deg,#eef2ff,#f5f3ff); color:#4f46e5;
}

[data-testid="stDataFrame"]{border-radius:14px; overflow:hidden; border:1px solid var(--line);}
div[data-testid="stExpander"]{
  border:1px solid var(--line); border-radius:14px; background:#fff;
}
.footer{
  margin-top:2.4rem; padding-top:1rem; border-top:1px solid var(--line);
  color:#94a3b8; font-size:.8rem; text-align:center;
}
/* ---------- Cyber intelligence map ---------- */
.tech-map-shell{
  position:relative;
  overflow:hidden;
  border:1px solid rgba(34,211,238,.22);
  border-radius:20px;
  background:
    radial-gradient(circle at 20% 20%, rgba(34,211,238,.07), transparent 34%),
    radial-gradient(circle at 82% 28%, rgba(168,85,247,.08), transparent 30%),
    linear-gradient(180deg,#020617 0%,#030712 100%);
  box-shadow:
    0 0 0 1px rgba(34,211,238,.05),
    0 0 42px rgba(34,211,238,.08),
    inset 0 0 60px rgba(15,23,42,.85);
}
.tech-map-grid{
  position:absolute; inset:0; pointer-events:none; opacity:.15;
  background-image:
    linear-gradient(rgba(34,211,238,.22) 1px, transparent 1px),
    linear-gradient(90deg, rgba(34,211,238,.22) 1px, transparent 1px);
  background-size:38px 38px;
  mask-image:linear-gradient(to bottom,rgba(0,0,0,.9),transparent 92%);
}
.tech-map-header{
  position:relative; z-index:2;
  display:flex; align-items:center; justify-content:space-between;
  gap:16px; padding:14px 17px;
  border-bottom:1px solid rgba(34,211,238,.14);
  background:linear-gradient(90deg,rgba(2,6,23,.96),rgba(15,23,42,.82));
}
.tech-map-title{
  font-size:.72rem; font-weight:900; letter-spacing:.18em;
  text-transform:uppercase; color:#67e8f9;
}
.tech-map-sub{
  margin-top:3px; color:#cbd5e1; font-size:.78rem; font-weight:600;
}
.tech-status{
  display:flex; align-items:center; gap:8px;
  padding:7px 11px; border:1px solid rgba(52,211,153,.22);
  border-radius:999px; background:rgba(6,78,59,.20);
  color:#6ee7b7; font-size:.68rem; font-weight:900;
  letter-spacing:.12em; text-transform:uppercase;
  white-space:nowrap;
}
.tech-status-dot{
  width:7px; height:7px; border-radius:50%;
  background:#34d399; box-shadow:0 0 12px rgba(52,211,153,.95);
}
.tech-map-footer{
  position:relative; z-index:2;
  display:flex; justify-content:space-between; gap:16px;
  padding:9px 13px;
  border-top:1px solid rgba(34,211,238,.12);
  color:#64748b; font-size:.68rem; letter-spacing:.06em;
  text-transform:uppercase;
  background:rgba(2,6,23,.92);
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# API helpers
# -----------------------------------------------------------------------------
def resolve_api_base_url() -> str:
    value = os.getenv("API_BASE_URL", "").strip()
    if value:
        return value.rstrip("/")

    try:
        value = str(st.secrets["API_BASE_URL"]).strip()
    except (KeyError, FileNotFoundError):
        value = ""

    return value.rstrip("/")


API = resolve_api_base_url()


def api_error(response: requests.Response) -> str:
    try:
        payload = response.json()
        detail = payload.get("detail")
        if detail:
            return str(detail)
    except ValueError:
        pass
    return f"Backend returned HTTP {response.status_code}."


@st.cache_resource
def get_http_session() -> requests.Session:
    """Reuse one HTTP connection pool across Streamlit reruns."""
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Synthetic-Experimentation-Lab/1.0",
            "Accept": "application/json",
        }
    )
    return session


def get(path: str, **params):
    if not API:
        raise RuntimeError(
            "API_BASE_URL is not configured. Add it to Streamlit Cloud Secrets."
        )
    response = get_http_session().get(
        API + path,
        params=params,
        timeout=180,
    )
    if not response.ok:
        raise RuntimeError(api_error(response))
    return response.json()


def post(path: str, payload: dict):
    if not API:
        raise RuntimeError(
            "API_BASE_URL is not configured. Add it to Streamlit Cloud Secrets."
        )
    response = get_http_session().post(
        API + path,
        json=payload,
        timeout=600,
    )
    if not response.ok:
        raise RuntimeError(api_error(response))
    return response.json()


@st.cache_data(ttl=30, max_entries=4, show_spinner=False)
def load_health():
    return get("/health")


@st.cache_data(ttl=1800, max_entries=8, show_spinner=False)
def load_population_map(population_id: str):
    return get(f"/population/{population_id}/map", limit=30000)


@st.cache_data(ttl=1800, max_entries=8, show_spinner=False)
def load_population_diagnostics(population_id: str):
    return get(f"/population/{population_id}/diagnostics")


@st.cache_data(ttl=1800, max_entries=8, show_spinner=False)
def load_reference_behavior(population_id: str):
    return get(f"/population/{population_id}/reference-behavior")


@st.cache_data(ttl=1800, max_entries=32, show_spinner=False)
def load_network(population_id: str, limit: int, features: tuple[str, ...]):
    return get(
        "/network",
        population_id=population_id,
        view="observable",
        limit=limit,
        features=",".join(features),
    )


# -----------------------------------------------------------------------------
# Small formatting helpers
# -----------------------------------------------------------------------------
def pct(value, decimals=2) -> str:
    try:
        return f"{float(value):.{decimals}%}"
    except (TypeError, ValueError):
        return "—"


def inr(value, decimals=0) -> str:
    try:
        return f"₹{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return "—"


def kpi_row(items: list[dict]):
    """Render a row of modern KPI cards."""
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        with col:
            st.markdown(
                f"""
                <div class="kpi">
                  <div class="label">{item.get('label', '')}</div>
                  <div class="value">{item.get('value', '—')}</div>
                  <div class="sub">{item.get('sub', '')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def section(title: str, subtitle: str = ""):
    st.markdown(
        f'<div class="section-title">{title}</div>'
        f'<div class="section-sub">{subtitle}</div>',
        unsafe_allow_html=True,
    )


PLOTLY_FONT = dict(
    family="Plus Jakarta Sans, -apple-system, Segoe UI, sans-serif",
    size=13,
    color="#0b1220",
)


def style_fig(fig: go.Figure, height: int = 420, showlegend: bool = True) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        font=PLOTLY_FONT,
        height=height,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=showlegend,
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="rgba(15,23,42,.1)",
            font=dict(family="Plus Jakarta Sans", size=12, color="#0b1220"),
        ),
    )
    fig.update_xaxes(gridcolor="rgba(15,23,42,.06)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(15,23,42,.06)", zeroline=False)
    return fig


def hover_series(df: pd.DataFrame) -> pd.Series:
    """Vectorised hover text builder — only uses columns that exist."""
    wanted = [
        "city", "state", "gender", "age", "income",
        "customer_type", "segment", "id",
    ]
    cols = [c for c in wanted if c in df.columns]
    text = pd.Series("", index=df.index, dtype="object")
    for col in cols:
        label = col.replace("_", " ").title()
        text = text + f"<b>{label}</b>: " + df[col].astype(str) + "<br>"
    return text.str.rstrip("<br>")


# -----------------------------------------------------------------------------
# Interactive India map
# -----------------------------------------------------------------------------
MAP_STYLES = {
    "Tech Dark": "carto-darkmatter",
    "Light (Carto Positron)": "carto-positron",
    "Streets (OpenStreetMap)": "open-street-map",
}

EDGE_FEATURES = [
    "gender",
    "device",
    "customer_type",
    "age",
    "orders",
    "aov",
    "recency",
    "sessions",
    "cart_abandonments",
]

EDGE_FEATURE_LABELS = {
    "gender": "Gender",
    "device": "Device",
    "customer_type": "Customer type",
    "age": "Age",
    "orders": "Orders",
    "aov": "AOV",
    "recency": "Recency",
    "sessions": "Sessions",
    "cart_abandonments": "Cart abandonment",
}

EDGE_FEATURE_COLORS = {
    "gender": "#ff4d67",
    "device": "#ffb020",
    "customer_type": "#2ee6a6",
    "age": "#38bdf8",
    "orders": "#a78bfa",
    "aov": "#f472b6",
    "recency": "#22d3ee",
    "sessions": "#84cc16",
    "cart_abandonments": "#fb923c",
}

TECH_MAP_STYLE = "carto-darkmatter"
TECH_MARKER_COLOR = "#5ee7ff"
TECH_MARKER_BORDER = "#c4f7ff"


def build_india_map(
    points: pd.DataFrame,
    edges: list[dict],
    *,
    map_style: str = TECH_MAP_STYLE,
    show_edges: bool = True,
    edge_opacity: float = 0.22,
    marker_size: int = 7,
    color_by: str = "customer_type",
    density: bool = False,
    height: int = 760,
) -> go.Figure:
    pts = points.copy()
    pts["lat"] = pd.to_numeric(pts["lat"], errors="coerce")
    pts["lon"] = pd.to_numeric(pts["lon"], errors="coerce")
    pts = pts.dropna(subset=["lat", "lon"])

    dark = "dark" in map_style
    fig = go.Figure()

    # --- Density layer -------------------------------------------------------
    if density:
        fig.add_trace(
            go.Densitymap(
                lat=pts["lat"],
                lon=pts["lon"],
                radius=14,
                colorscale=[
                    [0.0, "rgba(99,102,241,0)"],
                    [0.2, "rgba(99,102,241,.55)"],
                    [0.45, "rgba(139,92,246,.75)"],
                    [0.7, "rgba(6,182,212,.85)"],
                    [1.0, "rgba(245,158,11,.95)"],
                ],
                showscale=False,
                opacity=0.85,
                hoverinfo="skip",
                name="Density",
            )
        )

    # --- Feature-level similarity edges --------------------------------------
    if show_edges and edges:
        coords = pts.set_index("id")[["lat", "lon"]]
        grouped: dict[str, list[dict]] = {}

        for edge in edges:
            feature = edge.get("feature", "unknown")
            grouped.setdefault(feature, []).append(edge)

        for feature, feature_edges in grouped.items():
            edge_lat, edge_lon, edge_hover = [], [], []

            for edge in feature_edges:
                source = edge.get("source")
                target = edge.get("target")
                if source not in coords.index or target not in coords.index:
                    continue

                source_lat = coords.at[source, "lat"]
                source_lon = coords.at[source, "lon"]
                target_lat = coords.at[target, "lat"]
                target_lon = coords.at[target, "lon"]

                edge_lat.extend([source_lat, target_lat, None])
                edge_lon.extend([source_lon, target_lon, None])

                label = EDGE_FEATURE_LABELS.get(
                    feature,
                    edge.get("feature_label", "Similarity"),
                )
                weight = float(edge.get("weight", 0.0))
                reasons = edge.get("reasons") or []
                reason_text = "<br>".join(str(item) for item in reasons)

                edge_hover.extend(
                    [
                        (
                            f"<b>{label}</b><br>"
                            f"Similarity: {weight:.2f}<br>"
                            f"{reason_text}<extra></extra>"
                        ),
                        (
                            f"<b>{label}</b><br>"
                            f"Similarity: {weight:.2f}<br>"
                            f"{reason_text}<extra></extra>"
                        ),
                        None,
                    ]
                )

            if not edge_lat:
                continue

            rgba = EDGE_FEATURE_COLORS.get(feature, "#64748b")
            legend_name = EDGE_FEATURE_LABELS.get(
                feature,
                feature.replace("_", " ").title(),
            )

            # Two-layer rendering gives the network a subtle neon/glow effect
            # without changing the underlying data or increasing edge count.
            fig.add_trace(
                go.Scattermap(
                    lat=edge_lat,
                    lon=edge_lon,
                    mode="lines",
                    line=dict(width=5.0, color=rgba),
                    opacity=min(edge_opacity * 0.42, 0.24),
                    hoverinfo="skip",
                    name=f"{legend_name} glow",
                    showlegend=False,
                )
            )
            fig.add_trace(
                go.Scattermap(
                    lat=edge_lat,
                    lon=edge_lon,
                    mode="lines",
                    line=dict(width=1.15, color=rgba),
                    text=edge_hover,
                    hovertemplate="%{text}",
                    opacity=max(0.20, min(edge_opacity * 2.3, 0.95)),
                    name=legend_name,
                    showlegend=True,
                )
            )

    # --- Customer markers ----------------------------------------------------
    if not density:
        hover = hover_series(pts)

        if color_by == "customer_type" and "customer_type" in pts.columns:
            order = [c for c in ["New", "Repeat", "Loyal"] if c in set(pts["customer_type"])]
            order += [c for c in pts["customer_type"].unique() if c not in order]
            groups = [(name, pts[pts["customer_type"] == name]) for name in order]
            colors = {
                name: CUSTOMER_COLORS.get(name, PALETTE[i % len(PALETTE)])
                for i, name in enumerate(order)
            }
        elif color_by in pts.columns:
            values = pts[color_by].astype(str)
            order = sorted(values.unique().tolist())
            groups = [(name, pts[values == name]) for name in order]
            colors = {name: PALETTE[i % len(PALETTE)] for i, name in enumerate(order)}
        else:
            groups = [("Customers", pts)]
            colors = {"Customers": "#6366f1"}

        for name, subset in groups:
            if subset.empty:
                continue

            marker_color = colors.get(name, TECH_MARKER_COLOR)

            # Soft outer glow.
            fig.add_trace(
                go.Scattermap(
                    lat=subset["lat"],
                    lon=subset["lon"],
                    mode="markers",
                    marker=dict(
                        size=max(marker_size * 2.4, 10),
                        opacity=0.08,
                        color=marker_color,
                    ),
                    hoverinfo="skip",
                    name=f"{name} glow",
                    showlegend=False,
                )
            )

            # Bright intelligence-grid core.
            fig.add_trace(
                go.Scattermap(
                    lat=subset["lat"],
                    lon=subset["lon"],
                    mode="markers",
                    marker=dict(
                        size=marker_size,
                        opacity=0.92,
                        color=marker_color,
                    ),
                    text=hover.loc[subset.index],
                    hovertemplate="%{text}<extra></extra>",
                    name=str(name),
                )
            )

    # --- Layout --------------------------------------------------------------
    fig.update_layout(
        map=dict(
            style=map_style,
            center=dict(lat=22.6, lon=79.0),
            zoom=4.05,
        ),
        height=height,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        uirevision="keep-zoom",
        hoverlabel=dict(
            bgcolor="#020617" if dark else "white",
            bordercolor="rgba(34,211,238,.22)",
            font=dict(
                family="Plus Jakarta Sans",
                size=12,
                color="#e0f2fe" if dark else "#0b1220",
            ),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.01,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(15,23,42,.72)" if dark else "rgba(255,255,255,.86)",
            bordercolor="rgba(15,23,42,.08)",
            borderwidth=1,
            font=dict(color="#e2e8f0" if dark else "#0b1220", size=12),
        ),
    )
    return fig


PLOTLY_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False,
    "scrollZoom": True,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
    "toImageButtonOptions": {"format": "png", "scale": 2},
}


# -----------------------------------------------------------------------------
# Session helpers
# -----------------------------------------------------------------------------
def current_result():
    return st.session_state.get("experiment_result")


def current_meta():
    return st.session_state.get("experiment_meta", {})


# -----------------------------------------------------------------------------
# Hero
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
      <div class="pill">🧪 Synthetic Experimentation Lab</div>
      <h1>Test the experiment before testing it on real customers.</h1>
      <p>
        Generate a virtual Indian customer population, explore its observable
        similarity network on an interactive map, simulate a company experiment,
        and produce a decision-ready report.
      </p>
      <div class="chips">
        <div class="chip">🇮🇳 30,000 synthetic customers</div>
        <div class="chip">🕸️ Observable similarity graph</div>
        <div class="chip">🎲 Randomised treatment vs control</div>
        <div class="chip">📊 95% confidence intervals</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div class="brand">🧪 <span>Synthetic Lab</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="side-label">Workflow</div>', unsafe_allow_html=True)

    labels = [f"{i + 1}. {name}" for i, name in enumerate(PAGE_NAMES)]
    choice = st.radio("Workflow", labels, label_visibility="collapsed")
    page = PAGE_NAMES[labels.index(choice)]

    st.markdown('<div class="side-label">System</div>', unsafe_allow_html=True)
    if API:
        try:
            load_health()
            st.markdown(
                '<div class="badge ok"><span class="dot"></span>Simulation engine ready</div>',
                unsafe_allow_html=True,
            )
        except Exception:
            st.markdown(
                '<div class="badge bad"><span class="dot"></span>Simulation engine unavailable</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div class="badge bad"><span class="dot"></span>Simulation engine not configured</div>',
            unsafe_allow_html=True,
        )

    if st.session_state.get("population_id"):
        size = st.session_state.get("population_size", 0)
        st.caption(f"✓ {size:,} synthetic customers ready")

    st.divider()
    if st.button("↺ Start new simulation", use_container_width=True):
        for key in [
            "population_id",
            "population_size",
            "population_seed",
            "experiment_result",
            "experiment_meta",
            "population_diagnostics",
            "reference_behavior",
            "network_rebuilt_population",
        ]:
            st.session_state.pop(key, None)
        load_population_map.clear()
        load_population_diagnostics.clear()
        load_reference_behavior.clear()
        load_network.clear()
        load_health.clear()
        st.rerun()


# =============================================================================
# PAGE 1 — Generate population
# =============================================================================
if page == PAGE_NAMES[0]:
    section(
        "Generate the synthetic population",
        "Create the virtual Indian customer base that the company will experiment on.",
    )

    left, right = st.columns([1.35, 1], gap="large")

    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        population_size = st.slider(
            "Population size",
            min_value=5000,
            max_value=30000,
            value=30000,
            step=5000,
            help="30,000 is the recommended maximum for the interactive map.",
        )
        population_seed = st.number_input(
            "Population seed",
            min_value=0,
            max_value=999999,
            value=42,
            step=1,
            help="Same seed → identical synthetic population (reproducible runs).",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.write("")
        generate = st.button(
            "⚡ Generate synthetic customers",
            type="primary",
            use_container_width=True,
        )

    with right:
        st.markdown(
            """
            <div class="panel">
              <h4>What gets generated</h4>
              <div class="desc">
                A geographically grounded Indian customer base with hidden
                simulator behaviour. The observable similarity network is built
                on demand when you open the map.
              </div>
              <ul style="color:#475569;font-size:.88rem;line-height:1.75;margin:0;padding-left:1.1rem;">
                <li>Lat / lon jittered around major Indian city centres</li>
                <li>Correlated age, income, engagement, spending and digital behaviour</li>
                <li>Customer lifecycle: New, Repeat, Loyal</li>
                <li>Hidden response behaviour used only by the simulator</li>
                <li>Global cross-city similarity network available on demand</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if generate:
        try:
            with st.spinner("Generating customers and hidden simulator behaviour…"):
                result = post(
                    "/population/generate",
                    {"size": population_size, "seed": population_seed},
                )

            st.session_state["population_id"] = result["population_id"]
            st.session_state["population_size"] = result["size"]
            st.session_state["population_seed"] = result["seed"]
            st.session_state.pop("experiment_result", None)
            st.session_state.pop("experiment_meta", None)
            st.session_state.pop("population_diagnostics", None)

            load_population_map.clear()
            load_population_diagnostics.clear()
            load_reference_behavior.clear()
            load_network.clear()

            st.toast("Population generated successfully", icon="✅")
            st.success(f"Population created: {result['size']:,} customers")

        except Exception as exc:
            st.error(str(exc))

    if st.session_state.get("population_id"):
        st.write("")
        kpi_row(
            [
                {
                    "label": "Customers",
                    "value": f"{st.session_state.get('population_size', 0):,}",
                    "sub": "Synthetic Indian customers",
                },
                {
                    "label": "Seed",
                    "value": str(st.session_state.get("population_seed", "—")),
                    "sub": "Reproducible generation",
                },
                {
                    "label": "Network",
                    "value": "On demand",
                    "sub": "Built when map is opened",
                },
                {
                    "label": "Next step",
                    "value": "Map",
                    "sub": "Explore customer relationships",
                },
            ]
        )

    with st.expander("🧪 Validate population structure"):
        st.caption(
            "These checks verify that the synthetic generator preserves the "
            "relationships it was designed to model. They are not a substitute "
            "for calibration against real company data."
        )

        if st.button(
            "Run population diagnostics",
            key="run_population_diagnostics",
        ):
            try:
                with st.spinner("Checking population distributions and relationships…"):
                    diagnostics = load_population_diagnostics(
                        st.session_state["population_id"]
                    )
                st.session_state["population_diagnostics"] = diagnostics
            except Exception as exc:
                st.error(str(exc))

        diagnostics = st.session_state.get("population_diagnostics")
        if diagnostics:
            score = diagnostics.get("score", 0.0)
            label = diagnostics.get("label", "Generator consistency")
            tone = "✅" if score >= 80 else "⚠️" if score >= 60 else "❗"
            st.metric(
                f"{tone} {label}",
                f"{score:.1f}/100",
                help="Structural consistency score, not a real-world realism score.",
            )

            checks = diagnostics.get("checks", [])
            if checks:
                check_frame = pd.DataFrame(
                    [
                        {
                            "Check": item.get("name", "—"),
                            "Result": "PASS" if item.get("passed") else "REVIEW",
                            "Value": item.get("value", "—"),
                        }
                        for item in checks
                    ]
                )
                st.dataframe(
                    check_frame,
                    use_container_width=True,
                    hide_index=True,
                )

            summary = diagnostics.get("summary", {})
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Median age", summary.get("median_age", "—"))
            with m2:
                st.metric("Median AOV", inr(summary.get("median_aov", 0)))
            with m3:
                st.metric("Median orders", summary.get("median_orders", "—"))
            with m4:
                st.metric(
                    "Geography",
                    f"{summary.get('cities', 0)} cities",
                )

            st.caption(diagnostics.get("caveat", ""))


    st.markdown("### 📏 Compare with real customer behaviour")
    st.caption(
        "This is a separate benchmark from the generator-consistency score. "
        "It compares orders, AOV shape, recency and lifecycle composition with "
        "the bundled real UCI Online Retail II transaction sample."
    )

    if st.button(
        "Compare synthetic population with real transactions",
        key="run_reference_behavior",
    ):
        try:
            with st.spinner("Comparing the synthetic population with real transaction behaviour…"):
                benchmark = load_reference_behavior(
                    st.session_state["population_id"]
                )
            st.session_state["reference_behavior"] = benchmark
        except Exception as exc:
            st.error(str(exc))

    benchmark = st.session_state.get("reference_behavior")
    if benchmark:
        score = float(benchmark.get("score", 0.0))
        tone = "✅" if score >= 80 else "⚠️" if score >= 60 else "❗"
        kpi_row(
            [
                {
                    "label": "Behavior alignment",
                    "value": f"{score:.1f}/100",
                    "sub": benchmark.get("classification", "—"),
                },
                {
                    "label": "Real reference",
                    "value": f"{benchmark.get('reference_customers', 0):,}",
                    "sub": "Customer profiles from real transactions",
                },
                {
                    "label": "Synthetic",
                    "value": f"{benchmark.get('population_size', 0):,}",
                    "sub": "Customers being benchmarked",
                },
            ]
        )

        metric_rows = []
        for key, label in (
            ("orders", "Orders"),
            ("aov", "AOV shape"),
            ("recency", "Recency"),
        ):
            metric = benchmark.get("metrics", {}).get(key, {})
            metric_rows.append(
                {
                    "Metric": label,
                    "Alignment": f"{float(metric.get('score', 0.0)):.1f}/100",
                    "KS distance": metric.get("ks_distance", "—"),
                    "Real median": metric.get("real_median", "—"),
                    "Synthetic median": metric.get("synthetic_median", "—"),
                    "Comparison": metric.get("comparison", "—"),
                }
            )

        st.dataframe(
            pd.DataFrame(metric_rows),
            use_container_width=True,
            hide_index=True,
        )

        lifecycle = benchmark.get("lifecycle", {})
        lc1, lc2 = st.columns(2)
        with lc1:
            st.metric(
                "Lifecycle alignment",
                f"{float(lifecycle.get('score', 0.0)):.1f}/100",
            )
        with lc2:
            st.caption(
                "AOV is scored by relative distribution shape because the real "
                "reference is priced in GBP while the synthetic app uses INR."
            )

        source = benchmark.get("reference_source", {})
        st.caption(
            f"Reference: {source.get('name', 'Real dataset')} · "
            f"{source.get('license', 'licensed data')} · "
            f"{source.get('sample_rows', '—'):,} bundled real rows"
        )
        st.caption(benchmark.get("caveat", ""))

    with st.expander("ℹ️ How the simulation pipeline works"):
        st.markdown(
            """
            1. **Population** — customers are sampled across Indian cities with
               geographic jitter, demographics and a hidden behavioural profile.
            2. **Observable network** — measurable similarity between customers is
               exposed as a graph. An edge is *observable similarity*, **not** a
               causal relationship.
            3. **Experiment** — customers are randomised into treatment and control.
               The hidden simulator produces responses.
            4. **Report** — uplift, confidence intervals and segment findings are
               summarised into a decision-ready recommendation.
            """
        )


# =============================================================================
# PAGE 2 — Interactive India map
# =============================================================================
elif page == PAGE_NAMES[1]:
    population_id = st.session_state.get("population_id")
    if not population_id:
        st.warning("Generate a population on Page 1 first.")
        st.stop()

    section(
        "Interactive India population map",
        "Pan, zoom, filter and inspect every synthetic customer. "
        "The map loads first; the similarity network can be built on demand.",
    )

    try:
        with st.spinner("Loading the Indian population map…"):
            map_payload = load_population_map(population_id)

        points = pd.DataFrame(map_payload["rows"])

        kpi_row(
            [
                {"label": "Customers mapped", "value": f"{len(points):,}", "sub": "Points on the map"},
                {"label": "Indian cities", "value": f"{points['city'].nunique():,}", "sub": "Unique city centres"},
                {"label": "States / UTs", "value": f"{points['state'].nunique():,}", "sub": "Geographic spread"},
                {
                    "label": "Network",
                    "value": "Global",
                    "sub": "Cross-city feature similarity",
                },
            ]
        )

        st.write("")
        with st.expander("🎛️ Map controls", expanded=True):
            c1, c2, c3, c4 = st.columns(4)

            with c1:
                map_style_label = st.selectbox(
                    "Base map style",
                    list(MAP_STYLES.keys()),
                    index=0,
                )
                density_mode = st.toggle("Density heat layer", value=False)

            with c2:
                color_by = st.selectbox(
                    "Colour points by",
                    [c for c in ["customer_type", "gender", "state", "city"] if c in points.columns],
                    index=0,
                )
                marker_size = st.slider("Marker size", 3, 16, 7, 1)

            with c3:
                edge_limit = st.slider(
                    "Similarity edges to load",
                    min_value=900,
                    max_value=18000,
                    value=9000,
                    step=900,
                    help="The budget is shared roughly equally across selected features.",
                )
                show_edges = st.toggle(
                    "Show similarity network",
                    value=True,
                    help="Display the observable cross-city intelligence network.",
                )

            with c4:
                edge_opacity = st.slider(
                    "Edge opacity", 0.05, 0.60, 0.24, 0.01
                )
                map_height = st.slider("Map height (px)", 520, 980, 760, 20)

            edge_feature_labels = st.multiselect(
                "Edge features",
                options=EDGE_FEATURES,
                default=EDGE_FEATURES,
                format_func=lambda value: EDGE_FEATURE_LABELS[value],
                help="Each observable feature is rendered as a different edge colour. "
                "Customers can connect across cities when the selected feature supports similarity.",
            )

        # ---- Filters --------------------------------------------------------
        f1, f2, f3 = st.columns([1.6, 1, 1])

        with f1:
            city_options = ["All India"] + sorted(points["city"].unique().tolist())
            city_filter = st.selectbox("City filter", city_options)

        with f2:
            type_options = (
                sorted(points["customer_type"].unique().tolist())
                if "customer_type" in points.columns
                else []
            )
            type_filter = st.multiselect(
                "Customer type", type_options, default=type_options
            )

        with f3:
            gender_options = (
                sorted(points["gender"].unique().tolist())
                if "gender" in points.columns
                else []
            )
            gender_filter = st.multiselect(
                "Gender", gender_options, default=gender_options
            )

        # ---- Apply filters --------------------------------------------------
        visible_points = points.copy()

        if city_filter != "All India":
            visible_points = visible_points[visible_points["city"] == city_filter]

        if type_filter and "customer_type" in visible_points.columns:
            visible_points = visible_points[
                visible_points["customer_type"].isin(type_filter)
            ]

        if gender_filter and "gender" in visible_points.columns:
            visible_points = visible_points[
                visible_points["gender"].isin(gender_filter)
            ]

        selected_edge_features = tuple(edge_feature_labels)

        if show_edges and selected_edge_features:
            with st.spinner("Loading global feature-level similarity edges…"):
                network_payload = load_network(
                    population_id,
                    edge_limit,
                    selected_edge_features,
                )
        else:
            network_payload = {"edges": []}

        if (
            show_edges
            and selected_edge_features
            and not network_payload.get("edges")
            and st.session_state.get("network_rebuilt_population") != population_id
        ):
            # New populations intentionally skip graph construction during
            # generation. Build the graph automatically the first time the
            # user opens the network layer, then reload the edges.
            with st.spinner("Activating customer intelligence network…"):
                rebuild = post(
                    f"/population/{population_id}/network/rebuild",
                    {},
                )
            st.session_state["network_rebuilt_population"] = population_id
            load_network.clear()
            st.rerun()

        if (
            show_edges
            and selected_edge_features
            and not network_payload.get("edges")
            and st.session_state.get("network_rebuilt_population") == population_id
        ):
            st.info(
                "No observable similarity edges are available for the current "
                "feature selection."
            )

        visible_ids = set(visible_points["id"])
        visible_edges = [
            edge
            for edge in network_payload["edges"]
            if edge["source"] in visible_ids and edge["target"] in visible_ids
        ]

        st.markdown(
            """
            <div class="tech-map-shell">
              <div class="tech-map-grid"></div>
              <div class="tech-map-header">
                <div>
                  <div class="tech-map-title">◉ CUSTOMER INTELLIGENCE GRID // INDIA</div>
                  <div class="tech-map-sub">Synthetic entities · cross-city observable similarity · live analysis layer</div>
                </div>
                <div class="tech-status">
                  <span class="tech-status-dot"></span>
                  LIVE SIGNAL
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tabs = st.tabs(["🛰️ Network map", "📊 Distributions", "🧾 Data explorer"])

        # ---- Map tab --------------------------------------------------------
        with tabs[0]:
            kpi_row(
                [
                    {"label": "Visible customers", "value": f"{len(visible_points):,}", "sub": "After filters"},
                    {"label": "Edges drawn", "value": f"{len(visible_edges):,}", "sub": "Strongest observable similarities"},
                    {"label": "Cities shown", "value": f"{visible_points['city'].nunique():,}" if not visible_points.empty else "0", "sub": "In current selection"},
                    {"label": "Layer", "value": "Density" if density_mode else "Points", "sub": "Map rendering mode"},
                ]
            )

            st.write("")

            if visible_points.empty:
                st.info("No customers match the current filters.")
            else:
                fig = build_india_map(
                    visible_points,
                    visible_edges,
                    map_style=MAP_STYLES[map_style_label],
                    show_edges=show_edges,
                    edge_opacity=edge_opacity,
                    marker_size=marker_size,
                    color_by=color_by,
                    density=density_mode,
                    height=map_height,
                )
                st.markdown('<div class="tech-map-shell">', unsafe_allow_html=True)
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config=PLOTLY_CONFIG,
                    key="india_population_map",
                )
                st.markdown(
                    """
                    <div class="tech-map-footer">
                      <span>NODE FIELD: SYNTHETIC CUSTOMERS</span>
                      <span>LINKS: OBSERVABLE SIGNALS ONLY</span>
                      <span>MODE: INTELLIGENCE / EXPLORATION</span>
                    </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.caption(
                    "The visual theme is intentionally cyber/command-center inspired. "
                    "Geography and similarity semantics remain the same: an edge means "
                    "**measurable observable similarity**, not causality."
                )

        # ---- Distributions tab ---------------------------------------------
        with tabs[1]:
            if visible_points.empty:
                st.info("No customers match the current filters.")
            else:
                d1, d2 = st.columns(2)

                with d1:
                    top_cities = (
                        visible_points["city"]
                        .value_counts()
                        .head(15)
                        .sort_values()
                        .rename_axis("city")
                        .reset_index(name="customers")
                    )
                    fig_city = px.bar(
                        top_cities,
                        x="customers",
                        y="city",
                        orientation="h",
                        title="Top cities in current selection",
                        color="customers",
                        color_continuous_scale=["#e0e7ff", "#6366f1", "#06b6d4"],
                    )
                    fig_city.update_layout(coloraxis_showscale=False)
                    st.plotly_chart(
                        style_fig(fig_city, height=520, showlegend=False),
                        use_container_width=True,
                        config=PLOTLY_CONFIG,
                        key="chart_top_cities",
                    )

                with d2:
                    if "customer_type" in visible_points.columns:
                        type_counts = (
                            visible_points["customer_type"]
                            .value_counts()
                            .rename_axis("customer_type")
                            .reset_index(name="customers")
                        )
                        fig_donut = px.pie(
                            type_counts,
                            names="customer_type",
                            values="customers",
                            hole=0.62,
                            title="Customer type mix",
                            color="customer_type",
                            color_discrete_map=CUSTOMER_COLORS,
                        )
                        fig_donut.update_traces(
                            textposition="outside",
                            textinfo="percent+label",
                        )
                        st.plotly_chart(
                            style_fig(fig_donut, height=520, showlegend=False),
                            use_container_width=True,
                            config=PLOTLY_CONFIG,
                            key="chart_type_donut",
                        )

                d3, d4 = st.columns(2)

                with d3:
                    if "state" in visible_points.columns:
                        state_counts = (
                            visible_points["state"]
                            .value_counts()
                            .head(20)
                            .rename_axis("state")
                            .reset_index(name="customers")
                        )
                        fig_state = px.treemap(
                            state_counts,
                            path=["state"],
                            values="customers",
                            title="Customers by state / UT",
                            color="customers",
                            color_continuous_scale=["#eef2ff", "#8b5cf6", "#06b6d4"],
                        )
                        fig_state.update_layout(coloraxis_showscale=False)
                        st.plotly_chart(
                            style_fig(fig_state, height=460, showlegend=False),
                            use_container_width=True,
                            config=PLOTLY_CONFIG,
                            key="chart_state_treemap",
                        )

                with d4:
                    if "gender" in visible_points.columns:
                        gender_counts = (
                            visible_points["gender"]
                            .value_counts()
                            .rename_axis("gender")
                            .reset_index(name="customers")
                        )
                        fig_gender = px.bar(
                            gender_counts,
                            x="gender",
                            y="customers",
                            title="Gender split",
                            color="gender",
                            color_discrete_sequence=PALETTE,
                        )
                        fig_gender.update_layout(showlegend=False)
                        st.plotly_chart(
                            style_fig(fig_gender, height=460, showlegend=False),
                            use_container_width=True,
                            config=PLOTLY_CONFIG,
                            key="chart_gender",
                        )

        # ---- Data explorer tab ---------------------------------------------
        with tabs[2]:
            st.dataframe(
                visible_points.head(2000),
                use_container_width=True,
                height=520,
            )
            st.caption(
                f"Showing up to 2,000 of {len(visible_points):,} filtered rows."
            )
            st.download_button(
                "⬇️ Download visible customers (CSV)",
                data=visible_points.to_csv(index=False).encode("utf-8"),
                file_name=f"population_{population_id[:8]}_visible.csv",
                mime="text/csv",
            )

    except Exception as exc:
        st.error(str(exc))


# =============================================================================
# PAGE 3 — Company experiment
# =============================================================================
elif page == PAGE_NAMES[2]:
    population_id = st.session_state.get("population_id")
    population_size = st.session_state.get("population_size", 30000)

    if not population_id:
        st.warning("Generate a population on Page 1 first.")
        st.stop()

    section(
        "Design the company experiment",
        "Test a campaign, product change, new UI, checkout flow, pricing idea, or other customer intervention before exposing real customers.",
    )

    kpi_row(
        [
            {"label": "Population", "value": f"{population_size:,}", "sub": "Synthetic customers"},
            {"label": "Experiment type", "value": "Choose below", "sub": "Campaign · UI · pricing · checkout"},
            {"label": "Randomisation", "value": "Customer-level", "sub": "Treatment vs control"},
            {"label": "Status", "value": "Ready", "sub": "Configure and run"},
        ]
    )

    st.write("")

    st.markdown(
        '<div class="section-title">1. Choose what the company wants to test</div>'
        '<div class="section-sub">The simulator changes its response mechanism based on the experiment type.</div>',
        unsafe_allow_html=True,
    )

    experiment_type = st.selectbox(
        "Experiment type",
        EXPERIMENT_TYPES,
        index=0,
        help="Choose the business intervention, not the product category.",
    )
    st.info(EXPERIMENT_TYPE_HELP[experiment_type])

    st.write("")

    st.markdown(
        '<div class="section-title">2. Define the business context</div>'
        '<div class="section-sub">Name the initiative and identify the product, service, or experience being changed.</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([1.2, 1.0, 0.9], gap="large")

    with c1:
        experiment_name = st.text_input(
            "Experiment / campaign name",
            "Homepage campaign for new product launch",
        )
    with c2:
        product = st.text_input(
            "Product / service / experience",
            "New product collection",
        )
    with c3:
        category = st.selectbox(
            "Product category",
            PRODUCT_CATEGORIES,
            index=0,
        )

    hypothesis = st.text_area(
        "Business hypothesis",
        "Changing the customer experience will increase conversion or revenue.",
        height=95,
        help="State the measurable behaviour you expect to change.",
    )

    st.markdown(
        '<div class="section-title">3. Define control and treatment</div>'
        '<div class="section-sub">The control is what customers see today; the treatment is the proposed change.</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns(2, gap="large")

    with left:
        control_experience = st.text_area(
            "Control / current experience",
            "Current homepage and standard customer journey.",
            height=125,
            help="Describe what the control group receives.",
        )

    with right:
        offer = st.text_area(
            "Treatment / proposed experience",
            "New campaign creative and product placement shown to the treatment group.",
            height=125,
            help="Describe the change: campaign, UI, checkout, pricing, messaging, feature, etc.",
        )

    st.write("")

    st.markdown(
        '<div class="section-title">4. Measurement & experiment design</div>'
        '<div class="section-sub">Choose the primary outcome and who should receive the intervention.</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns([1, 1, 1], gap="large")

    with c1:
        success_metric = st.selectbox(
            "Primary success metric",
            SUCCESS_METRICS,
            index=0,
        )
    with c2:
        target_segment = st.text_input(
            "Target segment",
            "All customers",
            help="Examples: mobile users, new customers, high-value customers.",
        )
    with c3:
        treatment_share = st.slider(
            "Treatment share",
            min_value=0.10,
            max_value=0.90,
            value=0.50,
            step=0.05,
        )

    c1, c2, c3 = st.columns([1, 1, 1], gap="large")
    with c1:
        experiment_seed = st.number_input(
            "Experiment seed",
            min_value=0,
            max_value=999999,
            value=42,
            step=1,
            help="Same seed produces a reproducible synthetic randomisation.",
        )
    with c2:
        control_n = population_size - int(population_size * treatment_share)
        treatment_n = population_size - control_n
        st.metric("Expected control", f"{control_n:,}")
    with c3:
        st.metric("Expected treatment", f"{treatment_n:,}")

    st.write("")

    if st.button(
        "🚀 Simulate this experiment on synthetic customers",
        type="primary",
        use_container_width=True,
    ):
        try:
            with st.spinner(
                "Randomising synthetic customers and simulating the selected business scenario…"
            ):
                result = post(
                    "/experiments/simulate",
                    {
                        "population_id": population_id,
                        "name": experiment_name,
                        "experiment_type": experiment_type,
                        "product": product,
                        "hypothesis": hypothesis,
                        "control_experience": control_experience,
                        "offer": offer,
                        "success_metric": success_metric,
                        "target_segment": target_segment,
                        "category": category,
                        "treatment_share": treatment_share,
                        "seed": experiment_seed,
                    },
                )

            st.session_state["experiment_result"] = result
            st.session_state["experiment_meta"] = {
                "name": experiment_name,
                "experiment_type": experiment_type,
                "product": product,
                "hypothesis": hypothesis,
                "control_experience": control_experience,
                "offer": offer,
                "success_metric": success_metric,
                "target_segment": target_segment,
                "category": category,
                "treatment_share": treatment_share,
                "seed": experiment_seed,
                "population_id": population_id,
                "population_size": population_size,
                "run_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            }

            st.toast("Experiment completed", icon="✅")
            st.success(f"Experiment completed: {result['experiment_id']}")
            st.info(
                "Open **4. Treatment vs Control** for the full result and "
                "**5. Experiment Report** for the report."
            )

            kpi_row(
                [
                    {"label": "Control conversion", "value": pct(result["control"]["conversion_rate"]), "sub": f"{result['control']['n']:,} customers"},
                    {"label": "Treatment conversion", "value": pct(result["treatment"]["conversion_rate"]), "sub": f"{result['treatment']['n']:,} customers"},
                    {"label": "Absolute uplift", "value": pct(result["absolute_uplift"]), "sub": "Treatment − control"},
                    {
                        "label": "Relative uplift",
                        "value": pct(result["relative_uplift"]) if result["relative_uplift"] is not None else "N/A",
                        "sub": "Share of control rate",
                    },
                ]
            )
        except Exception as exc:
            st.error(str(exc))


# PAGE 4 — Treatment vs control
# =============================================================================
elif page == PAGE_NAMES[3]:
    result = current_result()
    if not result:
        st.warning("Run the company experiment on Page 3 first.")
        st.stop()

    meta = current_meta()

    section(
        meta.get("name", "Virtual experiment"),
        f"{meta.get('experiment_type', 'Experiment')} · {meta.get('product', 'General product')} · Experiment ID {result['experiment_id']}",
    )

    control = result["control"]
    treatment = result["treatment"]
    uplift = result["absolute_uplift"]
    ci_low, ci_high = result["ci_95"]

    kpi_row(
        [
            {"label": "Control conversion", "value": pct(control["conversion_rate"]), "sub": f"{control['n']:,} customers"},
            {"label": "Treatment conversion", "value": pct(treatment["conversion_rate"]), "sub": f"{treatment['n']:,} customers"},
            {"label": "Absolute uplift", "value": pct(uplift), "sub": f"95% CI [{pct(ci_low)}, {pct(ci_high)}]"},
            {
                "label": "Relative uplift",
                "value": pct(result["relative_uplift"]) if result["relative_uplift"] is not None else "N/A",
                "sub": "Relative to control",
            },
        ]
    )

    st.write("")
    kpi_row(
        [
            {"label": "Control revenue", "value": inr(control["revenue"]), "sub": f"{inr(control['revenue_per_customer'], 2)} / customer"},
            {"label": "Treatment revenue", "value": inr(treatment["revenue"]), "sub": f"{inr(treatment['revenue_per_customer'], 2)} / customer"},
            {
                "label": "Revenue delta",
                "value": inr(treatment["revenue"] - control["revenue"]),
                "sub": "Treatment − control",
            },
            {"label": "Recommendation", "value": "See report", "sub": "Page 5"},
        ]
    )

    st.write("")
    tabs = st.tabs(["📈 Uplift & interval", "📊 Arm comparison", "🧩 Segments", "🧾 Raw data"])

    # ---- Uplift tab ---------------------------------------------------------
    with tabs[0]:
        left, right = st.columns([1.1, 1], gap="large")

        with left:
            fig_ci = go.Figure()
            fig_ci.add_trace(
                go.Scatter(
                    x=[uplift],
                    y=["Absolute uplift"],
                    error_x=dict(
                        type="data",
                        symmetric=False,
                        array=[ci_high - uplift],
                        arrayminus=[uplift - ci_low],
                        color="#6366f1",
                        thickness=2.4,
                        width=9,
                    ),
                    mode="markers",
                    marker=dict(size=17, color="#6366f1", line=dict(color="white", width=2)),
                    hovertemplate="Uplift %{x:.2%}<extra></extra>",
                    name="Absolute uplift",
                )
            )
            fig_ci.add_vline(x=0, line_dash="dash", line_color="#ef4444", line_width=1.6)
            fig_ci.update_xaxes(tickformat=".2%", title="Absolute uplift")
            fig_ci.update_layout(title="Uplift with simulated 95% confidence interval")
            st.plotly_chart(
                style_fig(fig_ci, height=340, showlegend=False),
                use_container_width=True,
                config=PLOTLY_CONFIG,
                key="chart_ci",
            )

        with right:
            st.markdown(
                f"""
                <div class="panel">
                  <h4>95% confidence interval</h4>
                  <div class="desc">Simulated sampling variability of the uplift.</div>
                  <div style="font-size:2rem;font-weight:800;color:#0b1220;letter-spacing:-.03em;">
                    [{pct(ci_low)}, {pct(ci_high)}]
                  </div>
                  <div style="margin-top:10px;color:#475569;font-size:.9rem;line-height:1.7;">
                    Control: <b>{pct(control['conversion_rate'])}</b><br>
                    Treatment: <b>{pct(treatment['conversion_rate'])}</b><br>
                    Absolute uplift: <b>{pct(uplift)}</b><br>
                    Relative uplift: <b>{pct(result['relative_uplift']) if result['relative_uplift'] is not None else 'N/A'}</b>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.info(result["interpretation"])

    # ---- Arm comparison -----------------------------------------------------
    with tabs[1]:
        comparison = pd.DataFrame(
            [
                {
                    "Arm": "Control",
                    "Customers": control["n"],
                    "Conversion rate": control["conversion_rate"],
                    "Revenue": control["revenue"],
                    "Revenue / customer": control["revenue_per_customer"],
                },
                {
                    "Arm": "Treatment",
                    "Customers": treatment["n"],
                    "Conversion rate": treatment["conversion_rate"],
                    "Revenue": treatment["revenue"],
                    "Revenue / customer": treatment["revenue_per_customer"],
                },
            ]
        )

        c1, c2 = st.columns(2)

        with c1:
            fig_conv = px.bar(
                comparison,
                x="Arm",
                y="Conversion rate",
                color="Arm",
                text=comparison["Conversion rate"].map(lambda v: f"{v:.2%}"),
                title="Conversion rate by arm",
                color_discrete_map={"Control": "#94a3b8", "Treatment": "#6366f1"},
            )
            fig_conv.update_traces(textposition="outside")
            fig_conv.update_yaxes(tickformat=".1%")
            fig_conv.update_layout(showlegend=False)
            st.plotly_chart(
                style_fig(fig_conv, height=420, showlegend=False),
                use_container_width=True,
                config=PLOTLY_CONFIG,
                key="chart_conv",
            )

        with c2:
            fig_rev = px.bar(
                comparison,
                x="Arm",
                y="Revenue / customer",
                color="Arm",
                text=comparison["Revenue / customer"].map(lambda v: f"₹{v:,.1f}"),
                title="Revenue per customer by arm",
                color_discrete_map={"Control": "#94a3b8", "Treatment": "#06b6d4"},
            )
            fig_rev.update_traces(textposition="outside")
            fig_rev.update_layout(showlegend=False)
            st.plotly_chart(
                style_fig(fig_rev, height=420, showlegend=False),
                use_container_width=True,
                config=PLOTLY_CONFIG,
                key="chart_rev",
            )

        st.dataframe(
            comparison.style.format(
                {
                    "Customers": "{:,}",
                    "Conversion rate": "{:.2%}",
                    "Revenue": "₹{:,.0f}",
                    "Revenue / customer": "₹{:,.2f}",
                }
            ),
            use_container_width=True,
        )

    # ---- Segments -----------------------------------------------------------
    with tabs[2]:
        segment_frame = pd.DataFrame(result.get("segments", []))

        if segment_frame.empty:
            st.info("No segment-level results were returned for this experiment.")
        else:
            display = segment_frame.copy()
            for col in ["control_rate", "treatment_rate", "uplift"]:
                if col in display.columns:
                    display[col] = display[col].map(lambda v: f"{v:.2%}")

            st.dataframe(display, use_container_width=True)

            fig_seg = px.bar(
                segment_frame.sort_values("uplift"),
                x="uplift",
                y="segment",
                orientation="h",
                title="Simulated uplift by segment",
                color="uplift",
                color_continuous_scale=["#ef4444", "#f1f5f9", "#10b981"],
                color_continuous_midpoint=0,
            )
            fig_seg.update_xaxes(tickformat=".2%")
            fig_seg.update_layout(coloraxis_showscale=False)
            st.plotly_chart(
                style_fig(fig_seg, height=max(380, 44 * len(segment_frame)), showlegend=False),
                use_container_width=True,
                config=PLOTLY_CONFIG,
                key="chart_segments",
            )

    # ---- Raw data -----------------------------------------------------------
    with tabs[3]:
        st.json(result, expanded=False)


# =============================================================================
# PAGE 5 — Experiment report
# =============================================================================
else:
    result = current_result()
    if not result:
        st.warning("Run the company experiment on Page 3 first.")
        st.stop()

    meta = current_meta()
    ci_low, ci_high = result["ci_95"]
    uplift = result["absolute_uplift"]
    relative = result["relative_uplift"]

    if ci_low > 0:
        recommendation = (
            "The synthetic experiment shows a positive uplift whose simulated "
            "95% interval is above zero. This supports considering a controlled "
            "real-world pilot, subject to business, operational, and model-risk review."
        )
        rec_tone = "positive"
    elif ci_high < 0:
        recommendation = (
            "The synthetic experiment shows a negative uplift whose simulated "
            "95% interval is below zero. The proposed treatment should be reviewed "
            "before exposing real customers."
        )
        rec_tone = "negative"
    else:
        recommendation = (
            "The synthetic experiment is inconclusive because the simulated "
            "95% interval crosses zero. Consider revising the experiment design "
            "or running a carefully controlled pilot."
        )
        rec_tone = "neutral"

    section(
        meta.get("name", "Virtual experiment"),
        f"Experiment ID {result['experiment_id']} · generated {meta.get('run_at', '—')}",
    )

    kpi_row(
        [
            {"label": "Control conversion", "value": pct(result["control"]["conversion_rate"]), "sub": f"{result['control']['n']:,} customers"},
            {"label": "Treatment conversion", "value": pct(result["treatment"]["conversion_rate"]), "sub": f"{result['treatment']['n']:,} customers"},
            {"label": "Absolute uplift", "value": pct(uplift), "sub": f"95% CI [{pct(ci_low)}, {pct(ci_high)}]"},
            {
                "label": "Relative uplift",
                "value": pct(relative) if relative is not None else "N/A",
                "sub": "Relative to control",
            },
        ]
    )

    st.write("")

    left, right = st.columns([1.5, 1], gap="large")

    with left:
        st.markdown(
            f"""
            <div class="panel">
              <h4>Business setup</h4>
              <div class="desc">What was tested and why.</div>
              <div style="color:#334155;font-size:.92rem;line-height:1.85;">
                <b>Experiment type:</b> {meta.get('experiment_type', '—')}<br>
                <b>Product / experience:</b> {meta.get('product', '—')}<br>
                <b>Category:</b> {meta.get('category', '—')}<br>
                <b>Population:</b> {meta.get('population_size', 0):,} synthetic customers<br>
                <b>Target segment:</b> {meta.get('target_segment', '—')}<br>
                <b>Treatment share:</b> {pct(meta.get('treatment_share', 0), 0)}<br>
                <b>Primary success metric:</b> {meta.get('success_metric', '—')}
              </div>
              <hr style="border:none;border-top:1px solid rgba(15,23,42,.08);margin:14px 0;">
              <div style="color:#334155;font-size:.92rem;line-height:1.8;">
                <b>Hypothesis:</b><br>{meta.get('hypothesis', '—')}<br><br>
                <b>Control / current:</b><br>{meta.get('control_experience', '—')}<br><br>
                <b>Treatment / proposed:</b><br>{meta.get('offer', '—')}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        tone_color = {
            "positive": ("#ecfdf5", "#047857", "#a7f3d0"),
            "negative": ("#fef2f2", "#b91c1c", "#fecaca"),
            "neutral": ("#fffbeb", "#b45309", "#fde68a"),
        }[rec_tone]

        st.markdown(
            f"""
            <div class="panel" style="background:{tone_color[0]};border-color:{tone_color[2]};">
              <h4 style="color:{tone_color[1]};">Decision recommendation</h4>
              <div style="color:#334155;font-size:.92rem;line-height:1.75;margin-top:8px;">
                {recommendation}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    section("Treatment vs control", "Executive summary table.")

    report_table = pd.DataFrame(
        [
            {
                "Arm": "Control",
                "Customers": result["control"]["n"],
                "Conversion": result["control"]["conversion_rate"],
                "Revenue": result["control"]["revenue"],
                "Revenue / customer": result["control"]["revenue_per_customer"],
            },
            {
                "Arm": "Treatment",
                "Customers": result["treatment"]["n"],
                "Conversion": result["treatment"]["conversion_rate"],
                "Revenue": result["treatment"]["revenue"],
                "Revenue / customer": result["treatment"]["revenue_per_customer"],
            },
        ]
    )

    st.dataframe(
        report_table.style.format(
            {
                "Customers": "{:,}",
                "Conversion": "{:.2%}",
                "Revenue": "₹{:,.0f}",
                "Revenue / customer": "₹{:,.2f}",
            }
        ),
        use_container_width=True,
    )

    if result.get("segments"):
        section("Segment findings", "Where the simulated effect is strongest and weakest.")
        seg = pd.DataFrame(result["segments"])
        fmt = {
            c: "{:.2%}"
            for c in ["control_rate", "treatment_rate", "uplift"]
            if c in seg.columns
        }
        st.dataframe(seg.style.format(fmt), use_container_width=True)

    section("Risk and interpretation", "")
    st.warning(
        "This is a synthetic experiment. The 95% confidence interval reflects "
        "randomization/sampling variability within the synthetic run. It does not "
        "capture uncertainty in simulator assumptions. A positive result is evidence "
        "to consider a real-world pilot, not evidence that the same effect will occur "
        "with real customers."
    )

    # ---- Downloads ----------------------------------------------------------
    relative_str = f"{relative:.2%}" if relative is not None else "N/A"

    report_text = f"""# Synthetic Experimentation Lab Report

## Experiment
- Name: {meta.get("name", "Virtual Experiment")}
- Experiment ID: {result["experiment_id"]}
- Experiment type: {meta.get("experiment_type", "—")}
- Product / experience: {meta.get("product", "—")}
- Category: {meta.get("category", "—")}
- Population: {meta.get("population_size", "—")} synthetic customers
- Population ID: {meta.get("population_id", "—")}
- Treatment share: {meta.get("treatment_share", "—")}
- Target segment: {meta.get("target_segment", "—")}
- Run at: {meta.get("run_at", "—")}

## Business setup
Hypothesis: {meta.get("hypothesis", "—")}

Control / current experience: {meta.get("control_experience", "—")}

Treatment / proposed experience: {meta.get("offer", "—")}

Primary success metric: {meta.get("success_metric", "—")}

## Results
Control conversion: {result["control"]["conversion_rate"]:.2%}
Treatment conversion: {result["treatment"]["conversion_rate"]:.2%}
Absolute uplift: {result["absolute_uplift"]:.2%}
Relative uplift: {relative_str}
95% CI: [{result["ci_95"][0]:.2%}, {result["ci_95"][1]:.2%}]

Control revenue: ₹{result["control"]["revenue"]:,.2f}
Treatment revenue: ₹{result["treatment"]["revenue"]:,.2f}
Control revenue / customer: ₹{result["control"]["revenue_per_customer"]:,.2f}
Treatment revenue / customer: ₹{result["treatment"]["revenue_per_customer"]:,.2f}

## Recommendation
{recommendation}

## Caveat
The interval reflects randomization/sampling variability in the synthetic run,
not simulator-assumption uncertainty. A positive synthetic result supports
considering a real-world pilot; it does not prove the same effect will occur
on real customers.
"""

    st.write("")
    d1, d2 = st.columns(2)
    with d1:
        st.download_button(
            "⬇️ Download report (Markdown)",
            data=report_text,
            file_name="synthetic_experiment_report.md",
            mime="text/markdown",
            type="primary",
            use_container_width=True,
        )
    with d2:
        st.download_button(
            "⬇️ Download raw result (JSON)",
            data=json.dumps(
                {"meta": meta, "result": result, "recommendation": recommendation},
                indent=2,
                default=str,
            ),
            file_name="synthetic_experiment_result.json",
            mime="application/json",
            use_container_width=True,
        )

    with st.expander("📄 Full report preview"):
        st.markdown(report_text)


# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown(
    '<div class="footer">Synthetic Experimentation Lab · '
    "Results are simulated and do not prove real-world causal effects.</div>",
    unsafe_allow_html=True,
)
