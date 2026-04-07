from typing import Tuple, List, Dict, Any
from schemas import LaborCase

def calculate_shock_index(systolic_bp: float, heart_rate: float) -> float:
    """计算休克指数 SI = HR/SBP"""
    if systolic_bp <= 0:
        return 0.0
    return heart_rate / systolic_bp

def calculate_map(systolic_bp: float, diastolic_bp: float) -> float:
    """计算平均动脉压 MAP = (SBP + 2*DBP) / 3"""
    return (systolic_bp + 2 * diastolic_bp) / 3

def get_shock_level(si: float) -> Tuple[str, str, str]:
    """根据休克指数判断休克程度，返回 (等级, 颜色代码, 处理建议)"""
    if si < 1.0:
        return "轻度", "#34C759", "密切监测，继续观察"
    elif si < 1.5:
        return "中度", "#FF9500", "需要快速补液，准备输血"
    elif si < 2.0:
        return "重度", "#FF6B35", "立即启动MTP预案，紧急配血"
    else:
        return "极重度", "#FF3B30", "濒死状态，立即复苏"

def calculate_resuscitation_plan(abl: float, gestational_age: float, parity: int) -> Dict[str, Any]:
    """
    根据《产后出血预防与处理指南（2023年版）》计算复苏方案
    返回包含所有复苏参数的字典
    """
    total_crystal = abl * 3
    total_colloid = abl
    total_fluid = total_crystal + total_colloid

    mtp_units = {
        "红细胞": 0,
        "新鲜冰冻血浆": 0,
        "血小板": 0,
        "冷沉淀": 0,
        "纤维蛋白原": 0
    }

    if abl >= 500:
        mtp_units["红细胞"] = 4
        mtp_units["新鲜冰冻血浆"] = 4
        mtp_units["血小板"] = 1

    if abl >= 1000:
        mtp_units["红细胞"] = 6
        mtp_units["新鲜冰冻血浆"] = 6
        mtp_units["血小板"] = 1
        mtp_units["冷沉淀"] = 10

    if abl >= 1500:
        mtp_units["红细胞"] = 10
        mtp_units["新鲜冰冻血浆"] = 10
        mtp_units["血小板"] = 2
        mtp_units["冷沉淀"] = 20
        mtp_units["纤维蛋白原"] = 4

    uterotonic = {
        "缩宫素": "10-20U + 500ml 晶体液 ivgtt 维持",
        "卡前列素氨丁三醇": "250μg 肌注或宫体注射，必要时15-90min重复，总量≤2mg",
        "氨甲环酸": "1g + 100ml NS iv >10min, 3g总量",
        "钙剂": "10%葡萄糖酸钙10ml + 5%GS 缓慢静注"
    }

    infusion_speed = {
        "第一小时": f"{max(int(total_fluid / 3), 100)}ml/h",
        "第二小时": f"{max(int(total_fluid / 6), 50)}ml/h",
        "维持": f"{max(int(total_fluid / 12), 25)}ml/h"
    }

    return {
        "target_sbp_range": "80-90",
        "target_map_range": "50-60",
        "total_crystal_ml": total_crystal,
        "total_colloid_ml": total_colloid,
        "total_fluid_ml": total_fluid,
        "mtp_units": mtp_units,
        "uterotonic": uterotonic,
        "infusion_speed": infusion_speed,
        "monitoring": [
            "保暖：室温28°C，加温毯",
            "高流量面罩吸氧 8-10L/min，维持SpO2≥95%",
            "建立两条16G/14G静脉通路",
            "留置导尿，记录每小时尿量，维持≥30ml/h",
            "深静脉穿刺置管监测CVP",
            "动脉穿刺置管实时监测ABP",
            "复查血常规、凝血功能、血气分析 q30min"
        ]
    }

def check_critical_alerts(case: LaborCase) -> Tuple[bool, List[str], List[str]]:
    """检查是否存在紧急情况，返回 (是否紧急, 警报列表, 建议联系人员)"""
    alerts = []
    contacts = []

    if case.fetal_heart_rate < 110:
        alerts.append(f"胎心率过缓 ({case.fetal_heart_rate} bpm)")
        contacts.extend(["产科主任", "麻醉医生"])
    elif case.fetal_heart_rate > 160:
        alerts.append(f"胎心率过快 ({case.fetal_heart_rate} bpm)")
        contacts.extend(["产科主任"])

    if case.amniotic_fluid == "III度":
        alerts.append("羊水III度混浊 - 胎儿窘迫风险高")
        contacts.extend(["儿科医生", "产科主任"])

    if case.blood_loss > 500:
        alerts.append(f"产后出血量过多 ({case.blood_loss} ml)")
        contacts.extend(["产科主任", "麻醉医生", "手术室"])

    if "瘢痕子宫" in case.comorbidities and case.contraction_strength == "持续性强烈宫缩":
        alerts.append("疑似子宫破裂风险")
        contacts.extend(["产科主任", "麻醉医生", "手术室团队"])

    if "子痫前期" in case.comorbidities:
        try:
            systolic = int(case.blood_pressure.split("/")[0])
            if systolic > 140:
                alerts.append(f"子痫前期血压危象 ({case.blood_pressure})")
                contacts.extend(["产科主任", "麻醉医生", "ICU"])
        except (ValueError, IndexError, AttributeError):
            pass

    if case.comorbidities_detail and "胎盘早剥" in case.comorbidities_detail:
        detail = case.comorbidities_detail["胎盘早剥"]
        if isinstance(detail, dict):
            if detail.get("degree") == "III度" or detail.get("bleeding", 0) > 300:
                alerts.append("重型胎盘早剥")
                contacts.extend(["产科主任", "麻醉医生", "手术室", "血库"])

    return len(alerts) > 0, alerts, list(set(contacts))[:4]
