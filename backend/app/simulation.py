import uuid, math
from dataclasses import dataclass
import numpy as np

CITIES=[("Bengaluru","Karnataka",12.9716,77.5946),("Mumbai","Maharashtra",19.076,72.8777),("Delhi","Delhi",28.6139,77.209),("Hyderabad","Telangana",17.385,78.4867),("Chennai","Tamil Nadu",13.0827,80.2707),("Pune","Maharashtra",18.5204,73.8567),("Mangaluru","Karnataka",12.9141,74.856),("Kolkata","West Bengal",22.5726,88.3639)]
PROFESSIONS=["Engineer","Teacher","Finance","Healthcare","Business","Student","Government","Other"]

@dataclass
class Population:
    customers:list[dict]
    truth:list[dict]

def sigmoid(x):
    return float(1/(1+np.exp(-np.clip(x,-30,30))))

def generate_population(size,seed):
    r=np.random.default_rng(seed)
    city_idx=r.choice(len(CITIES),size=size,p=[.20,.17,.14,.12,.11,.10,.06,.10])
    age=np.clip(r.normal(34,10,size),18,70).round().astype(int)
    gender=r.choice(["Female","Male"],size=size,p=[.48,.52])
    orders=r.poisson(np.clip(5.5-(age-35)*.02,1,8),size)
    aov=np.round(np.exp(r.normal(np.log(1100),.45,size)),2)
    recency=np.clip(r.gamma(2.2,18,size),1,180).round().astype(int)
    sessions=np.maximum(1,r.poisson(7,size))
    abandon=np.minimum(sessions,r.binomial(sessions,.28))
    device=r.choice(["Mobile","Desktop","Tablet"],size=size,p=[.68,.25,.07])
    customer_type=np.where(orders>=10,"Loyal",np.where(orders>=3,"Repeat","New"))
    income=np.clip(r.lognormal(np.log(65000),.55,size),18000,500000)
    profession=r.choice(PROFESSIONS,size=size,p=[.20,.12,.12,.12,.15,.12,.09,.08])
    price=r.beta(2.2,2.0,size); novelty=r.beta(2,2,size); risk=r.beta(2.5,2.5,size)
    beauty=np.clip(.45+.15*(gender=="Female")+.20*novelty-.10*price+r.normal(0,.12,size),0,1)
    electronics=np.clip(.40+.15*(gender=="Male")+.15*(age<35)+.15*r.beta(2,2,size),0,1)
    grocery=np.clip(.55+.10*(age>40)+.10*(income<70000)+r.normal(0,.08,size),0,1)
    customers=[]; truth=[]
    for i in range(size):
        city=CITIES[city_idx[i]]; cid=str(uuid.uuid4())
        customers.append({"id":cid,"age":int(age[i]),"gender":str(gender[i]),"city":city[0],"state":city[1],"lat":float(city[2]+r.normal(0,.035)),"lon":float(city[3]+r.normal(0,.035)),"device":str(device[i]),"customer_type":str(customer_type[i]),"orders":int(orders[i]),"aov":float(aov[i]),"recency_days":int(recency[i]),"sessions_30d":int(sessions[i]),"cart_abandonments":int(abandon[i])})
        truth.append({"id":str(uuid.uuid4()),"customer_id":cid,"profession":str(profession[i]),"income":float(income[i]),"price_sensitivity":float(price[i]),"novelty_preference":float(novelty[i]),"risk_preference":float(risk[i]),"beauty_affinity":float(beauty[i]),"electronics_affinity":float(electronics[i]),"grocery_affinity":float(grocery[i])})
    return Population(customers,truth)

def build_similarity_edges(customers,truth,view,max_edges_per_node=8):
    by_city={}
    for i,c in enumerate(customers): by_city.setdefault(c["city"],[]).append(i)
    truth_by_customer={t["customer_id"]:t for t in truth}
    rng=np.random.default_rng(11); edges=[]
    for i,c in enumerate(customers):
        candidates=by_city[c["city"]].copy(); rng.shuffle(candidates); scores=[]
        for j in candidates[:60]:
            if i==j: continue
            o=customers[j]
            score=.22*(c["gender"]==o["gender"])+.10*(c["device"]==o["device"])
            score+=.18*math.exp(-abs(c["age"]-o["age"])/12)+.18*math.exp(-abs(c["aov"]-o["aov"])/800)
            score+=.17*math.exp(-abs(c["recency_days"]-o["recency_days"])/45)+.15*math.exp(-abs(c["sessions_30d"]-o["sessions_30d"])/8)
            if view=="truth":
                a=truth_by_customer[c["id"]]; b=truth_by_customer[o["id"]]
                score+=.30*math.exp(-abs(a["price_sensitivity"]-b["price_sensitivity"]))+.20*math.exp(-abs(a["novelty_preference"]-b["novelty_preference"]))
            if score>=.52: scores.append((float(min(score,1)),j))
        for score,j in sorted(scores,reverse=True)[:max_edges_per_node]:
            reasons=["same city"]
            if c["gender"]==customers[j]["gender"]: reasons.append("same gender")
            if c["device"]==customers[j]["device"]: reasons.append("same device")
            if abs(c["age"]-customers[j]["age"])<7: reasons.append("similar age")
            if view=="truth": reasons.append("hidden behavioral similarity")
            edges.append({"id":str(uuid.uuid4()),"source_id":c["id"],"target_id":customers[j]["id"],"weight":score,"view":view,"reasons":reasons})
    return edges

def simulate_outcomes(customers,truth_by_customer,category,treatment_share,seed):
    rng=np.random.default_rng(seed); n=len(customers); treated=set(rng.permutation(n)[:int(n*treatment_share)])
    fields={"Beauty":("beauty_affinity",.10),"Electronics":("electronics_affinity",.08),"Grocery":("grocery_affinity",.06)}
    field,base=fields.get(category,fields["Beauty"]); outcomes=[]; segments={}
    for i,c in enumerate(customers):
        h=truth_by_customer[c["id"]]; affinity=h[field]
        baseline=-2.05+.18*np.log1p(c["orders"])+.08*c["sessions_30d"]-.012*c["recency_days"]-.55*h["price_sensitivity"]+.30*affinity
        effect=base*(.65+.9*affinity)*(1-.45*h["price_sensitivity"])+.035*h["novelty_preference"]
        if category=="Beauty" and c["gender"]=="Female": effect*=1.22
        converted=bool(rng.random()<sigmoid(baseline+(effect if i in treated else 0)))
        arm="treatment" if i in treated else "control"
        outcomes.append({"customer_id":c["id"],"arm":arm,"converted":converted,"revenue":float(c["aov"] if converted else 0)})
        for segment in (c["gender"],c["customer_type"]): segments.setdefault(segment,[]).append((arm,converted))
    return outcomes,segments
