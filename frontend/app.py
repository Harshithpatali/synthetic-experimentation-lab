import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st


PAGE_NAMES = [
    "1. Generate Population",
    "2. India Population Map",
    "3. Company Experiment",
    "4. Treatment vs Control",
    "5. Experiment Report",
]


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

st.set_page_config(
    page_title="Synthetic Experimentation Lab",
    page_icon="🧪",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
    .hero {padding: 1.2rem 1.4rem; border-radius: 16px; background: linear-gradient(135deg,#f7f2ff,#eef7ff);}
    .small-note {color:#667085; font-size:0.92rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


def api_error(response: requests.Response) -> str:
    try:
        payload = response.json()
        detail = payload.get("detail")
        if detail:
            return str(detail)
    except ValueError:
        pass
    return f"Backend returned HTTP {response.status_code}."


def get(path: str, **params):
    if not API:
        raise RuntimeError(
            "API_BASE_URL is not configured. Add it to Streamlit Cloud Secrets."
        )

    response = requests.get(
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

    response = requests.post(
        API + path,
        json=payload,
        timeout=600,
    )
    if not response.ok:
        raise RuntimeError(api_error(response))
    return response.json()


@st.cache_data(ttl=600, show_spinner=False)
def load_population_map(population_id: str):
    return get(f"/population/{population_id}/map", limit=30000)


@st.cache_data(ttl=600, show_spinner=False)
def load_network(population_id: str, limit: int):
    return get(
        "/network",
        population_id=population_id,
        view="observable",
        limit=limit,
    )


def build_india_network_map(
    population_rows: pd.DataFrame,
    edge_rows: list[dict],
) -> go.Figure:
    points = population_rows.copy()
    points["lat"] = pd.to_numeric(points["lat"])
    points["lon"] = pd.to_numeric(points["lon"])

    coords = points.set_index("id")[["lat", "lon"]]
    edge_lat = []
    edge_lon = []

    for edge in edge_rows:
        source = edge.get("source")
        target = edge.get("target")

        if source not in coords.index or target not in coords.index:
            continue

        edge_lat.extend(
            [coords.at[source, "lat"], coords.at[target, "lat"], None]
        )
        edge_lon.extend(
            [coords.at[source, "lon"], coords.at[target, "lon"], None]
        )

    fig = go.Figure()

    if edge_lat:
        fig.add_trace(
            go.Scattergeo(
                lat=edge_lat,
                lon=edge_lon,
                mode="lines",
                line=dict(width=0.8, color="rgba(99,102,241,0.18)"),
                hoverinfo="skip",
                name="Similarity edges",
            )
        )

    color_map = {
        "New": "#60A5FA",
        "Repeat": "#8B5CF6",
        "Loyal": "#F59E0B",
    }

    for customer_type in ["New", "Repeat", "Loyal"]:
        subset = points[points["customer_type"] == customer_type]
        if subset.empty:
            continue

        fig.add_trace(
            go.Scattergeo(
                lat=subset["lat"],
                lon=subset["lon"],
                mode="markers",
                marker=dict(
                    size=4,
                    opacity=0.62,
                    color=color_map[customer_type],
                ),
                text=subset.apply(
                    lambda row: (
                        f"City: {row['city']}<br>"
                        f"State: {row['state']}<br>"
                        f"Gender: {row['gender']}<br>"
                        f"Customer type: {row['customer_type']}"
                    ),
                    axis=1,
                ),
                hovertemplate="%{text}<extra></extra>",
                name=customer_type,
            )
        )

    fig.update_geos(
        scope="asia",
        projection_type="mercator",
        center=dict(lat=22.0, lon=79.0),
        projection_scale=4.6,
        lonaxis=dict(range=[67, 98]),
        lataxis=dict(range=[6, 38]),
        showland=True,
        landcolor="#F5F7FA",
        showocean=True,
        oceancolor="#EAF2FF",
        showlakes=True,
        lakecolor="#EAF2FF",
        showcountries=True,
        countrycolor="#98A2B3",
        showcoastlines=True,
        coastlinecolor="#667085",
        showframe=False,
    )

    fig.update_layout(
        title="30,000 Synthetic Customers across India",
        height=720,
        margin=dict(l=0, r=0, t=50, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0),
        paper_bgcolor="white",
    )
    return fig


def current_result():
    return st.session_state.get("experiment_result")


st.title("🧪 Synthetic Experimentation Lab")
st.markdown(
    """
    <div class="hero">
      <h3 style="margin:0;">Test the experiment before testing it on real customers.</h3>
      <div class="small-note">
        Generate a virtual Indian customer population, inspect its observable
        similarity network, simulate a company experiment, and produce a
        decision-ready report.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### Lab workflow")
    page = st.radio("Step", PAGE_NAMES)
    st.divider()

    if API:
        try:
            health = get("/health")
            st.success("FastAPI + Neon connected")
            st.caption(API)
            st.caption(f"Database: {health.get('database', 'unknown')}")
        except Exception as exc:
            st.error(f"Backend unavailable: {exc}")
    else:
        st.error("API_BASE_URL is not configured.")

    st.divider()
    if st.session_state.get("population_id"):
        st.caption("Active population")
        st.code(st.session_state["population_id"])

    if current_result():
        st.caption("Experiment result available")
        st.code(current_result()["experiment_id"])


if page == PAGE_NAMES[0]:
    st.header("1. Generate Population")
    st.write(
        "Create the virtual customer population that the company will experiment on."
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        population_size = st.slider(
            "Population size",
            min_value=5000,
            max_value=30000,
            value=30000,
            step=5000,
        )
    with col2:
        population_seed = st.number_input(
            "Population seed",
            min_value=0,
            max_value=999999,
            value=42,
            step=1,
        )

    st.info(
        "The 30,000-customer default is distributed across major Indian cities. "
        "Each customer receives a small geographic jitter around the city center."
    )

    if st.button("Generate 30,000 synthetic customers", type="primary"):
        try:
            with st.spinner(
                "Generating customers, hidden simulator behavior, and observable network..."
            ):
                result = post(
                    "/population/generate",
                    {
                        "size": population_size,
                        "seed": population_seed,
                    },
                )

            st.session_state["population_id"] = result["population_id"]
            st.session_state["population_size"] = result["size"]
            st.session_state.pop("experiment_result", None)
            st.session_state.pop("experiment_meta", None)

            load_population_map.clear()
            load_network.clear()

            st.success(
                f"Population created: {result['size']:,} customers"
            )
            st.write(f"Population ID: {result['population_id']}")

            a, b, c = st.columns(3)
            a.metric("Customers", f"{result['size']:,}")
            b.metric("Seed", result["seed"])
            c.metric("Next step", "Open Page 2")
        except Exception as exc:
            st.error(str(exc))


elif page == PAGE_NAMES[1]:
    st.header("2. India Population Map")

    population_id = st.session_state.get("population_id")
    if not population_id:
        st.warning("Generate a population on Page 1 first.")
        st.stop()

    try:
        with st.spinner("Loading the Indian population map..."):
            map_payload = load_population_map(population_id)

        points = pd.DataFrame(map_payload["rows"])

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Customers mapped", f"{len(points):,}")
        c2.metric("Indian cities", f"{points['city'].nunique():,}")
        c3.metric("States / UTs", f"{points['state'].nunique():,}")

        edge_limit = st.slider(
            "Visible strongest similarity edges",
            min_value=1000,
            max_value=10000,
            value=6000,
            step=1000,
        )

        with st.spinner("Loading similarity edges..."):
            network_payload = load_network(population_id, edge_limit)

        c4.metric("Edges drawn", f"{len(network_payload['edges']):,}")

        city_filter = st.selectbox(
            "City filter",
            ["All India"] + sorted(points["city"].unique().tolist()),
        )

        if city_filter != "All India":
            visible_points = points[points["city"] == city_filter].copy()
            visible_ids = set(visible_points["id"])
            visible_edges = [
                edge
                for edge in network_payload["edges"]
                if edge["source"] in visible_ids
                and edge["target"] in visible_ids
            ]
        else:
            visible_points = points
            visible_edges = network_payload["edges"]

        st.plotly_chart(
            build_india_network_map(visible_points, visible_edges),
            use_container_width=True,
        )

        st.caption(
            "The base map is geographic. Points are synthetic customer locations. "
            "An edge represents measurable observable similarity, not a causal relationship. "
            "Only the strongest requested edges are drawn so the 30,000-customer map remains usable."
        )

    except Exception as exc:
        st.error(str(exc))


elif page == PAGE_NAMES[2]:
    st.header("3. Company Experiment")
    st.write(
        "Define the business experiment you want to test before exposing real customers."
    )

    population_id = st.session_state.get("population_id")
    population_size = st.session_state.get("population_size", 30000)

    if not population_id:
        st.warning("Generate a population on Page 1 first.")
        st.stop()

    st.write(f"Population ID: {population_id}")

    col1, col2 = st.columns(2)
    with col1:
        experiment_name = st.text_input(
            "Experiment name",
            "Beauty offer pilot",
        )
        hypothesis = st.text_area(
            "Business hypothesis",
            "A targeted beauty offer will increase customer conversion.",
        )
        offer = st.text_area(
            "Treatment / offer",
            "Personalized beauty promotion shown to the treatment group.",
        )
    with col2:
        category = st.selectbox(
            "Experiment category",
            ["Beauty", "Electronics", "Grocery"],
        )
        success_metric = st.text_input(
            "Primary success metric",
            "Conversion rate",
        )
        target_segment = st.text_input(
            "Target segment",
            "All customers",
        )

    col1, col2, col3 = st.columns(3)
    with col1:
        treatment_share = st.slider(
            "Treatment share",
            min_value=0.10,
            max_value=0.90,
            value=0.50,
            step=0.05,
        )
    with col2:
        experiment_seed = st.number_input(
            "Experiment seed",
            min_value=0,
            max_value=999999,
            value=42,
            step=1,
        )
    with col3:
        st.metric("Synthetic sample", f"{population_size:,}")

    control_n = population_size - int(population_size * treatment_share)
    treatment_n = population_size - control_n

    a, b = st.columns(2)
    a.metric("Expected control", f"{control_n:,}")
    b.metric("Expected treatment", f"{treatment_n:,}")

    if st.button("Run virtual experiment", type="primary"):
        try:
            with st.spinner(
                "Randomizing synthetic customers and simulating responses..."
            ):
                result = post(
                    "/experiments/simulate",
                    {
                        "population_id": population_id,
                        "name": experiment_name,
                        "hypothesis": hypothesis,
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
                "hypothesis": hypothesis,
                "offer": offer,
                "success_metric": success_metric,
                "target_segment": target_segment,
                "category": category,
                "treatment_share": treatment_share,
                "seed": experiment_seed,
                "population_id": population_id,
                "population_size": population_size,
            }

            st.success(
                f"Experiment completed: {result['experiment_id']}"
            )
            st.info(
                "Open Page 4 for the full treatment-vs-control result and Page 5 for the report."
            )
        except Exception as exc:
            st.error(str(exc))


elif page == PAGE_NAMES[3]:
    st.header("4. Treatment vs Control")

    result = current_result()
    if not result:
        st.warning("Run the company experiment on Page 3 first.")
        st.stop()

    meta = st.session_state.get("experiment_meta", {})

    st.caption(
        f"{meta.get('name', 'Virtual Experiment')} · "
        f"{meta.get('category', 'Unknown')} · "
        f"Experiment ID: {result['experiment_id']}"
    )

    control = result["control"]
    treatment = result["treatment"]

    a, b, c, d = st.columns(4)
    a.metric("Control conversion", f"{control['conversion_rate']:.2%}")
    b.metric("Treatment conversion", f"{treatment['conversion_rate']:.2%}")
    c.metric("Absolute uplift", f"{result['absolute_uplift']:.2%}")
    d.metric(
        "Relative uplift",
        (
            f"{result['relative_uplift']:.2%}"
            if result["relative_uplift"] is not None
            else "N/A"
        ),
    )

    a, b, c, d = st.columns(4)
    a.metric("Control customers", f"{control['n']:,}")
    b.metric("Treatment customers", f"{treatment['n']:,}")
    c.metric("Control revenue", f"₹{control['revenue']:,.0f}")
    d.metric("Treatment revenue", f"₹{treatment['revenue']:,.0f}")

    st.subheader("95% confidence interval")
    st.write(
        f"Absolute uplift CI: **[{result['ci_95'][0]:.2%}, {result['ci_95'][1]:.2%}]**"
    )

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

    st.subheader("Full arm comparison")
    st.dataframe(comparison, use_container_width=True)

    segment_frame = pd.DataFrame(result.get("segments", []))
    if not segment_frame.empty:
        st.subheader("Segment-level results")

        display_segments = segment_frame.copy()
        display_segments["control_rate"] = display_segments["control_rate"].map(
            lambda x: f"{x:.2%}"
        )
        display_segments["treatment_rate"] = display_segments["treatment_rate"].map(
            lambda x: f"{x:.2%}"
        )
        display_segments["uplift"] = display_segments["uplift"].map(
            lambda x: f"{x:.2%}"
        )

        st.dataframe(display_segments, use_container_width=True)

        st.plotly_chart(
            px.bar(
                segment_frame.sort_values("uplift"),
                x="uplift",
                y="segment",
                orientation="h",
                title="Simulated uplift by segment",
            ),
            use_container_width=True,
        )

    st.info(result["interpretation"])


else:
    st.header("5. Experiment Report")

    result = current_result()
    if not result:
        st.warning("Run the company experiment on Page 3 first.")
        st.stop()

    meta = st.session_state.get("experiment_meta", {})
    ci_low, ci_high = result["ci_95"]
    uplift = result["absolute_uplift"]

    if ci_low > 0:
        recommendation = (
            "The synthetic experiment shows a positive uplift whose simulated "
            "95% interval is above zero. This supports considering a controlled "
            "real-world pilot, subject to business, operational, and model-risk review."
        )
    elif ci_high < 0:
        recommendation = (
            "The synthetic experiment shows a negative uplift whose simulated "
            "95% interval is below zero. The proposed treatment should be reviewed "
            "before exposing real customers."
        )
    else:
        recommendation = (
            "The synthetic experiment is inconclusive because the simulated "
            "95% interval crosses zero. Consider revising the experiment design "
            "or running a carefully controlled pilot."
        )

    st.markdown(
        f"""
        ## {meta.get('name', 'Virtual Experiment')}

        **Population:** {meta.get('population_size', 0):,} synthetic customers  
        **Category:** {meta.get('category', '—')}  
        **Target segment:** {meta.get('target_segment', '—')}  
        **Treatment share:** {meta.get('treatment_share', 0):.0%}  
        **Experiment ID:** {result['experiment_id']}

        ### Business setup

        **Hypothesis:** {meta.get('hypothesis', '—')}

        **Treatment / offer:** {meta.get('offer', '—')}

        **Primary success metric:** {meta.get('success_metric', '—')}
        """
    )

    st.subheader("Executive result")

    a, b, c = st.columns(3)
    a.metric(
        "Control conversion",
        f"{result['control']['conversion_rate']:.2%}",
    )
    b.metric(
        "Treatment conversion",
        f"{result['treatment']['conversion_rate']:.2%}",
    )
    c.metric(
        "Absolute uplift",
        f"{uplift:.2%}",
    )

    st.write(f"Simulated 95% CI: [{ci_low:.2%}, {ci_high:.2%}]")

    st.subheader("Decision recommendation")
    st.info(recommendation)

    st.subheader("Treatment vs control")
    report_table = pd.DataFrame(
        [
            {
                "Arm": "Control",
                "Customers": result["control"]["n"],
                "Conversion": f"{result['control']['conversion_rate']:.2%}",
                "Revenue": f"₹{result['control']['revenue']:,.0f}",
                "Revenue / customer": f"₹{result['control']['revenue_per_customer']:,.2f}",
            },
            {
                "Arm": "Treatment",
                "Customers": result["treatment"]["n"],
                "Conversion": f"{result['treatment']['conversion_rate']:.2%}",
                "Revenue": f"₹{result['treatment']['revenue']:,.0f}",
                "Revenue / customer": f"₹{result['treatment']['revenue_per_customer']:,.2f}",
            },
        ]
    )
    st.dataframe(report_table, use_container_width=True)

    if result.get("segments"):
        st.subheader("Segment findings")
        st.dataframe(
            pd.DataFrame(result["segments"]).style.format(
                {
                    "control_rate": "{:.2%}",
                    "treatment_rate": "{:.2%}",
                    "uplift": "{:.2%}",
                }
            ),
            use_container_width=True,
        )

    st.subheader("Risk and interpretation")
    st.warning(
        "This is a synthetic experiment. The 95% confidence interval reflects "
        "randomization/sampling variability within the synthetic run. It does not "
        "capture uncertainty in simulator assumptions. A positive result is evidence "
        "to consider a real-world pilot, not evidence that the same effect will occur "
        "with real customers."
    )

    report_text = f"""# Synthetic Experimentation Lab Report

## Experiment
- Name: {meta.get("name", "Virtual Experiment")}
- Experiment ID: {result["experiment_id"]}
- Category: {meta.get("category", "—")}
- Population: {meta.get("population_size", "—")}
- Treatment share: {meta.get("treatment_share", "—")}
- Target segment: {meta.get("target_segment", "—")}

## Business setup
Hypothesis: {meta.get("hypothesis", "—")}

Treatment / offer: {meta.get("offer", "—")}

Primary success metric: {meta.get("success_metric", "—")}

## Results
Control conversion: {result["control"]["conversion_rate"]:.2%}
Treatment conversion: {result["treatment"]["conversion_rate"]:.2%}
Absolute uplift: {result["absolute_uplift"]:.2%}
Relative uplift: {result["relative_uplift"] if result["relative_uplift"] is not None else "N/A"}
95% CI: [{result["ci_95"][0]:.2%}, {result["ci_95"][1]:.2%}]

Control revenue: ₹{result["control"]["revenue"]:,.2f}
Treatment revenue: ₹{result["treatment"]["revenue"]:,.2f}

## Recommendation
{recommendation}

## Caveat
The interval reflects randomization/sampling variability in the synthetic run,
not simulator-assumption uncertainty. A positive synthetic result supports
considering a real-world pilot; it does not prove the same effect will occur
on real customers.
"""

    st.download_button(
        "Download report (Markdown)",
        data=report_text,
        file_name="synthetic_experiment_report.md",
        mime="text/markdown",
        type="primary",
    )
