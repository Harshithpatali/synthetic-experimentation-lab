from app.main import diff_ci, make_population, sigmoid

def test_population_reproducible():
    first,_=make_population(50,7); second,_=make_population(50,7)
    assert [(r["age"],r["city"],r["gender"]) for r in first] == [(r["age"],r["city"],r["gender"]) for r in second]

def test_sigmoid():
    assert 0 < sigmoid(-2) < .5 < sigmoid(2) < 1

def test_ci_contains_estimate():
    difference,low,high=diff_ci(100,20,100,30)
    assert abs(difference-.10)<1e-9 and low < difference < high
