import os
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API=os.getenv("API_BASE_URL","http://localhost:8000").rstrip("/")
st.set_page_config(page_title="Synthetic Experimentation Lab",page_icon="🧪",layout="wide")
st.markdown("# 🧪 Synthetic Experimentation Lab")
st.markdown("### Test the experiment before testing it on real customers.")
st.caption("A virtual customer population laboratory. Backend: FastAPI on Cloudflare Containers. Database: Neon PostgreSQL.")

def api_get(path,**params):
    response=requests.get(API+path,params=params,timeout=60); response.raise_for_status(); return response.json()
def api_post(path,payload):
    response=requests.post(API+path,json=payload,timeout=180); response.raise_for_status(); return response.json()

with st.sidebar:
    st.header("Lab")
    page=st.radio("Navigate",["Experiment Lab","Synthetic Population","Observable Network","Simulator Truth","History"])

if page=="Experiment Lab":
    st.subheader("Define and run a virtual experiment")
    population_id=st.text_input("Population ID",value=st.session_state.get("population_id",""))
    c1,c2,c3=st.columns(3)
    with c1: name=st.text_input("Experiment name","Beauty offer pilot")
    with c2: category=st.selectbox("Category",["Beauty","Electronics","Grocery"])
    with c3: treatment_share=st.slider("Treatment share",.1,.9,.5,.05)
    seed=st.number_input("Experiment seed",0,999999,42)
    if st.button("Run virtual experiment",type="primary",disabled=not population_id):
        try:
            with st.spinner("Simulating the synthetic population..."):
                st.session_state["result"]=api_post("/experiments/simulate",{"population_id":population_id,"name":name,"category":category,"treatment_share":treatment_share,"seed":seed})
        except Exception as exc: st.error(str(exc))
    result=st.session_state.get("result")
    if result:
        a,b,c,d=st.columns(4); a.metric("Control conversion",f"{result['control']['conversion_rate']:.2%}"); b.metric("Treatment conversion",f"{result['treatment']['conversion_rate']:.2%}"); c.metric("Absolute uplift",f"{result['absolute_uplift']:.2%}"); d.metric("95% CI",f"[{result['ci_95'][0]:.2%}, {result['ci_95'][1]:.2%}]")
        segments=pd.DataFrame(result["segments"])
        if not segments.empty: st.plotly_chart(px.bar(segments,x="segment",y="uplift",title="Simulated uplift by segment"),use_container_width=True)
        st.info(result["interpretation"]); st.success(f"Experiment ID: {result['experiment_id']}")

elif page=="Synthetic Population":
    st.subheader("Generate a synthetic customer population")
    size=st.slider("Population size",100,5000,1500,100); seed=st.number_input("Population seed",0,999999,42)
    if st.button("Generate population",type="primary"):
        try:
            result=api_post("/population/generate",{"size":size,"seed":seed}); st.session_state["population_id"]=result["population_id"]; st.success(result)
        except Exception as exc: st.error(str(exc))
    population_id=st.text_input("Population ID",value=st.session_state.get("population_id",""))
    if population_id:
        try:
            result=api_get(f"/population/{population_id}",limit=100); st.dataframe(pd.DataFrame(result["rows"]),use_container_width=True)
            st.caption("Only company-observable variables are shown. Simulator-hidden variables remain internal.")
        except Exception as exc: st.error(str(exc))

elif page=="Observable Network":
    st.subheader("Observable customer similarity network")
    population_id=st.text_input("Population ID",value=st.session_state.get("population_id",""))
    if population_id:
        try:
            result=api_get("/graph/analytics",population_id=population_id,view="observable")
            a,b,c=st.columns(3); a.metric("Nodes",result.get("nodes",0)); b.metric("Edges",result.get("edges",0)); c.metric("Density",f"{result.get('density',0):.4f}")
            st.dataframe(pd.DataFrame(result.get("top_influence",[])),use_container_width=True)
            st.warning("Graph semantics: an edge means measurable evidence of similarity. No edge does NOT mean the customers are dissimilar.")
        except Exception as exc: st.error(str(exc))

elif page=="Simulator Truth":
    st.subheader("Simulator truth — internal diagnostic")
    st.warning("This view inspects hidden simulator structure. It is not company-observable customer data.")
    population_id=st.text_input("Population ID",value=st.session_state.get("population_id",""))
    if population_id:
        try:
            result=api_get("/graph/analytics",population_id=population_id,view="truth")
            a,b=st.columns(2); a.metric("Truth-network nodes",result.get("nodes",0)); b.metric("Truth-network edges",result.get("edges",0))
            st.dataframe(pd.DataFrame(result.get("top_influence",[])),use_container_width=True)
        except Exception as exc: st.error(str(exc))

else:
    st.subheader("Experiment history")
    try: st.dataframe(pd.DataFrame(api_get("/experiments")),use_container_width=True)
    except Exception as exc: st.error(str(exc))
