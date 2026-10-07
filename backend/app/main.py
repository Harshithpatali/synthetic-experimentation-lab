import uuid
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from .analytics import difference_in_proportions, segment_results
from .config import CORS_ORIGINS
from .db import Base, engine, get_db
from .models import Customer, CustomerEdge, Experiment, ExperimentOutcome, PopulationRun, SegmentResult, SimulatorTruth
from .schemas import ExperimentCreate, PopulationCreate
from .simulation import build_similarity_edges, generate_population, simulate_outcomes

app=FastAPI(title="Synthetic Experimentation Lab API",version="2.0.0",description="Test experiments on a synthetic population before exposing real customers.")
app.add_middleware(CORSMiddleware,allow_origins=["*"] if CORS_ORIGINS==["*"] else CORS_ORIGINS,allow_credentials=False,allow_methods=["*"],allow_headers=["*"])

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"service":"synthetic-experimentation-lab","backend":"FastAPI","database":"Neon PostgreSQL","status":"ok"}

@app.get("/health")
def health(db:Session=Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status":"ok","database":"connected"}

@app.post("/population/generate")
def create_population(req:PopulationCreate,db:Session=Depends(get_db)):
    population_id=str(uuid.uuid4()); population=generate_population(req.size,req.seed)
    db.add(PopulationRun(id=population_id,seed=req.seed,size=req.size,config={"hidden_variables_internal":True}))
    db.add_all([Customer(population_id=population_id,**c) for c in population.customers])
    db.add_all([SimulatorTruth(population_id=population_id,**t) for t in population.truth])
    for view in ("observable","truth"):
        db.add_all([CustomerEdge(population_id=population_id,**e) for e in build_similarity_edges(population.customers,population.truth,view)])
    db.commit()
    return {"population_id":population_id,"size":req.size,"seed":req.seed}

@app.get("/population/{population_id}")
def get_population(population_id:str,limit:int=100,db:Session=Depends(get_db)):
    rows=db.query(Customer).filter(Customer.population_id==population_id).limit(limit).all()
    if not rows: raise HTTPException(404,"Population not found")
    fields=["id","age","gender","city","state","lat","lon","device","customer_type","orders","aov","recency_days","sessions_30d","cart_abandonments"]
    return {"population_id":population_id,"rows":[{f:getattr(row,f) for f in fields} for row in rows]}

@app.get("/network")
def network(population_id:str,view:str="observable",limit:int=3000,db:Session=Depends(get_db)):
    if view not in {"observable","truth"}: raise HTTPException(400,"view must be observable or truth")
    edges=db.query(CustomerEdge).filter(CustomerEdge.population_id==population_id,CustomerEdge.view==view).limit(limit).all()
    return {"population_id":population_id,"view":view,"semantic":"An edge means measurable evidence of similarity. No edge does not mean no similarity.","edges":[{"source":e.source_id,"target":e.target_id,"weight":e.weight,"reasons":e.reasons} for e in edges]}

@app.get("/graph/analytics")
def graph_analytics(population_id:str,view:str="observable",db:Session=Depends(get_db)):
    edges=db.query(CustomerEdge).filter(CustomerEdge.population_id==population_id,CustomerEdge.view==view).all()
    weighted_degree={}; nodes=set()
    for e in edges:
        nodes.add(e.source_id); nodes.add(e.target_id); weighted_degree[e.source_id]=weighted_degree.get(e.source_id,0)+e.weight
    n=len(nodes); m=len(edges)
    top=sorted(weighted_degree.items(),key=lambda x:x[1],reverse=True)[:10]
    return {"nodes":n,"edges":m,"density":m/(n*(n-1)) if n>1 else 0,"top_influence":[{"customer_id":k,"weighted_degree":v} for k,v in top],"note":"Centrality is not causal influence."}

@app.post("/experiments/simulate")
def run_experiment(req:ExperimentCreate,db:Session=Depends(get_db)):
    customers=db.query(Customer).filter(Customer.population_id==req.population_id).all()
    truths=db.query(SimulatorTruth).filter(SimulatorTruth.population_id==req.population_id).all()
    if not customers: raise HTTPException(404,"Population not found")
    customer_dicts=[{"id":c.id,"age":c.age,"gender":c.gender,"orders":c.orders,"aov":c.aov,"recency_days":c.recency_days,"sessions_30d":c.sessions_30d,"customer_type":c.customer_type} for c in customers]
    truth_by_customer={t.customer_id:{"price_sensitivity":t.price_sensitivity,"novelty_preference":t.novelty_preference,"beauty_affinity":t.beauty_affinity,"electronics_affinity":t.electronics_affinity,"grocery_affinity":t.grocery_affinity} for t in truths}
    outcomes,segments=simulate_outcomes(customer_dicts,truth_by_customer,req.category,req.treatment_share,req.seed)
    experiment_id=str(uuid.uuid4())
    db.add(Experiment(id=experiment_id,population_id=req.population_id,name=req.name,category=req.category,treatment_share=req.treatment_share,seed=req.seed,config={"synthetic":True,"hidden_variables_used":True}))
    db.add_all([ExperimentOutcome(id=str(uuid.uuid4()),experiment_id=experiment_id,**o) for o in outcomes])
    segment_rows=segment_results(segments)
    db.add_all([SegmentResult(id=str(uuid.uuid4()),experiment_id=experiment_id,**r) for r in segment_rows])
    control=[o for o in outcomes if o["arm"]=="control"]; treatment=[o for o in outcomes if o["arm"]=="treatment"]
    stats=difference_in_proportions(len(control),sum(o["converted"] for o in control),len(treatment),sum(o["converted"] for o in treatment))
    db.commit()
    return {"experiment_id":experiment_id,"population_id":req.population_id,"control":{"n":len(control),"conversion_rate":stats["control_rate"]},"treatment":{"n":len(treatment),"conversion_rate":stats["treatment_rate"]},"absolute_uplift":stats["uplift"],"relative_uplift":stats["uplift"]/stats["control_rate"] if stats["control_rate"] else None,"ci_95":[stats["ci_low"],stats["ci_high"]],"revenue_control":sum(o["revenue"] for o in control),"revenue_treatment":sum(o["revenue"] for o in treatment),"segments":segment_rows,"interpretation":"The 95% interval reflects randomization/sampling variability in the synthetic run, not simulator-assumption uncertainty."}

@app.get("/experiments")
def experiments(limit:int=20,db:Session=Depends(get_db)):
    rows=db.query(Experiment).order_by(Experiment.created_at.desc()).limit(limit).all()
    return [{"experiment_id":r.id,"name":r.name,"category":r.category,"population_id":r.population_id,"seed":r.seed,"created_at":r.created_at} for r in rows]
