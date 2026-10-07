import os
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API=os.getenv("API_BASE_URL","http://localhost:8000").rstrip("/")
st.set_page_config(page_title="Synthetic Experimentation Lab",page_icon="🧪",layout="wide")

def get(path,**params):
    r=requests.get(API+path,params=params,timeout=120); r.raise_for_status(); return r.json()

def post(path,payload):
    r=requests.post(API+path,json=payload,timeout=300); r.raise_for_status(); return r.json()

st.title("🧪 Synthetic Experimentation Lab")
st.subheader("Test the experiment before testing it on real customers.")
st.caption("Synthetic simulation under explicit assumptions. Use real-world pilots for validation.")

with st.sidebar:
    page=st.radio("Navigate",["Experiment Lab","Synthetic Population","Observable Network","Simulator Truth","History"])
    st.divider()
    st.caption("FastAPI backend")
    st.code(API)

if page=="Synthetic Population":
    st.header("Synthetic Population")
    size=st.slider("Population size",100,5000,1500,100)
    seed=st.number_input("Population seed",0,999999,42)
    if st.button("Generate population",type="primary"):
        try:
            result=post("/population/generate",{"size":size,"seed":seed})
            st.session_state["population_id"]=result["population_id"]
            st.success(f"Population created: {result['population_id']}")
        except Exception as e: st.error(str(e))
    population_id=st.text_input("Population ID",st.session_state.get("population_id",""))
    if population_id:
        try:
            result=get(f"/population/{population_id}",limit=100)
            st.dataframe(pd.DataFrame(result["rows"]),use_container_width=True)
            st.info("Only observable variables are exposed. Simulator-hidden variables remain internal.")
        except Exception as e: st.error(str(e))

elif page=="Experiment Lab":
    st.header("Experiment Lab")
    population_id=st.text_input("Population ID",st.session_state.get("population_id",""))
    c1,c2,c3=st.columns(3)
    with c1: name=st.text_input("Experiment name","Beauty offer pilot")
    with c2: category=st.selectbox("Category",["Beauty","Electronics","Grocery"])
    with c3: share=st.slider("Treatment share",.1,.9,.5,.05)
    seed=st.number_input("Experiment seed",0,999999,42)
    if st.button("Run virtual experiment",type="primary",disabled=not population_id):
        try:
            with st.spinner("Simulating synthetic customers..."):
                st.session_state["result"]=post("/experiments/simulate",{"population_id":population_id,"name":name,"category":category,"treatment_share":share,"seed":seed})
        except Exception as e: st.error(str(e))
    result=st.session_state.get("result")
    if result:
        a,b,c,d=st.columns(4)
        a.metric("Control conversion",f"{result['control']['conversion_rate']:.2%}")
        b.metric("Treatment conversion",f"{result['treatment']['conversion_rate']:.2%}")
        c.metric("Absolute uplift",f"{result['absolute_uplift']:.2%}")
        d.metric("95% CI",f"[{result['ci_95'][0]:.2%}, {result['ci_95'][1]:.2%}]")
        seg=pd.DataFrame(result["segments"])
        if not seg.empty: st.plotly_chart(px.bar(seg,x="segment",y="uplift",title="Simulated uplift by segment"),use_container_width=True)
        st.info(result["interpretation"])

elif page=="Observable Network":
    st.header("Observable Similarity Network")
    population_id=st.text_input("Population ID",st.session_state.get("population_id",""))
    if population_id:
        try:
            result=get("/graph/analytics",population_id=population_id,view="observable")
            a,b,c=st.columns(3); a.metric("Nodes",result["nodes"]); b.metric("Edges",result["edges"]); c.metric("Density",f"{result['density']:.4f}")
            st.dataframe(pd.DataFrame(result["top_influence"]),use_container_width=True)
            st.warning("Edge = measurable evidence of similarity. No edge ≠ no similarity.")
        except Exception as e: st.error(str(e))

elif page=="Simulator Truth":
    st.header("Simulator Truth — Internal Diagnostic")
    st.warning("This view is simulator-internal. It is not company-observable customer data.")
    population_id=st.text_input("Population ID",st.session_state.get("population_id",""))
    if population_id:
        try:
            result=get("/graph/analytics",population_id=population_id,view="truth")
            a,b=st.columns(2); a.metric("Nodes",result["nodes"]); b.metric("Edges",result["edges"])
            st.dataframe(pd.DataFrame(result["top_influence"]),use_container_width=True)
        except Exception as e: st.error(str(e))

else:
    st.header("Experiment History")
    try:
        st.dataframe(pd.DataFrame(get("/experiments")),use_container_width=True)
    except Exception as e: st.error(str(e))
