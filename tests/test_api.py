import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "产房风险决策辅助工具" in response.json()["name"]

def test_read_pph():
    response = client.get("/pph")
    assert response.status_code == 200
    assert "PPH 紧急复苏工作站" in response.json()["name"]

def test_analyze_invalid_type():
    payload = {
        "type": "invalid",
        "case": {
            "gestational_age": 39,
            "parity": 1,
            "cervical_dilation": 5,
            "fetal_presentation_level": 0,
            "fetal_heart_rate": 140,
            "blood_pressure": "120/80",
            "contraction_strength": "正常",
            "amniotic_fluid": "清",
            "fetal_biparietal_diameter": 9.2,
            "blood_loss": 200,
            "comorbidities": []
        }
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 400

def test_pph_analyze_direct():
    payload = {
        "accumulated_blood_loss": 1200,
        "heart_rate": 120,
        "systolic_bp": 80,
        "diastolic_bp": 50,
        "spo2": 95,
        "urine_output": 20,
        "gcs": 15,
        "gestational_age": 39,
        "parity": 1
    }
    response = client.post("/pph/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "pph"
    assert data["indicators"]["abl"] == 1200
    assert data["need_mtp"] == True
