import os, math, uuid
from datetime import datetime, timezone
import networkx as nx
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL","postgresql+psycopg://synthetic:synthetic@localhost:5432/synthetic_lab")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase): pass
class Population(Base):
    __tablename__="population_runs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    seed: Mapped[int] = mapped_column(Integer)
    size: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    config: Mapped[dict] = mapped_column(JSON)
class Customer(Base):
    __tablename__="customers"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    population_id: Mapped[str] = mapped_column(ForeignKey("population_runs.id"), index=True)
    age: Mapped[int] = mapped_column(Integer); gender: Mapped[str] = mapped_column(String(20))
    city: Mapped[str] = mapped_column(String(80)); state: Mapped[str] = mapped_column(String(80))
    lat: Mapped[float] = mapped_column(Float); lon: Mapped[float] = mapped_column(Float)
    device: Mapped[str] = mapped_column(String(20)); customer_type: Mapped[str] = mapped_column(String(30))
    orders: Mapped[int] = mapped_column(Integer); aov: Mapped[float] = mapped_column(Float)
    recency_days: Mapped[int] = mapped_column(Integer); sessions_30d: Mapped[int] = mapped_column(Integer)
    cart_abandonments: Mapped[int] = mapped_column(Integer)
class Truth(Base):
    __tablename__="simulator_truth"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    population_id: Mapped[str] = mapped_column(ForeignKey("population_runs.id"), index=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), index=True)
    profession: Mapped[str] = mapped_column(String(40)); income: Mapped[float] = mapped_column(Float)
    price_sensitivity: Mapped[float] = mapped_column(Float); novelty_preference: Mapped[float] = mapped_column(Float)
    risk_preference: Mapped[float] = mapped_column(Float); beauty_affinity: Mapped[float] = mapped_column(Float)
    electronics_affinity: Mapped[float] = mapped_column(Float); grocery_affinity: Mapped[float] = mapped_column(Float)
class Edge(Base):
    __tablename__="customer_edges"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    population_id: Mapped[str] = mapped_column(ForeignKey("population_runs.id"), index=True)
    source_id: Mapped[str] = mapped_column(String(36), index=True); target_id: Mapped[str] = mapped_column(String(36), index=True)
    weight: Mapped[float] = mapped_column(Float); view: Mapped[str] = mapped_column(String(20)); reasons: Mapped[list] = mapped_column(JSON)
class Experiment(Base):
    __tablename__="experiments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    population_id: Mapped[str] = mapped_column(ForeignKey("population_runs.id"), index=True)
    name: Mapped[str] = mapped_column(String(160)); category: Mapped[str] = mapped_column(String(40))
    treatment_share: Mapped[float] = mapped_column(Float); seed: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    config: Mapped[dict] = mapped_column(JSON)
class Outcome(Base):
    __tablename__="experiment_outcomes"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    experiment_id: Mapped[str] = mapped_column(ForeignKey("experiments.id"), index=True)
    customer_id: Mapped[str] = mapped_column(String(36), index=True); arm: Mapped[str] = mapped_column(String(12))
    converted: Mapped[bool] = mapped_column(Boolean); revenue: Mapped[float] = mapped_column(Float)
class SegmentResult(Base):
    __tablename__="segment_results"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    experiment_id: Mapped[str] = mapped_column(ForeignKey("experiments.id"), index=True)
    segment: Mapped[str] = mapped_column(String(80)); control_rate: Mapped[float] = mapped_column(Float)
    treatment_rate: Mapped[float] = mapped_column(Float); uplift: Mapped[float] = mapped_column(Float); n: Mapped[int] = mapped_column(Integer)

app=FastAPI(title="Synthetic Experimentation Lab",version="1.0.0",description="Test experiments on a synthetic customer population before exposing real customers.")

class PopulationRequest(BaseModel):
    size:int=Field(1500,ge=100,le=10000); seed:int=42
class ExperimentRequest(BaseModel):
    population_id:str; name:str="Virtual Experiment"; category:str="Beauty"; treatment_share:float=Field(.5,gt=.1,lt=.9); seed:int=42

CITIES=[("Bengaluru","Karnataka",12.9716,77.5946),("Mumbai","Maharashtra",19.076,72.8777),("Delhi","Delhi",28.6139,77.209),("Hyderabad","Telangana",17.385,78.4867),("Chennai","Tamil Nadu",13.0827,80.2707),("Pune","Maharashtra",18.5204,73.8567),("Mangaluru","Karnataka",12.9141,74.856),("Kolkata","West Bengal",22.5726,88.3639)]
PROFESSIONS=["Engineer","Teacher","Finance","Healthcare","Business","Student","Government","Other"]

def sigmoid(x): return 1/(1+np.exp(-np.clip(x,-30,30)))

def make_population(size,seed):
    r=np.random.default_rng(seed); city_idx=r.choice(len(CITIES),size=size,p=[.20,.17,.14,.12,.11,.10,.06,.10])
    age=np.clip(r.normal(34,10,size),18,70).round().astype(int); gender=r.choice(["Female","Male"],size=size,p=[.48,.52])
    orders=np.maximum(0,r.poisson(np.clip(5.5-(age-35)*.02,1,8),size)); aov=np.round(np.exp(r.normal(np.log(1100),.45,size)),2)
    recency=np.clip(r.gamma(2.2,18,size),1,180).round().astype(int); sessions=np.maximum(1,r.poisson(7,size)); abandon=np.minimum(sessions,r.binomial(sessions,.28))
    device=r.choice(["Mobile","Desktop","Tablet"],size=size,p=[.68,.25,.07]); customer_type=np.where(orders>=10,"Loyal",np.where(orders>=3,"Repeat","New"))
    income=np.clip(r.lognormal(np.log(65000),.55,size),18000,500000); profession=r.choice(PROFESSIONS,size=size,p=[.20,.12,.12,.12,.15,.12,.09,.08])
    price=np.clip(r.beta(2.2,2.0,size),0,1); novelty=np.clip(r.beta(2,2,size),0,1); risk=np.clip(r.beta(2.5,2.5,size),0,1)
    beauty=np.clip(.45+.15*(gender=="Female")+.20*novelty-.10*price+r.normal(0,.12,size),0,1)
    electronics=np.clip(.40+.15*(gender=="Male")+.15*(age<35)+.15*r.beta(2,2,size),0,1)
    grocery=np.clip(.55+.10*(age>40)+.10*(income<70000)+r.normal(0,.08,size),0,1)
    rows=[]; truth=[]
    for i in range(size):
        city=CITIES[city_idx[i]]; cid=str(uuid.uuid4())
        rows.append({"id":cid,"population_id":"","age":int(age[i]),"gender":gender[i],"city":city[0],"state":city[1],"lat":float(city[2]+r.normal(0,.035)),"lon":float(city[3]+r.normal(0,.035)),"device":device[i],"customer_type":customer_type[i],"orders":int(orders[i]),"aov":float(aov[i]),"recency_days":int(recency[i]),"sessions_30d":int(sessions[i]),"cart_abandonments":int(abandon[i])})
        truth.append({"id":str(uuid.uuid4()),"customer_id":cid,"profession":profession[i],"income":float(income[i]),"price_sensitivity":float(price[i]),"novelty_preference":float(novelty[i]),"risk_preference":float(risk[i]),"beauty_affinity":float(beauty[i]),"electronics_affinity":float(electronics[i]),"grocery_affinity":float(grocery[i])})
    return rows,truth

def similarity_edges(customers,truths,view="observable",max_edges_per_node=8):
    rng=np.random.default_rng(11); by_city={}
    for i,c in enumerate(customers): by_city.setdefault(c["city"],[]).append(i)
    edges=[]
    for i,c in enumerate(customers):
        candidates=by_city[c["city"]].copy(); rng.shuffle(candidates); scores=[]
        for j in candidates[:50]:
            if i==j: continue
            o=customers[j]; score=0.0
            if c["gender"]==o["gender"]: score+=.22
            if c["device"]==o["device"]: score+=.10
            score+=.18*math.exp(-abs(c["age"]-o["age"])/12)
            score+=.18*math.exp(-abs(c["aov"]-o["aov"])/800)
            score+=.17*math.exp(-abs(c["recency_days"]-o["recency_days"])/45)
            score+=.15*math.exp(-abs(c["sessions_30d"]-o["sessions_30d"])/8)
            if view=="truth":
                a,b=truths[i],truths[j]; score+=.30*math.exp(-abs(a["price_sensitivity"]-b["price_sensitivity"])); score+=.20*math.exp(-abs(a["novelty_preference"]-b["novelty_preference"]))
            if score>=.52: scores.append((score,j))
        scores.sort(reverse=True)
        for score,j in scores[:max_edges_per_node]:
            reasons=["same city"]
            if c["gender"]==customers[j]["gender"]: reasons.append("same gender")
            if c["device"]==customers[j]["device"]: reasons.append("same device")
            if abs(c["age"]-customers[j]["age"])<7: reasons.append("similar age")
            if view=="truth": reasons.append("hidden behavioral similarity")
            edges.append((i,j,float(min(score,1)),reasons))
    return edges

def diff_ci(control_n,control_converted,treatment_n,treatment_converted):
    pc=control_converted/control_n if control_n else 0; pt=treatment_converted/treatment_n if treatment_n else 0; diff=pt-pc
    se=math.sqrt(max(pc*(1-pc)/control_n+pt*(1-pt)/treatment_n,1e-12))
    return diff,diff-1.96*se,diff+1.96*se

def population_rows(db,population_id):
    rows=db.query(Customer).filter(Customer.population_id==population_id).all()
    if not rows: raise HTTPException(404,"Population not found")
    return rows

@app.on_event("startup")
def startup(): Base.metadata.create_all(engine)

@app.get("/health")
def health(): return {"status":"ok","service":"synthetic-experimentation-lab"}

@app.post("/population/generate")
def generate_population(req:PopulationRequest):
    population_id=str(uuid.uuid4()); rows,truth=make_population(req.size,req.seed)
    for row in rows: row["population_id"]=population_id
    db=SessionLocal()
    try:
        db.add(Population(id=population_id,seed=req.seed,size=req.size,config={"observable_fields":["age","gender","city","state","device","customer_type","orders","aov","recency_days","sessions_30d","cart_abandonments"],"hidden_fields":["profession","income","price_sensitivity","novelty_preference","risk_preference","category_affinity"]}))
        db.add_all([Customer(**row) for row in rows])
        db.add_all([Truth(id=item["id"],population_id=population_id,**{k:v for k,v in item.items() if k!="id"}) for item in truth])
        for view in ("observable","truth"):
            for i,j,weight,reasons in similarity_edges(rows,truth,view):
                db.add(Edge(id=str(uuid.uuid4()),population_id=population_id,source_id=rows[i]["id"],target_id=rows[j]["id"],weight=weight,view=view,reasons=reasons))
        db.commit()
    except Exception:
        db.rollback(); raise
    finally: db.close()
    return {"population_id":population_id,"size":req.size,"seed":req.seed,"message":"Synthetic population created. Hidden variables remain simulator-internal."}

@app.get("/population/{population_id}")
def get_population(population_id:str,limit:int=100):
    db=SessionLocal()
    try:
        rows=population_rows(db,population_id); fields=["age","gender","city","state","lat","lon","device","customer_type","orders","aov","recency_days","sessions_30d","cart_abandonments"]
        return {"population_id":population_id,"rows":[{field:getattr(row,field) for field in fields} for row in rows[:limit]]}
    finally: db.close()

@app.get("/network")
def get_network(population_id:str,view:str="observable",limit:int=2500):
    if view not in ("observable","truth"): raise HTTPException(400,"view must be observable or truth")
    db=SessionLocal()
    try:
        edges=db.query(Edge).filter(Edge.population_id==population_id,Edge.view==view).limit(limit).all()
        return {"population_id":population_id,"view":view,"semantic":"Edges are measurable evidence of similarity; no edge does not imply dissimilarity.","edges":[{"source":e.source_id,"target":e.target_id,"weight":e.weight,"reasons":e.reasons} for e in edges]}
    finally: db.close()

@app.get("/graph/analytics")
def graph_analytics(population_id:str,view:str="observable"):
    if view not in ("observable","truth"): raise HTTPException(400,"view must be observable or truth")
    db=SessionLocal()
    try:
        edges=db.query(Edge).filter(Edge.population_id==population_id,Edge.view==view).all(); graph=nx.DiGraph()
        graph.add_weighted_edges_from([(e.source_id,e.target_id,e.weight) for e in edges])
        if not graph: return {"nodes":0,"edges":0,"density":0}
        pagerank=nx.pagerank(graph,weight="weight"); degree=dict(graph.degree()); top=sorted(pagerank.items(),key=lambda x:x[1],reverse=True)[:10]
        return {"nodes":graph.number_of_nodes(),"edges":graph.number_of_edges(),"density":nx.density(graph),"top_influence":[{"customer_id":node,"pagerank":score,"degree":degree[node]} for node,score in top],"note":"Influence here means graph centrality, not causal influence."}
    finally: db.close()

@app.post("/experiments/simulate")
def simulate_experiment(req:ExperimentRequest):
    db=SessionLocal()
    try:
        customers=population_rows(db,req.population_id); truth={item.customer_id:item for item in db.query(Truth).filter(Truth.population_id==req.population_id).all()}
        if not truth: raise HTTPException(404,"Simulator truth not found")
        experiment_id=str(uuid.uuid4())
        db.add(Experiment(id=experiment_id,population_id=req.population_id,name=req.name,category=req.category,treatment_share=req.treatment_share,seed=req.seed,config={"warning":"Synthetic simulation; validate with a real-world pilot.","hidden_variables_used":True}))
        rng=np.random.default_rng(req.seed); order=rng.permutation(len(customers)); treated=set(order[:int(len(customers)*req.treatment_share)])
        category_config={"Beauty":("beauty_affinity",.10),"Electronics":("electronics_affinity",.08),"Grocery":("grocery_affinity",.06)}
        affinity_field,base_effect=category_config.get(req.category,category_config["Beauty"]); outcomes=[]; segment_values={}
        for i,customer in enumerate(customers):
            hidden=truth[customer.id]; affinity=getattr(hidden,affinity_field)
            baseline=-2.05+.18*math.log1p(customer.orders)+.08*customer.sessions_30d-.012*customer.recency_days-.55*hidden.price_sensitivity+.30*affinity
            treatment_effect=base_effect*(.65+.9*affinity)*(1-.45*hidden.price_sensitivity)+.035*hidden.novelty_preference
            if req.category=="Beauty" and customer.gender=="Female": treatment_effect*=1.22
            probability=float(sigmoid(baseline+(treatment_effect if i in treated else 0))); converted=bool(rng.random()<probability)
            outcomes.append(Outcome(id=str(uuid.uuid4()),experiment_id=experiment_id,customer_id=customer.id,arm="treatment" if i in treated else "control",converted=converted,revenue=float(customer.aov if converted else 0)))
            for segment in (customer.gender,customer.customer_type): segment_values.setdefault(segment,[]).append((i in treated,converted))
        db.add_all(outcomes); db.flush()
        control=[o for o in outcomes if o.arm=="control"]; treatment=[o for o in outcomes if o.arm=="treatment"]; cc=sum(o.converted for o in control); tc=sum(o.converted for o in treatment)
        absolute_uplift,ci_low,ci_high=diff_ci(len(control),cc,len(treatment),tc); segment_rows=[]
        for segment,values in segment_values.items():
            if len(values)<30: continue
            cv=[converted for is_treatment,converted in values if not is_treatment]; tv=[converted for is_treatment,converted in values if is_treatment]
            if not cv or not tv: continue
            cr=sum(cv)/len(cv); tr=sum(tv)/len(tv); segment_rows.append(SegmentResult(id=str(uuid.uuid4()),experiment_id=experiment_id,segment=segment,control_rate=cr,treatment_rate=tr,uplift=tr-cr,n=len(values)))
        db.add_all(segment_rows); db.commit()
        cr=cc/len(control); tr=tc/len(treatment)
        return {"experiment_id":experiment_id,"population_id":req.population_id,"control":{"n":len(control),"conversion_rate":cr},"treatment":{"n":len(treatment),"conversion_rate":tr},"absolute_uplift":absolute_uplift,"relative_uplift":absolute_uplift/cr if cr else None,"ci_95":[ci_low,ci_high],"revenue_control":sum(o.revenue for o in control),"revenue_treatment":sum(o.revenue for o in treatment),"segments":[{"segment":row.segment,"control_rate":row.control_rate,"treatment_rate":row.treatment_rate,"uplift":row.uplift,"n":row.n} for row in segment_rows],"interpretation":"The interval captures randomization/sampling variability in the synthetic run, not uncertainty in the simulator assumptions."}
    except Exception:
        db.rollback(); raise
    finally: db.close()

@app.get("/experiments")
def list_experiments(limit:int=20):
    db=SessionLocal()
    try:
        rows=db.query(Experiment).order_by(Experiment.created_at.desc()).limit(limit).all()
        return [{"experiment_id":row.id,"name":row.name,"category":row.category,"population_id":row.population_id,"seed":row.seed,"created_at":row.created_at} for row in rows]
    finally: db.close()

@app.get("/experiments/{experiment_id}")
def get_experiment(experiment_id:str):
    db=SessionLocal()
    try:
        experiment=db.get(Experiment,experiment_id)
        if not experiment: raise HTTPException(404,"Experiment not found")
        segments=db.query(SegmentResult).filter(SegmentResult.experiment_id==experiment_id).all()
        outcomes=db.query(Outcome).filter(Outcome.experiment_id==experiment_id).count()
        return {"experiment_id":experiment.id,"name":experiment.name,"category":experiment.category,"population_id":experiment.population_id,"seed":experiment.seed,"segments":[{"segment":row.segment,"control_rate":row.control_rate,"treatment_rate":row.treatment_rate,"uplift":row.uplift,"n":row.n} for row in segments],"outcome_count":outcomes}
    finally: db.close()
