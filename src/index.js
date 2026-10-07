const HTML = "<!doctype html>\n<html>\n<head>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n<title>Synthetic Experimentation Lab</title>\n<link rel=\"stylesheet\" href=\"https://unpkg.com/leaflet@1.9.4/dist/leaflet.css\">\n<style>\n:root{--bg:#07111f;--panel:#101c2f;--panel2:#0b1627;--border:#213652;--text:#eaf2ff;--muted:#8fa3bd;--accent:#4f9cff;--green:#55d98b;--yellow:#ffd166;--red:#ff7180}\n*{box-sizing:border-box}body{font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif;background:radial-gradient(circle at 20% 0%,#102643 0,#07111f 42%);color:var(--text);margin:0}\nheader{padding:30px 24px;border-bottom:1px solid var(--border);background:rgba(7,17,31,.92);position:sticky;top:0;z-index:20;backdrop-filter:blur(12px)}\nheader h1{margin:0 0 7px;font-size:28px}header p{margin:0;color:var(--muted);max-width:850px;line-height:1.5}\nmain{max-width:1500px;margin:auto;padding:18px}.tabs{display:flex;gap:8px;flex-wrap:wrap;margin:4px 0 18px}.tab{padding:10px 15px}.tab.active{background:var(--accent)}\nsection{display:none}.card{background:linear-gradient(180deg,rgba(16,28,47,.96),rgba(11,22,39,.96));border:1px solid var(--border);border-radius:16px;padding:18px;margin:12px 0;box-shadow:0 14px 30px rgba(0,0,0,.12)}\n.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.grid2{display:grid;grid-template-columns:1.2fr .8fr;gap:12px}.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}\n.kpi{font-size:28px;font-weight:750;margin-top:5px}.label{color:var(--muted);font-size:13px}.muted{color:var(--muted)}.small{font-size:12px;line-height:1.5}\nbutton,select,input{padding:10px 12px;border-radius:9px;border:1px solid #2b4667;background:#0a1728;color:var(--text);margin:4px}button{cursor:pointer}button:hover{border-color:#4f9cff}.primary{background:#256bc9;border-color:#327bdc}.danger{background:#57212b}.pill{display:inline-block;border:1px solid var(--border);border-radius:999px;padding:5px 9px;margin:2px;color:#b9d4f4}\ntable{width:100%;border-collapse:collapse}th,td{padding:9px;border-bottom:1px solid #20324d;text-align:left;font-size:12px}th{color:#a9bdd6;position:sticky;top:0;background:#101c2f}\n.tablewrap{max-height:420px;overflow:auto;border:1px solid var(--border);border-radius:10px}.good{color:var(--green)}.warn{color:var(--yellow)}.bad{color:var(--red)}\n.callout{border-left:3px solid var(--accent);padding:12px 14px;background:#0a182b;border-radius:8px;margin:10px 0}.warning{border-left-color:var(--yellow)}\n#map{height:500px;border-radius:12px;overflow:hidden}.network{height:500px;overflow:auto;background:#081321;border:1px solid var(--border);border-radius:12px}.network svg{width:100%;height:100%;min-width:900px}\nsvg line{stroke:#37516f;stroke-opacity:.5}svg circle{stroke:#dcecff;stroke-width:1.2}\n.hero{display:flex;justify-content:space-between;gap:18px;align-items:flex-start}.hero h2{margin:0 0 7px}.hero .badge{padding:7px 10px;border-radius:9px;background:#102846;border:1px solid #2b4c70;color:#b9d7f8}\n.metric{background:#0b1728;border:1px solid var(--border);border-radius:12px;padding:13px}\nform .row{display:flex;flex-wrap:wrap;gap:4px;align-items:center}\n@media(max-width:1000px){.grid{grid-template-columns:repeat(2,1fr)}.grid2,.grid3{grid-template-columns:1fr}}\n@media(max-width:600px){.grid{grid-template-columns:1fr}header h1{font-size:23px}}\n</style>\n</head>\n<body>\n<header>\n  <h1>Synthetic Experimentation Lab</h1>\n  <p>Build a virtual customer population, run an experiment on it, and inspect the simulated result before exposing real customers.</p>\n</header>\n<main>\n<nav class=\"tabs\">\n <button class=\"tab active\" data-tab=\"lab\">Experiment Lab</button>\n <button class=\"tab\" data-tab=\"population\">Population</button>\n <button class=\"tab\" data-tab=\"network\">Observable Network</button>\n <button class=\"tab\" data-tab=\"truth\">Simulator Truth</button>\n <button class=\"tab\" data-tab=\"history\">History</button>\n</nav>\n\n<section id=\"lab\" style=\"display:block\">\n <div class=\"hero card\">\n  <div><h2>1. Design a virtual experiment</h2><p class=\"muted\">The company defines the scenario. The simulator supplies a synthetic population and heterogeneous responses.</p></div>\n  <div class=\"badge\">No real customers are contacted</div>\n </div>\n <div class=\"grid\">\n  <div class=\"metric\"><div class=\"label\">Synthetic customers</div><div id=\"kc\" class=\"kpi\">—</div></div>\n  <div class=\"metric\"><div class=\"label\">Observable relationships</div><div id=\"ke\" class=\"kpi\">—</div></div>\n  <div class=\"metric\"><div class=\"label\">Cities represented</div><div id=\"kcity\" class=\"kpi\">—</div></div>\n  <div class=\"metric\"><div class=\"label\">Last simulated uplift</div><div id=\"ku\" class=\"kpi\">—</div></div>\n </div>\n <div class=\"grid2\">\n  <div class=\"card\">\n   <h3>Experiment setup</h3>\n   <div class=\"row\">\n    <label class=\"small\">Scenario\n      <select id=\"et\"><option>UI/UX</option><option>Advertisement</option><option>Discount</option><option>Product launch</option><option>Recommendation</option><option>Shipping</option></select>\n    </label>\n    <label class=\"small\">Category\n      <select id=\"cat\"><option>Fashion</option><option>Beauty</option><option>Electronics</option><option>Grocery</option><option>Home</option><option>Sports</option></select>\n    </label>\n    <label class=\"small\">Treatment share\n      <select id=\"share\"><option value=\"0.5\">50%</option><option value=\"0.2\">20%</option><option value=\"0.3\">30%</option><option value=\"0.7\">70%</option></select>\n    </label>\n   </div>\n   <button id=\"runexp\" class=\"primary\">Run virtual experiment</button>\n   <button id=\"gen\" class=\"primary\">Generate 1,500 customers</button>\n   <span id=\"status\" class=\"muted\"></span>\n   <div class=\"callout small\">A simulated uplift is evidence under the simulator's assumptions. It is not a guarantee of real-world treatment effectiveness.</div>\n  </div>\n  <div class=\"card\">\n   <h3>What is being tested?</h3>\n   <div id=\"setupText\" class=\"muted\">Choose a scenario and category. The simulator will create control and treatment outcomes.</div>\n  </div>\n </div>\n <div class=\"card\"><h3>Virtual experiment result</h3><div id=\"out\" class=\"muted\">Run an experiment to see the result.</div></div>\n</section>\n\n<section id=\"population\">\n <div class=\"hero card\"><div><h2>Synthetic population</h2><p class=\"muted\">These are the fields a company can reasonably use for the virtual experiment.</p></div><button id=\"regen\" class=\"primary\">Generate population</button></div>\n <div class=\"callout\"><b>Privacy boundary:</b> hidden simulator variables such as income, profession, price sensitivity, novelty preference and risk preference are not exposed here.</div>\n <div class=\"grid2\">\n  <div class=\"card\"><h3>Customer locations</h3><div id=\"map\"></div></div>\n  <div class=\"card\"><h3>Observable customer sample</h3><div id=\"popout\" class=\"tablewrap\"></div></div>\n </div>\n</section>\n\n<section id=\"network\">\n <div class=\"hero card\"><div><h2>Observable similarity network</h2><p class=\"muted\">An edge means we found measurable evidence of similarity. No edge does not mean no similarity.</p></div><button id=\"loadnet\" class=\"primary\">Build network</button></div>\n <div class=\"grid3\">\n  <div class=\"metric\"><div class=\"label\">Nodes</div><div id=\"nn\" class=\"kpi\">—</div></div>\n  <div class=\"metric\"><div class=\"label\">Measured edges</div><div id=\"ne\" class=\"kpi\">—</div></div>\n  <div class=\"metric\"><div class=\"label\">Interpretation</div><div class=\"small\">Partial measurement of population structure</div></div>\n </div>\n <div class=\"grid2\">\n  <div class=\"card\"><div id=\"networkSvg\" class=\"network\"></div></div>\n  <div class=\"card\"><h3>Relationship evidence</h3><div id=\"netout\" class=\"tablewrap\"></div></div>\n </div>\n</section>\n\n<section id=\"truth\">\n <div class=\"hero card\"><div><h2>Simulator truth</h2><p class=\"muted\">Internal diagnostic view. Hidden variables are used by the simulator but are not company-observable customer data.</p></div></div>\n <div class=\"callout warning\"><b>Do not interpret this as company knowledge.</b> This view exists so the lab can compare observable structure with the simulator's underlying synthetic structure.</div>\n <div class=\"grid3\">\n  <div class=\"metric\"><div class=\"label\">Ground-truth relationships</div><div id=\"tn\" class=\"kpi\">—</div></div>\n  <div class=\"metric\"><div class=\"label\">Additional relationship evidence</div><div id=\"te\" class=\"kpi\">—</div></div>\n  <div class=\"metric\"><div class=\"label\">Hidden structure</div><div class=\"small\">Profession, income and latent behavioural preferences</div></div>\n </div>\n <div class=\"card\"><div id=\"truthout\" class=\"tablewrap\"></div></div>\n</section>\n\n<section id=\"history\">\n <div class=\"hero card\"><div><h2>Experiment history</h2><p class=\"muted\">Previous virtual experiments run against the synthetic population.</p></div><button id=\"loadhist\" class=\"primary\">Refresh history</button></div>\n <div class=\"card\"><div id=\"histout\" class=\"tablewrap\"></div></div>\n</section>\n</main>\n\n<script src=\"https://unpkg.com/leaflet@1.9.4/dist/leaflet.js\"></script>\n<script>\nconst $=id=>document.getElementById(id);\nconst esc=x=>String(x??'').replace(/[&<>\"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[m]));\nasync function api(u,o){const r=await fetch(u,o);let d={};try{d=await r.json()}catch{}if(!r.ok)throw Error(d.error||('HTTP '+r.status));return d}\ndocument.querySelectorAll('.tab').forEach(b=>b.onclick=()=>{document.querySelectorAll('section').forEach(s=>s.style.display='none');document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));$(b.dataset.tab).style.display='block';b.classList.add('active');if(b.dataset.tab==='population')loadPopulation();if(b.dataset.tab==='history')loadHistory()});\nasync function stats(){try{const s=await api('/api/stats');$('kc').textContent=s.customers.toLocaleString();$('ke').textContent=s.observable_edges.toLocaleString();$('kcity').textContent=s.cities}catch{}}\nfunction setupText(){const e=$('et').value,c=$('cat').value;const labels={Discount:'A discount or price incentive',Advertisement:'A new advertising treatment',UIUX:'A different customer interface',Recommendation:'A different recommendation experience','Product launch':'A new product experience',Shipping:'A different shipping experience'};const l=labels[e]||e;$('setupText').innerHTML='<b>'+esc(l)+'</b> for <b>'+esc(c)+'</b>. The simulator randomly assigns customers to control/treatment and generates noisy heterogeneous responses.'}\n$('et').onchange=setupText;$('cat').onchange=setupText;setupText();\n\n$('gen').onclick=generate;$('regen').onclick=generate;\nasync function generate(){try{$('status').textContent='Generating synthetic population...';const r=await api('/api/population/generate',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({n:1500})});$('status').textContent='Generated '+r.customers.toLocaleString()+' customers and '+r.observable_edges.toLocaleString()+' observable relationships';await stats();await loadPopulation()}catch(e){$('status').textContent=e.message}}\n\n$('runexp').onclick=async()=>{try{const r=await api('/api/experiments/simulate',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({experiment_type:$('et').value,category:$('cat').value,treatment_share:Number($('share').value)})});$('ku').textContent=(r.absolute_uplift*100).toFixed(2)+' pp';$('out').innerHTML='<div class=\"grid3\"><div class=\"metric\"><div class=\"label\">Control conversion</div><div class=\"kpi\">'+(r.control_rate*100).toFixed(2)+'%</div></div><div class=\"metric\"><div class=\"label\">Treatment conversion</div><div class=\"kpi\">'+(r.treatment_rate*100).toFixed(2)+'%</div></div><div class=\"metric\"><div class=\"label\">Absolute uplift</div><div class=\"kpi good\">'+(r.absolute_uplift*100).toFixed(2)+' pp</div></div></div><p><b>Relative uplift:</b> '+(r.relative_uplift*100).toFixed(2)+'% &nbsp; <b>Approx. 95% CI:</b> ['+(r.ci_low*100).toFixed(2)+' pp, '+(r.ci_high*100).toFixed(2)+' pp]</p><p><b>Simulated revenue difference:</b> '+Number(r.revenue_uplift).toLocaleString(undefined,{maximumFractionDigits:0})+'</p><div class=\"callout small\">'+esc(r.interpretation)+'</div>'>;await stats();}catch(e){$('out').textContent=e.message}};\n\nlet map,markers=[];\nasync function loadPopulation(){try{const r=await api('/api/network?mode=observable');$('popout').innerHTML='<table><tr><th>ID</th><th>Age</th><th>Gender</th><th>City</th><th>Device</th><th>Type</th><th>Orders</th></tr>'+r.nodes.slice(0,150).map(c=>'<tr><td>'+esc(c.customer_id)+'</td><td>'+c.age+'</td><td>'+esc(c.gender)+'</td><td>'+esc(c.city)+'</td><td>'+esc(c.device)+'</td><td>'+esc(c.customer_type)+'</td><td>'+c.orders+'</td></tr>').join('')+'</table>';if(!map){map=L.map('map').setView([21,79],5);L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{attribution:'© OpenStreetMap contributors'}).addTo(map)}markers.forEach(m=>m.remove());markers=[];r.nodes.slice(0,500).forEach(c=>markers.push(L.circleMarker([c.lat,c.lon],{radius:4,weight:1,fillOpacity:.55}).bindPopup('<b>'+esc(c.customer_id)+'</b><br>'+esc(c.city)+' · '+esc(c.device)+'<br>'+esc(c.customer_type)).addTo(map)));if(r.nodes.length){const b=L.latLngBounds(r.nodes.slice(0,500).map(c=>[c.lat,c.lon]));map.fitBounds(b.pad(.15))}}catch(e){$('popout').textContent=e.message}}\nfunction graphSvg(nodes,edges){const ns=nodes.slice(0,140),ids=new Set(ns.map(n=>n.customer_id)),es=edges.filter(e=>ids.has(e.a)&&ids.has(e.b)).slice(0,500);const w=900,h=480,pts=new Map();ns.forEach((n,i)=>{const a=i/ns.length*Math.PI*2;pts.set(n.customer_id,[w/2+Math.cos(a)*(w*.36),h/2+Math.sin(a)*(h*.38)])});const lines=es.map(e=>{const a=pts.get(e.a),b=pts.get(e.b);return a&&b?'<line x1=\"'+a[0]+'\" y1=\"'+a[1]+'\" x2=\"'+b[0]+'\" y2=\"'+b[1]+'\" stroke-width=\"'+Math.max(1,e.weight*5)+'\"/>':''}).join('');const circles=ns.map(n=>{const p=pts.get(n.customer_id);return '<circle cx=\"'+p[0]+'\" cy=\"'+p[1]+'\" r=\"5\" fill=\"'+(n.degree>6?'#55d98b':'#4f9cff')+'\"><title>'+esc(n.customer_id)+' · '+n.degree+' measured relationships</title></circle>'}).join('');return '<svg viewBox=\"0 0 '+w+' '+h+'\">'+lines+circles+'</svg>'}\n$('loadnet').onclick=async()=>{try{const r=await api('/api/network?mode=observable');$('nn').textContent=r.nodes.length.toLocaleString();$('ne').textContent=r.edges.length.toLocaleString();$('networkSvg').innerHTML=graphSvg(r.nodes,r.edges);$('netout').innerHTML='<table><tr><th>Customer</th><th>Neighbour</th><th>Similarity evidence</th><th>Weight</th></tr>'+r.edges.slice(0,120).map(e=>'<tr><td>'+esc(e.a)+'</td><td>'+esc(e.b)+'</td><td>'+esc(e.reasons.replaceAll('_',' '))+'</td><td>'+Number(e.weight).toFixed(2)+'</td></tr>').join('')+'</table>'}catch(e){$('netout').textContent=e.message}};\n\n$('loadhist').onclick=loadHistory;\nasync function loadHistory(){try{const r=await api('/api/experiments');$('histout').innerHTML='<table><tr><th>ID</th><th>Scenario</th><th>Category</th><th>N</th><th>Control</th><th>Treatment</th><th>Uplift</th><th>95% CI</th></tr>'+r.experiments.map(x=>'<tr><td>'+x.id+'</td><td>'+esc(x.experiment_type)+'</td><td>'+esc(x.category)+'</td><td>'+x.sample_size.toLocaleString()+'</td><td>'+((x.conversion_rate_control||0)*100).toFixed(2)+'%</td><td>'+((x.conversion_rate_treatment||0)*100).toFixed(2)+'%</td><td class=\"good\">'+((x.absolute_uplift||0)*100).toFixed(2)+' pp</td><td>['+((x.ci_low||0)*100).toFixed(2)+', '+((x.ci_high||0)*100).toFixed(2)+'] pp</td></tr>').join('')+'</table>'}catch(e){$('histout').textContent=e.message}}\nasync function loadTruth(){try{const r=await api('/api/network?mode=ground_truth');const o=await api('/api/network?mode=observable');$('tn').textContent=r.edges.length.toLocaleString();$('te').textContent=Math.max(0,r.edges.length-o.edges.length).toLocaleString();$('truthout').innerHTML='<table><tr><th>Customer</th><th>Neighbour</th><th>Relationship evidence</th><th>Weight</th></tr>'+r.edges.filter(e=>/(profession|price_sensitivity|novelty|risk)/.test(e.reasons)).slice(0,180).map(e=>'<tr><td>'+esc(e.a)+'</td><td>'+esc(e.b)+'</td><td>'+esc(e.reasons.replaceAll('_',' '))+'</td><td>'+Number(e.weight).toFixed(2)+'</td></tr>').join('')+'</table>'}catch(e){$('truthout').textContent=e.message}}\ndocument.querySelector('[data-tab=\"truth\"]').onclick=async()=>{document.querySelectorAll('section').forEach(s=>s.style.display='none');document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));$('truth').style.display='block';document.querySelector('[data-tab=\"truth\"]').classList.add('active');await loadTruth()};\nstats();loadPopulation();loadHistory();\n</script>\n</body>\n</html>";

const cities={Mumbai:['Maharashtra',19.076,72.8777],Bengaluru:['Karnataka',12.9716,77.5946],Delhi:['Delhi',28.6139,77.209],Hyderabad:['Telangana',17.385,78.4867],Chennai:['Tamil Nadu',13.0827,80.2707],Kolkata:['West Bengal',22.5726,88.3639],Pune:['Maharashtra',18.5204,73.8567],Ahmedabad:['Gujarat',23.0225,72.5714],Jaipur:['Rajasthan',26.9124,75.7873],Lucknow:['Uttar Pradesh',26.8467,80.9462],Kochi:['Kerala',9.9312,76.2673],Indore:['Madhya Pradesh',22.7196,75.8577]};
const professions=['Software','Finance','Healthcare','Education','Retail','Manufacturing','Student','Consulting','Government'];
const devices=['Android','iPhone','Desktop'],genders=['Male','Female'],types=['New','Returning','Loyal','High Value'],cats=['Fashion','Beauty','Electronics','Grocery','Home','Sports'];

function rng(seed){let x=seed|0;return()=>{x|=0;x=Math.imul(x^x>>>15,1|x);x^=x+Math.imul(x^x>>>7,61|x);return((x^x>>>14)>>>0)/4294967296}}
function pick(r,a){return a[Math.floor(r()*a.length)]}
function clamp(x,a,b){return Math.max(a,Math.min(b,x))}
function customer(i,r){
 const city=pick(r,Object.keys(cities)),m=cities[city];
 const c={customer_id:'CUST-'+String(i+1).padStart(5,'0'),age:clamp(Math.round(34+11*(r()+r()+r()-1.5)*1.6),18,72),gender:pick(r,genders),state:m[0],city,lat:m[1]+(r()-.5)*.13,lon:m[2]+(r()-.5)*.13,device:pick(r,devices),customer_type:pick(r,types),orders:Math.max(0,Math.round(6+r()*10)),aov:Math.round(300+3000*r()),recency_days:Math.max(1,Math.round(90*r())),sessions_30d:Math.max(1,Math.round(3+18*r())),cart_abandonments:Math.round(6*r())};
 c.h={profession:pick(r,professions),income:15000+Math.round(r()*140000),affinity:pick(r,cats),price:r(),novelty:r(),risk:r()};
 return c
}

function similarity(a,b,truth){
 let w=0,r=[];
 if(a.device===b.device){w+=.22;r.push('device')}
 if(a.gender===b.gender){w+=.16;r.push('gender')}
 if(a.city===b.city){w+=.16;r.push('city')}
 if(a.state===b.state){w+=.08;r.push('state')}
 if(Math.floor(a.age/10)===Math.floor(b.age/10)){w+=.10;r.push('age_band')}
 if(a.customer_type===b.customer_type){w+=.08;r.push('customer_type')}
 if(truth){
  if(a.h.profession===b.h.profession){w+=.13;r.push('profession')}
  if(Math.abs(a.h.price-b.h.price)<.18){w+=.08;r.push('price_sensitivity')}
  if(Math.abs(a.h.novelty-b.h.novelty)<.18){w+=.06;r.push('novelty')}
  if(Math.abs(a.h.risk-b.h.risk)<.18){w+=.06;r.push('risk')}
 }
 return [w,r.join(',')]
}

function buildCandidatePairs(cs){
 const indexes={device:new Map(),gender:new Map(),city:new Map(),state:new Map(),age_band:new Map(),customer_type:new Map()};
 const add=(map,key,i)=>{if(!map.has(key))map.set(key,[]);map.get(key).push(i)};
 cs.forEach((c,i)=>{add(indexes.device,c.device,i);add(indexes.gender,c.gender,i);add(indexes.city,c.city,i);add(indexes.state,c.state,i);add(indexes.age_band,Math.floor(c.age/10),i);add(indexes.customer_type,c.customer_type,i)});
 const pairs=new Set();
 for(const map of Object.values(indexes))for(const arr of map.values())for(let x=0;x<arr.length;x++)for(let y=x+1;y<arr.length;y++){const a=arr[x],b=arr[y];pairs.add(a<b?a+'|'+b:b+'|'+a)}
 return [...pairs]
}

async function generate(env,n){
 await env.DB.prepare('DELETE FROM customer_edges').run();
 await env.DB.prepare('DELETE FROM graph_metrics').run();
 await env.DB.prepare('DELETE FROM customers').run();
 const r=rng(Date.now()&2147483647),cs=[];
 for(let i=0;i<n;i++)cs.push(customer(i,r));

 const candidates=buildCandidatePairs(cs),edges=[];
 for(const key of candidates){
  const [i,j]=key.split('|').map(Number),[w,reasons]=similarity(cs[i],cs[j],true);
  if(w>=.24)edges.push({a:cs[i],b:cs[j],w,reasons});
 }

 const ins=env.DB.prepare('INSERT INTO customers(customer_id,age,gender,state,city,lat,lon,device,customer_type,orders,aov,recency_days,sessions_30d,cart_abandonments) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)');
 for(const c of cs)await ins.bind(c.customer_id,c.age,c.gender,c.state,c.city,c.lat,c.lon,c.device,c.customer_type,c.orders,c.aov,c.recency_days,c.sessions_30d,c.cart_abandonments).run();

 const ei=env.DB.prepare('INSERT INTO customer_edges(customer_id,neighbor_id,weight,reasons) VALUES(?,?,?,?)');
 for(const e of edges){await ei.bind(e.a.customer_id,e.b.customer_id,e.w,e.reasons).run();await ei.bind(e.b.customer_id,e.a.customer_id,e.w,e.reasons).run()}

 await env.DB.prepare('INSERT INTO population_runs(created_at,population_size,observable_features,hidden_features,graph_definition) VALUES(?,?,?,?,?)')
  .bind(new Date().toISOString(),n,'age,gender,state,city,location,device,customer_type,orders,aov,recency_days,sessions_30d,cart_abandonments','profession,income,affinity,price_sensitivity,novelty,risk','edge = measurable similarity above threshold; no-edge does not imply dissimilarity').run();

 return {customers:n,observable_edges:edges.length*2,preview:cs.slice(0,50).map(({h,...x})=>x)};
}

async function network(env,mode){
 const cs=(await env.DB.prepare('SELECT * FROM customers LIMIT 5000').all()).results;
 let es=(await env.DB.prepare('SELECT customer_id a,neighbor_id b,weight,reasons FROM customer_edges LIMIT 30000').all()).results;
 if(mode==='observable')es=es.filter(e=>!/(profession|price_sensitivity|novelty|risk)/.test(e.reasons));
 const ids=new Set(cs.map(c=>c.customer_id));
 const degree=new Map(cs.map(c=>[c.customer_id,0]));
 for(const e of es)if(ids.has(e.a)&&ids.has(e.b))degree.set(e.a,(degree.get(e.a)||0)+1);
 return {mode,nodes:cs.map(c=>({...c,degree:degree.get(c.customer_id)||0})),edges:es};
}

async function graph(env,mode){
 const cs=(await env.DB.prepare('SELECT * FROM customers LIMIT 2000').all()).results;
 let es=(await env.DB.prepare('SELECT customer_id a,neighbor_id b,weight,reasons FROM customer_edges LIMIT 30000').all()).results;
 if(mode==='observable')es=es.filter(e=>!/(profession|price_sensitivity|novelty|risk)/.test(e.reasons));

 const ids=new Set(cs.map(c=>c.customer_id)),adj=new Map(cs.map(c=>[c.customer_id,[]]));
 for(const e of es)if(ids.has(e.a)&&ids.has(e.b))adj.get(e.a).push([e.b,e.weight]);

 const deg={},wd={};
 for(const c of cs){const z=adj.get(c.customer_id)||[];deg[c.customer_id]=z.length;wd[c.customer_id]=z.reduce((s,x)=>s+x[1],0)}

 let pr=Object.fromEntries(cs.map(c=>[c.customer_id,1/Math.max(cs.length,1)]));
 for(let it=0;it<12;it++){
  const nx=Object.fromEntries(cs.map(c=>[c.customer_id,.15/Math.max(cs.length,1)]));
  for(const c of cs){const z=adj.get(c.customer_id),sum=z.reduce((s,x)=>s+x[1],0)||1;for(const [v,w] of z)nx[v]+=.85*pr[c.customer_id]*w/sum}
  pr=nx;
 }

 let lab=Object.fromEntries(cs.map((c,i)=>[c.customer_id,i]));
 for(let it=0;it<6;it++)for(const c of cs){const q={};for(const [v,w] of adj.get(c.customer_id)){const k=lab[v];q[k]=(q[k]||0)+w}const best=Object.entries(q).sort((a,b)=>b[1]-a[1])[0];if(best)lab[c.customer_id]=+best[0]}

 const rem={},cnt={},metrics=[];let nc=0;
 for(const c of cs){const old=lab[c.customer_id];if(rem[old]===undefined)rem[old]=nc++;lab[c.customer_id]=rem[old];cnt[lab[c.customer_id]]=(cnt[lab[c.customer_id]]||0)+1}

 const md=Math.max(...Object.values(deg),1),mp=Math.max(...Object.values(pr),1e-9);
 for(const c of cs)metrics.push({customer_id:c.customer_id,degree:deg[c.customer_id],weighted_degree:wd[c.customer_id],pagerank:pr[c.customer_id],community_id:lab[c.customer_id],influence_score:.55*pr[c.customer_id]/mp+.45*deg[c.customer_id]/md});
 metrics.sort((a,b)=>b.influence_score-a.influence_score);

 const leaders=metrics.slice(0,20);
 await env.DB.prepare('DELETE FROM graph_metrics').run();
 const ins=env.DB.prepare('INSERT INTO graph_metrics(customer_id,degree,weighted_degree,pagerank,community_id,influence_score,updated_at) VALUES(?,?,?,?,?,?,?)');
 for(const m of metrics)await ins.bind(m.customer_id,m.degree,m.weighted_degree,m.pagerank,m.community_id,m.influence_score,new Date().toISOString()).run();

 return {mode,nodes:cs.length,edges:es.length,communities:nc,largest_community:Math.max(...Object.values(cnt),0),leaders,metrics,customers:cs};
}

function base(c){
 let p=.045+.012*Math.min(c.orders/12,1)+.008*Math.min(c.sessions_30d/20,1);
 if(c.customer_type==='Loyal')p+=.03;
 if(c.customer_type==='High Value')p+=.04;
 if(c.device==='iPhone')p+=.008;
 p-=.018*Math.min(c.recency_days/120,1);
 return clamp(p,.01,.35);
}

function treatmentEffect(c,type,category){
 let x=.012;
 if(type==='Discount')x+=.035*(1-Math.min(c.cart_abandonments/10,.9));
 if(type==='UI/UX'&&c.device==='iPhone')x+=.022;
 if(type==='Advertisement'&&c.gender==='Female'&&category==='Beauty')x+=.028;
 if(type==='Product launch')x+=.035;
 if(type==='Recommendation'&&c.customer_type==='Loyal')x+=.024;
 if(type==='Shipping'&&c.customer_type!=='New')x+=.018;
 return x;
}

function normalCI(t,c){const se=Math.sqrt(t*(1-t)/Math.max(t.n,1)+c*(1-c)/Math.max(c.n,1));return [t.rate-c.rate-1.96*se,t.rate-c.rate+1.96*se]}

async function experiment(env,b){
 const cs=(await env.DB.prepare('SELECT * FROM customers LIMIT 5000').all()).results;
 if(!cs.length)throw Error('Generate a synthetic population first.');
 const share=clamp(Number(b.treatment_share||.5),.1,.9),r=rng(Date.now()&2147483647),T=[],C=[];
 for(const c of cs)(r()<share?T:C).push(c);

 const sim=(c,t)=>r()<clamp(base(c)+(t?treatmentEffect(c,b.experiment_type,b.category):0),.001,.9)?1:0;
 const tr=T.map(c=>sim(c,1)),cr=C.map(c=>sim(c,0));
 const mr=a=>a.reduce((s,x)=>s+x,0)/Math.max(a.length,1);
 const t={n:T.length,rate:mr(tr),conv:tr.reduce((a,x)=>a+x,0)},c={n:C.length,rate:mr(cr),conv:cr.reduce((a,x)=>a+x,0)};
 const u=t.rate-c.rate,rel=u/Math.max(c.rate,1e-9),[lo,hi]=normalCI(t,c);
 const rvT=T.reduce((s,x,i)=>s+(tr[i]?x.aov:0),0),rvC=C.reduce((s,x,i)=>s+(cr[i]?x.aov:0),0);
 const q=await env.DB.prepare('INSERT INTO experiments(created_at,experiment_type,category,sample_size,treatment_size,control_size,conversions_treatment,conversions_control,revenue_treatment,revenue_control,aov_treatment,aov_control,conversion_rate_treatment,conversion_rate_control,absolute_uplift,relative_uplift,ci_low,ci_high,revenue_uplift,treatment_share) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)')
  .bind(new Date().toISOString(),b.experiment_type,b.category,cs.length,T.length,C.length,t.conv,c.conv,rvT,rvC,rvT/Math.max(t.conv,1),rvC/Math.max(c.conv,1),t.rate,c.rate,u,rel,lo,hi,rvT-rvC,share).run();

 const segments=[['gender',x=>x.gender],['device',x=>x.device],['customer_type',x=>x.customer_type]];
 const expId=q.meta.last_row_id;
 for(const [name,fn] of segments){
  const values=[...new Set(cs.map(fn))];
  for(const v of values){
   const tt=T.map((x,i)=>({x,y:tr[i]})).filter(z=>fn(z.x)===v),cc=C.map((x,i)=>({x,y:cr[i]})).filter(z=>fn(z.x)===v);
   const trr=tt.reduce((s,z)=>s+z.y,0)/Math.max(tt.length,1),crr=cc.reduce((s,z)=>s+z.y,0)/Math.max(cc.length,1);
   await env.DB.prepare('INSERT INTO segment_results(experiment_id,segment,segment_value,control_n,treatment_n,control_rate,treatment_rate,uplift) VALUES(?,?,?,?,?,?,?,?)').bind(expId,name,v,cc.length,tt.length,crr,trr,trr-crr).run();
  }
 }
 return {id:expId,control_n:C.length,treatment_n:T.length,control_rate:c.rate,treatment_rate:t.rate,absolute_uplift:u,relative_uplift:rel,ci_low:lo,ci_high:hi,revenue_uplift:rvT-rvC,interpretation:'This is a virtual experiment under the simulator assumptions. A positive uplift means the treatment performed better in this synthetic run; it is not a prediction or guarantee for real customers.'};
}

async function graphUplift(env){
 const g=await graph(env,'observable'),metrics=g.metrics,vals=metrics.map(x=>x.influence_score).sort((a,b)=>a-b),med=vals[Math.floor(vals.length*.5)]||0,p95=vals[Math.floor(vals.length*.95)]||0;
 const tiers={Low:[],Medium:[],High:[]},r=rng(90210),lm=new Map(metrics.map(x=>[x.customer_id,x.influence_score]));
 for(const c of g.customers){const inf=lm.get(c.customer_id)||0;(inf>=p95?tiers.High:inf>=med?tiers.Medium:tiers.Low).push({c,inf})}
 const rows=[];
 for(const [tier,a] of Object.entries(tiers)){let tn=0,cn=0,ty=0,cy=0;for(const x of a){const t=r()<.5,p=clamp(base(x.c)+(t?.02+.035*x.inf:0),.001,.9),y=r()<p?1:0;if(t){tn++;ty+=y}else{cn++;cy+=y}}rows.push({tier,n:a.length,control_rate:cy/Math.max(cn,1),treatment_rate:ty/Math.max(tn,1),uplift:ty/Math.max(tn,1)-cy/Math.max(cn,1)})}
 return {tiers:rows,note:'Observable graph only: influence is derived from measurable relationships. A customer without an edge is not assumed dissimilar. This is a synthetic network-effect benchmark, not real-customer causal evidence.'};
}

function res(d,s=200){return new Response(JSON.stringify(d),{status:s,headers:{'content-type':'application/json','cache-control':'no-store'}})}

async function handle(req,env){
 const u=new URL(req.url),p=u.pathname;
 if(p==='/api/health')return res({ok:true,product:'synthetic-experimentation-lab'});
 if(p==='/api/stats'){const a=await env.DB.prepare('SELECT COUNT(*) n FROM customers').first(),b=await env.DB.prepare("SELECT COUNT(*) n FROM customer_edges WHERE reasons NOT LIKE '%profession%' AND reasons NOT LIKE '%price_sensitivity%' AND reasons NOT LIKE '%novelty%' AND reasons NOT LIKE '%risk%'").first(),c=await env.DB.prepare('SELECT COUNT(DISTINCT city) n FROM customers').first();return res({customers:a.n,observable_edges:b.n,cities:c.n})}
 if(p==='/api/population/generate'&&req.method==='POST'){const b=await req.json(),n=clamp(Math.floor(b.n||1500),500,5000);return res(await generate(env,n))}
 if(p==='/api/network'){const mode=u.searchParams.get('mode')||'observable';return res(await network(env,mode))}
 if(p==='/api/experiments/simulate'&&req.method==='POST')return res(await experiment(env,await req.json()));
 if(p==='/api/experiments')return res({experiments:(await env.DB.prepare('SELECT * FROM experiments ORDER BY id DESC LIMIT 50').all()).results});
 if(p.startsWith('/api/experiments/')&&p.endsWith('/report')){const id=p.split('/')[3];return res({experiment:await env.DB.prepare('SELECT * FROM experiments WHERE id=?').bind(id).first(),segments:(await env.DB.prepare('SELECT * FROM segment_results WHERE experiment_id=?').bind(id).all()).results})}
 if(p==='/api/graph/analytics')return res(await graph(env,u.searchParams.get('mode')||'observable'));
 if(p==='/api/graph/uplift'&&req.method==='POST')return res(await graphUplift(env));
 if(p==='/')return new Response(HTML,{headers:{'content-type':'text/html; charset=utf-8'}});
 return res({error:'Not found'},404)
}
export default {async fetch(req,env){try{return await handle(req,env)}catch(e){return res({error:e.message||String(e)},500)}}};