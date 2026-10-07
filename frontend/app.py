import os

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


def resolve_api_base_url() -> str:
    """Read the API URL from local env or Streamlit Cloud secrets."""
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
            "API_BASE_URL is not configured. Add it to Streamlit Cloud Secrets "
            "or set it as an environment variable."
        )

    response = requests.get(
        API + path,
        params=params,
        timeout=120,
    )
    if not response.ok:
        raise RuntimeError(api_error(response))
    return response.json()


def post(path: str, payload: dict):
    if not API:
        raise RuntimeError(
            "API_BASE_URL is not configured. Add it to Streamlit Cloud Secrets "
            "or set it as an environment variable."
        )

    response = requests.post(
        API + path,
        json=payload,
        timeout=300,
    )
    if not response.ok:
        raise RuntimeError(api_error(response))
    return response.json()


st.title("🧪 Synthetic Experimentation Lab")
st.subheader("Test the experiment before testing it on real customers.")
st.caption(
    "Synthetic simulation under explicit assumptions. "
    "Use real-world pilots for validation."
)

with st.sidebar:
    page = st.radio(
        "Navigate",
        [
            "Experiment Lab",
            "Synthetic Population",
            "Observable Network",
            "Simulator Truth",
            "History",
        ],
    )
    st.divider()
    st.caption("FastAPI backend")
    st.code(API or "API_BASE_URL not configured")

    if API:
        try:
            health = get("/health")
            st.success("API connected")
            st.caption(f"Database: {health.get('database', 'unknown')}")
        except Exception as exc:
            st.error(f"API unavailable: {exc}")

if page == "Synthetic Population":
    st.header("Synthetic Population")
    st.write(
        "Generate a virtual customer population with observable attributes. "
        "Hidden simulator variables are stored only on the backend."
    )

    size = st.slider("Population size", 100, 5000, 1500, 100)
    seed = st.number_input("Population seed", 0, 999999, 42)

    if st.button("Generate population", type="primary"):
        try:
            with st.spinner("Generating synthetic customers and networks..."):
                result = post(
                    "/population/generate",
                    {"size": size, "seed": seed},
                )
            st.session_state["population_id"] = result["population_id"]
            st.session_state.pop("result", None)
            st.success(
                f"Population created: {result['population_id']} "
                f"({result['size']:,} customers)"
            )
        except Exception as exc:
            st.error(str(exc))

    population_id = st.text_input(
        "Population ID",
        st.session_state.get("population_id", ""),
    )

    if population_id:
        try:
            result = get(f"/population/{population_id}", limit=100)
            st.dataframe(pd.DataFrame(result["rows"]), use_container_width=True)
            st.info(
                "Only observable variables are exposed here. "
                "Simulator-hidden variables remain internal to the backend."
            )
        except Exception as exc:
            st.error(str(exc))

elif page == "Experiment Lab":
    st.header("Experiment Lab")
    st.write(
        "Randomly assign the synthetic customers to control and treatment, "
        "simulate heterogeneous responses, and estimate uplift."
    )

    population_id = st.text_input(
        "Population ID",
        st.session_state.get("population_id", ""),
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        name = st.text_input("Experiment name", "Beauty offer pilot")
    with c2:
        category = st.selectbox("Category", ["Beauty", "Electronics", "Grocery"])
    with c3:
        share = st.slider("Treatment share", 0.1, 0.9, 0.5, 0.05)

    seed = st.number_input("Experiment seed", 0, 999999, 42)

    if st.button(
        "Run virtual experiment",
        type="primary",
        disabled=not population_id,
    ):
        try:
            with st.spinner("Simulating synthetic customers..."):
                st.session_state["result"] = post(
                    "/experiments/simulate",
                    {
                        "population_id": population_id,
                        "name": name,
                        "category": category,
                        "treatment_share": share,
                        "seed": seed,
                    },
                )
        except Exception as exc:
            st.error(str(exc))

    result = st.session_state.get("result")

    if result:
        a, b, c, d = st.columns(4)
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
            f"{result['absolute_uplift']:.2%}",
        )
        d.metric(
            "95% CI",
            f"[{result['ci_95'][0]:.2%}, {result['ci_95'][1]:.2%}]",
        )

        e, f = st.columns(2)
        e.metric(
            "Control revenue / customer",
            f"₹{result['control']['revenue_per_customer']:,.0f}",
        )
        f.metric(
            "Treatment revenue / customer",
            f"₹{result['treatment']['revenue_per_customer']:,.0f}",
        )

        segment_frame = pd.DataFrame(result["segments"])
        if not segment_frame.empty:
            st.plotly_chart(
                px.bar(
                    segment_frame,
                    x="segment",
                    y="uplift",
                    title="Simulated uplift by segment",
                ),
                use_container_width=True,
            )

        st.info(result["interpretation"])

elif page == "Observable Network":
    st.header("Observable Similarity Network")
    st.write(
        "This graph uses only customer attributes the company could reasonably observe."
    )

    population_id = st.text_input(
        "Population ID",
        st.session_state.get("population_id", ""),
    )

    if population_id:
        try:
            result = get(
                "/graph/analytics",
                population_id=population_id,
                view="observable",
            )
            a, b, c = st.columns(3)
            a.metric("Nodes", result["nodes"])
            b.metric("Edges", result["edges"])
            c.metric("Density", f"{result['density']:.4f}")

            st.dataframe(
                pd.DataFrame(result["top_influence"]),
                use_container_width=True,
            )
            st.warning(
                "Edge = measurable evidence of similarity. "
                "No edge does not mean no similarity. "
                "Network centrality is not causal influence."
            )
        except Exception as exc:
            st.error(str(exc))

elif page == "Simulator Truth":
    st.header("Simulator Truth — Internal Diagnostic")
    st.warning(
        "This view uses hidden simulator behavior to diagnose the simulation. "
        "It is not presented as observable customer data."
    )

    population_id = st.text_input(
        "Population ID",
        st.session_state.get("population_id", ""),
    )

    if population_id:
        try:
            result = get(
                "/graph/analytics",
                population_id=population_id,
                view="truth",
            )
            a, b = st.columns(2)
            a.metric("Nodes", result["nodes"])
            b.metric("Edges", result["edges"])

            st.dataframe(
                pd.DataFrame(result["top_influence"]),
                use_container_width=True,
            )
        except Exception as exc:
            st.error(str(exc))

else:
    st.header("Experiment History")
    try:
        history = pd.DataFrame(get("/experiments"))
        if history.empty:
            st.info("No experiments have been run yet.")
        else:
            st.dataframe(history, use_container_width=True)
    except Exception as exc:
        st.error(str(exc))
