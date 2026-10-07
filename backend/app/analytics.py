import math

def difference_in_proportions(control_n, control_success, treatment_n, treatment_success):
    pc=control_success/control_n if control_n else 0.0
    pt=treatment_success/treatment_n if treatment_n else 0.0
    diff=pt-pc
    se=math.sqrt(max(pc*(1-pc)/control_n + pt*(1-pt)/treatment_n, 1e-12))
    return {"control_rate":pc,"treatment_rate":pt,"uplift":diff,"ci_low":diff-1.96*se,"ci_high":diff+1.96*se}

def segment_results(segments):
    result=[]
    for segment, values in segments.items():
        control=[v for arm,v in values if arm=="control"]
        treatment=[v for arm,v in values if arm=="treatment"]
        if len(values)<30 or not control or not treatment: continue
        cr=sum(control)/len(control); tr=sum(treatment)/len(treatment)
        result.append({"segment":segment,"control_rate":cr,"treatment_rate":tr,"uplift":tr-cr,"n":len(values)})
    return result
