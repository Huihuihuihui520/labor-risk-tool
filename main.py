import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from schemas import LaborCase, PPHCase, AnalyzeRequest
from utils import (
    calculate_shock_index, calculate_map, get_shock_level,
    calculate_resuscitation_plan, check_critical_alerts
)
from services import (
    build_labor_system_prompt, build_pph_system_prompt,
    build_user_prompt, build_pph_user_prompt,
    call_ai_analysis, generate_stream
)

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="产房风险决策辅助工具",
    description="为助产士小组提供产科风险分析和决策支持 - 医学指南合规版",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    """统一分析接口 - 根据 type 参数调用不同的分析逻辑"""
    match request.type:
        case "labor":
            return await handle_labor_analysis(request.case)
        case "pph":
            return await handle_pph_analysis(request.case)
        case _:
            raise HTTPException(status_code=400, detail=f"无效的type参数: {request.type}")

async def handle_labor_analysis(case: LaborCase) -> dict:
    """处理产程评估分析"""
    is_critical, alerts, contacts = check_critical_alerts(case)

    if is_critical:
        return {
            "status": "critical",
            "type": "labor",
            "alerts": alerts,
            "contacts": contacts,
            "ai_analysis": None,
            "newborn_emergency": any(kw in str(alerts) for kw in ["羊水III度", "胎心率"])
        }

    system_prompt = build_labor_system_prompt()
    user_prompt = build_user_prompt(case)
    ai_analysis = await call_ai_analysis(system_prompt, user_prompt)

    has_newborn_risk = any([
        case.amniotic_fluid == "III度",
        case.fetal_heart_rate < 110 or case.fetal_heart_rate > 160,
        case.gestational_age < 34,
        "胎盘早剥" in case.comorbidities
    ])

    return {
        "status": "normal",
        "type": "labor",
        "alerts": [],
        "contacts": [],
        "ai_analysis": ai_analysis,
        "newborn_emergency": has_newborn_risk,
        "newborn_nrp": [
            "1. 辐射保温台预热至36.5°C",
            "2. 摆正体位，清理气道（必要时）",
            "3. 擦干全身，给予触觉刺激",
            "4. 评估呼吸：若无呼吸或喘息 → 正压通气(PPV) 40-60次/分",
            "5. 30秒后评估心率：若<60bpm → 启动胸外按压",
            "6. 气管插管或喉罩气道置入",
            "7. 若心率仍<60bpm → 肾上腺素0.01-0.03mg/kg静脉注射",
            "[参考：NRP第8版指南]"
        ] if has_newborn_risk else None
    }

async def handle_pph_analysis(case: LaborCase) -> dict:
    """处理PPH复苏分析 - 基于规则计算优先，AI增强可选"""
    abl = max(case.blood_loss, 0)
    # Default values for mock request
    hr = 80
    sbp = 90
    dbp = 60

    si = calculate_shock_index(sbp, hr)
    shock_level, shock_color, shock_advice = get_shock_level(si)
    resuscitation = calculate_resuscitation_plan(abl, case.gestational_age, case.parity)
    need_mtp = abl >= 1000 or si > 1.0

    pph_case = PPHCase(
        accumulated_blood_loss=abl,
        heart_rate=hr,
        systolic_bp=sbp,
        diastolic_bp=dbp,
        gestational_age=case.gestational_age,
        parity=case.parity
    )

    system_prompt = build_pph_system_prompt(shock_level)
    user_prompt = build_pph_user_prompt(pph_case, si, shock_level)
    ai_analysis = await call_ai_analysis(system_prompt, user_prompt)

    return {
        "status": "ok",
        "type": "pph",
        "indicators": {
            "abl": abl,
            "si": round(si, 2),
            "shock_level": shock_level,
            "shock_color": shock_color,
            "shock_advice": shock_advice
        },
        "need_mtp": need_mtp,
        "mtp_message": "【！！紧急启动MTP预案！！】请立即通知：麻醉医生、血库、产科主任" if need_mtp else None,
        "ai_analysis": ai_analysis,
        "resuscitation": resuscitation,
        "lab_reference": {
            "hemoglobin": pph_case.hemoglobin,
            "fibrinogen": pph_case.fibrinogen,
            "lactate": pph_case.lactate
        }
    }

@app.post("/analyze/stream")
async def analyze_stream(request: AnalyzeRequest):
    """流式分析接口 - 根据 type 参数调用不同的分析逻辑"""
    match request.type:
        case "labor":
            is_critical, alerts, contacts = check_critical_alerts(request.case)
            if is_critical:
                return {"status": "critical", "type": "labor", "alerts": alerts, "contacts": contacts}
            
            system_prompt = build_labor_system_prompt()
            user_prompt = build_user_prompt(request.case)
            
            return StreamingResponse(
                generate_stream(system_prompt, user_prompt),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"}
            )
        case "pph":
            abl = max(request.case.blood_loss, 0)
            si = calculate_shock_index(90, 80)
            shock_level, _, _ = get_shock_level(si)
            pph_case = PPHCase(
                accumulated_blood_loss=abl, heart_rate=80, systolic_bp=90, diastolic_bp=60,
                gestational_age=request.case.gestational_age, parity=request.case.parity
            )
            system_prompt = build_pph_system_prompt(shock_level)
            user_prompt = build_pph_user_prompt(pph_case, si, shock_level)
            
            return StreamingResponse(
                generate_stream(system_prompt, user_prompt),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"}
            )
        case _:
            raise HTTPException(status_code=400, detail=f"无效的type参数: {request.type}")

@app.post("/pph/analyze")
async def analyze_pph_direct(pph_case: PPHCase):
    """
    PPH复苏分析接口（直接接收PPHCase）- 核心接口
    基于规则的计算结果始终返回，AI分析作为可选增强
    """
    si = calculate_shock_index(pph_case.systolic_bp, pph_case.heart_rate)
    map_val = calculate_map(pph_case.systolic_bp, pph_case.diastolic_bp)
    abl = pph_case.accumulated_blood_loss

    shock_level, shock_color, shock_advice = get_shock_level(si)
    resuscitation = calculate_resuscitation_plan(abl, pph_case.gestational_age, pph_case.parity)
    need_mtp = abl >= 1000 or si > 1.0

    system_prompt = build_pph_system_prompt(shock_level)
    user_prompt = build_pph_user_prompt(pph_case, si, shock_level)
    ai_analysis = await call_ai_analysis(system_prompt, user_prompt)

    return {
        "status": "ok",
        "type": "pph",
        "indicators": {
            "abl": abl,
            "si": round(si, 2),
            "map": round(map_val, 1),
            "shock_level": shock_level,
            "shock_color": shock_color,
            "shock_advice": shock_advice
        },
        "need_mtp": need_mtp,
        "mtp_message": "【！！紧急启动MTP预案！！】请立即通知：麻醉医生、血库、产科主任" if need_mtp else None,
        "ai_analysis": ai_analysis,
        "resuscitation": resuscitation,
        "lab_reference": {
            "hemoglobin": pph_case.hemoglobin,
            "hematocrit": pph_case.hematocrit,
            "fibrinogen": pph_case.fibrinogen,
            "lactate": pph_case.lactate,
            "interpretation": {}
        }
    }

@app.get("/pph")
def read_pph():
    """PPH工作站入口"""
    return {
        "name": "PPH 紧急复苏工作站",
        "version": "1.1.0",
        "endpoints": {
            "/pph/analyze": "PPH复苏分析 (POST, 直接接收PPHCase)",
            "/analyze": "统一分析接口 (POST, 含type参数)",
            "/analyze/stream": "流式分析接口 (POST)"
        }
    }

@app.get("/")
def read_root():
    return {
        "name": "产房风险决策辅助工具",
        "version": "2.1.0",
        "endpoints": {
            "/analyze": "统一分析接口 (POST)",
            "/analyze/stream": "流式分析接口 (POST)",
            "/pph/analyze": "PPH复苏分析 (POST)",
            "/pph": "PPH工作站"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
