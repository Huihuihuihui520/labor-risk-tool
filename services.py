import json
import logging
from typing import Optional, AsyncGenerator, Dict, Any
from openai import AsyncOpenAI
from schemas import LaborCase, PPHCase
from config import settings

logger = logging.getLogger(__name__)

# Reusing single client instance for performance
client = AsyncOpenAI(api_key=settings.api_key, base_url=settings.api_base, timeout=60.0)

def build_labor_system_prompt() -> str:
    """构建产程评估系统提示"""
    return """你是谢泰山，资深产科主任，拥有30年临床经验，精通产科麻醉与危重救治。

【核心原则】你的所有建议必须参考以下权威指南：
- 《妇产科学（第10版）》，人民卫生出版社
- ACOG Practice Bulletin 系列指南
- 中国《产后出血预防与处理指南（2023年版）》
- 中国《妊娠期高血压疾病诊治指南（2020年版）》
- 新生儿复苏教程（NRP）第8版

【输出格式要求】
1. 使用 Markdown 格式输出
2. **粗体**强调关键指标和警告词
3. 使用有序列表描述操作步骤，每步单独成行
4. 紧急呼叫指令必须单独成行，使用【】包裹
5. 关键决策后必须标注参考来源，格式：[参考：指南名称]
6. 每一个建议项必须换行，使用 `-` 符号，严禁堆砌文字

【分析结构 - 必须按此顺序输出】
严格按以下4个模块顺序输出，不要合并或省略：

---
**【风险识别】**
根据体征数据识别的主要风险点

**【处理措施】**
1. 助产士立即执行的操作
2. 需要呼叫的上级医护
3. 针对合并症的特殊处理

**【呼叫建议】**
【紧急】需要立即呼叫：人员列表
【备选】可能需要的支援：人员列表

**【新生儿预案】**（仅当存在以下任一条件时输出：羊水III度、胎心<110或>160、早产、胎盘早剥）
辐射暖箱准备 → 清理气道 → 评估呼吸 → 正压通气(PPV) → 胸外按压 → 肾上腺素
详细NRP步骤见指南

---

【呼叫触发规则】
满足以下任一条件，必须在输出最开头使用红色警示：
- 胎心率 < 110 bpm 或 > 160 bpm
- 羊水III度混浊
- 出血量 > 500 ml
- 瘢痕子宫伴强烈宫缩
- 子痫前期伴血压 > 140/90 mmHg

【合并症处理规范】
- 瘢痕子宫：禁止使用缩宫素，警惕子宫破裂，监测胎心变化
- 子痫前期：硫酸镁解痉，硝苯地平降压，严密监测抽搐前兆
- 胎盘早剥：评估凝血功能，准备输血，立即通知手术室
- 心脏病：缩短第二产程，避免Valsalva动作，考虑分娩镇痛
- GDM：监测血糖，警惕巨大儿，肩难产风险评估

【绝对禁令】：禁止在输出结果的结尾添加任何个人签名、日期、医院名称或虚构的职称（如：主任医师、2025年等）。输出必须以最后一个临床建议结束，严禁任何社交辞令或落款。"""

def build_pph_system_prompt(shock_level: str) -> str:
    """构建PPH复苏系统提示"""
    return f"""你是谢泰山，资深产科主任，专注于危重孕产妇救治。

【核心原则】你必须严格参考《产后出血预防与处理指南（2023年版）》和中国《妊娠期高血压疾病诊治指南》，所有建议必须有循证依据。

【输出格式要求】
1. 使用标准 Markdown 语法
2. **粗体**强调关键指标和药物剂量
3. 每一个建议项必须换行，使用 `-` 符号，严禁堆砌文字
4. 紧急指令用【】包裹
5. 关键决策后必须标注参考来源，格式：[参考：指南名称]

【强制输出要求 - 第一行必须这样开始】
**【当前状态：{shock_level}休克】**

【分析顺序 - 必须严格按此顺序输出】

---
**【紧急评估】**
- 休克指数(SI)及其含义
- 休克程度分级
- 核心警报

**【容量复苏建议】**
1. 补液速度（分阶段）
2. 晶体液与胶体液用量
3. 允许性低血压目标

**【输血比例建议】**
1. 红细胞、血浆、血小板、冷沉淀、纤维蛋白原单位数
2. 输血比例（如1:1:1）
3. 血液制品准备顺序

**【止血药物建议】**
1. 缩宫素用法
2. 卡前列素氨丁三醇用法（禁忌症提示）
3. 氨甲环酸用法
4. 钙剂补充

**【监测与操作流程】**
1. 保暖、吸氧、建立通路
2. 导尿及尿量目标
3. 深静脉/动脉穿刺指征
4. 实验室复查频率

**【呼叫触发】**
当出血量>1000ml或SI>1.0时，必须在输出最开头显示：
【！！紧急启动MTP预案！！】请立即通知：麻醉医生、血库、产科主任

---
【重要参考】
- 晶体液首剂20ml/kg快速输注
- 失血量1500ml以上建议启动MTP
- 纤维蛋白原<2g/L时补充冷沉淀或纤维蛋白原
- 乳酸>2mmol/L提示组织灌注不足

【绝对禁令】：禁止在输出结果的结尾添加任何个人签名、日期、医院名称或虚构的职称（如：主任医师、2025年等）。输出必须以最后一个临床建议结束，严禁任何社交辞令或落款。"""

def build_user_prompt(case: LaborCase) -> str:
    """构建用户提示，包含完整的合并症详情"""
    parts = [
        f"## 基础数据",
        f"- 孕周: {case.gestational_age} 周",
        f"- 产次: {case.parity} 次",
        f"- 宫口开大: {case.cervical_dilation} cm",
        f"- 先露高低: {'已入盆' if case.fetal_presentation_level >= 0 else f'尚在-{abs(case.fetal_presentation_level)}cm处'}",
        f"- 胎心率: {case.fetal_heart_rate} bpm",
        f"- 血压: {case.blood_pressure} mmHg",
        f"- 宫缩强度: {case.contraction_strength}",
        f"- 羊水性状: {case.amniotic_fluid}",
        f"- 胎儿双顶径: {case.fetal_biparietal_diameter} cm",
        f"- 出血量: {case.blood_loss} ml",
    ]

    if case.comorbidities:
        parts.append(f"\n## 合并症与高危因素")
        for comorbidity in case.comorbidities:
            parts.append(f"- {comorbidity}")

        if case.comorbidities_detail:
            parts.append(f"\n### 合并症详细信息")
            for name, detail in case.comorbidities_detail.items():
                if detail:
                    if isinstance(detail, dict):
                        detail_str = ", ".join([f"{k}: {v}" for k, v in detail.items() if v is not None and v != ""])
                        if detail_str:
                            parts.append(f"- **{name}**: {detail_str}")

    parts.append(f"\n---\n请按【分析结构】顺序输出医学建议。")
    return "\n".join(parts)

def build_pph_user_prompt(pph_case: PPHCase, si: float, shock_level: str) -> str:
    """构建PPH用户提示"""
    parts = [
        f"## 当前生命体征",
        f"- 累积失血量: {pph_case.accumulated_blood_loss} ml",
        f"- 心率: {pph_case.heart_rate} bpm",
        f"- 收缩压: {pph_case.systolic_bp} mmHg",
        f"- 舒张压: {pph_case.diastolic_bp} mmHg",
        f"- 血氧饱和度: {pph_case.spo2}%",
        f"- 每小时尿量: {pph_case.urine_output} ml/h",
        f"- GCS评分: {pph_case.gcs}",
        f"- 孕周: {pph_case.gestational_age} 周",
        f"- 产次: {pph_case.parity} 次",
    ]

    if pph_case.hemoglobin is not None:
        parts.append(f"- 血红蛋白: {pph_case.hemoglobin} g/L")
    if pph_case.fibrinogen is not None:
        parts.append(f"- 纤维蛋白原: {pph_case.fibrinogen} g/L")
    if pph_case.lactate is not None:
        parts.append(f"- 乳酸: {pph_case.lactate} mmol/L")

    parts.append(f"\n## 计算指标")
    parts.append(f"- 休克指数(SI): {si:.2f}")
    parts.append(f"- 休克程度: {shock_level}")

    parts.append(f"\n---\n**【强制要求】**")
    parts.append(f"1. 第一行必须输出：**【当前状态：{shock_level}休克】**")
    parts.append(f"2. 必须包含：[容量复苏建议]、[输血比例建议]、[止血药物建议]")
    parts.append(f"3. 使用 Markdown 格式，每一个建议项换行，使用 `-` 符号")

    return "\n".join(parts)

async def call_ai_analysis(system_prompt: str, user_prompt: str) -> Optional[str]:
    """调用AI进行分析，失败时记录日志并返回None"""
    try:
        response = await client.chat.completions.create(
            model=settings.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"[AI调用失败] {str(e)}", exc_info=True)
        return None

async def generate_stream(system_prompt: str, user_prompt: str) -> AsyncGenerator[str, None]:
    """通用流式生成器"""
    try:
        stream = await client.chat.completions.create(
            model=settings.model_name,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=0.3, max_tokens=2000, stream=True
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield f"data: {json.dumps({'token': chunk.choices[0].delta.content}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'done': True}, ensure_ascii=False)}\n\n"
    except Exception as e:
        logger.error(f"[AI流式生成失败] {str(e)}", exc_info=True)
        yield f"data: {json.dumps({'error': f'AI服务暂时不可用: {str(e)[:100]}'}, ensure_ascii=False)}\n\n"
