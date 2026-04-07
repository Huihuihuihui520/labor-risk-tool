import pytest
from utils import (
    calculate_shock_index,
    calculate_map,
    get_shock_level,
    calculate_resuscitation_plan,
    check_critical_alerts
)
from schemas import LaborCase

def test_calculate_shock_index():
    assert calculate_shock_index(90, 90) == 1.0
    assert calculate_shock_index(100, 50) == 0.5
    assert calculate_shock_index(0, 100) == 0.0

def test_calculate_map():
    assert calculate_map(120, 80) == (120 + 160) / 3

def test_get_shock_level():
    level, color, advice = get_shock_level(0.9)
    assert level == "轻度"
    level, color, advice = get_shock_level(1.2)
    assert level == "中度"
    level, color, advice = get_shock_level(1.8)
    assert level == "重度"
    level, color, advice = get_shock_level(2.5)
    assert level == "极重度"

def test_calculate_resuscitation_plan():
    plan = calculate_resuscitation_plan(1200, 39, 1)
    assert plan["total_crystal_ml"] == 3600
    assert plan["total_colloid_ml"] == 1200
    assert plan["mtp_units"]["红细胞"] == 6

def test_check_critical_alerts():
    case = LaborCase(
        gestational_age=39,
        parity=1,
        cervical_dilation=5,
        fetal_presentation_level=0,
        fetal_heart_rate=140,
        blood_pressure="120/80",
        contraction_strength="正常",
        amniotic_fluid="清",
        fetal_biparietal_diameter=9.2,
        blood_loss=200,
        comorbidities=[]
    )
    is_critical, alerts, contacts = check_critical_alerts(case)
    assert not is_critical
    assert len(alerts) == 0

    case.fetal_heart_rate = 100
    is_critical, alerts, contacts = check_critical_alerts(case)
    assert is_critical
    assert any("胎心率过缓" in alert for alert in alerts)

    case.fetal_heart_rate = 140
    case.blood_loss = 800
    is_critical, alerts, contacts = check_critical_alerts(case)
    assert is_critical
    assert any("产后出血量过多" in alert for alert in alerts)
