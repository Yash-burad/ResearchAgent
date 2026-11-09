import time
from fastapi.testclient import TestClient
from research_agent.web.app import app

client = TestClient(app)

def test_create_and_get_travel_plan():
    payload = {
        "destinations": ["Japan"],
        "origin_city": "Mumbai",
        "trip_days": 7,
        "target_budget_inr": 160000.0,
        "travel_tier": "mid",
        "travelers_count": 1,
        "pace_style": "balanced"
    }

    # 1. Create plan
    res = client.post("/api/travel/plans", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "run_id" in data
    assert data["status"] == "processing"
    run_id = data["run_id"]

    # 2. List plans
    list_res = client.get("/api/travel/plans")
    assert list_res.status_code == 200
    plans = list_res.json()
    assert any(p["run_id"] == run_id for p in plans)

    # 3. Poll for completion
    for _ in range(15):
        get_res = client.get(f"/api/travel/plans/{run_id}")
        assert get_res.status_code == 200
        plan = get_res.json()
        if plan.get("status") in ["completed", "failed"]:
            break
        time.sleep(0.4)

    assert plan["status"] == "completed"
    assert plan["result"] is not None
    assert len(plan["result"]["days"]) == 7
    assert plan["result"]["gateway_airport"]["city"] == "Tokyo"
    assert plan["result"]["cost_breakdown"]["total_cost_inr"] > 0

def test_travel_plan_validation():
    # Budget too low (< 10000) or trip_days < 3
    invalid_payload = {
        "destinations": ["Japan"],
        "origin_city": "Mumbai",
        "trip_days": 1,
        "target_budget_inr": 500.0
    }
    res = client.post("/api/travel/plans", json=invalid_payload)
    assert res.status_code == 422
