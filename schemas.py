from typing import Optional, List, Literal, Dict, Any
from pydantic import BaseModel, Field

# ============================================
# 合并症详细信息模型定义
# ============================================

class PlacentalAbruptionDetail(BaseModel):
    """胎盘早剥详细信息"""
    degree: Optional[str] = Field(None, description="分型: I度/II度/III度")
    bleeding: Optional[float] = Field(0, description="阴道出血量 (ml)")
    abdominal_pain: Optional[bool] = Field(False, description="是否持续性腹痛")

class PlacentaPreviaDetail(BaseModel):
    """前置胎盘详细信息"""
    type: Optional[str] = Field(None, description="类型: 完全性/部分性/边缘性/低置胎盘")

class PROMDetail(BaseModel):
    """胎膜早破详细信息"""
    time: Optional[float] = Field(0, description="破膜时间 (小时)")
    fluid_character: Optional[str] = Field(None, description="羊水性状: 清/混浊/臭味")
    temperature: Optional[float] = Field(None, description="体温 (℃)")

class PreeclampsiaDetail(BaseModel):
    """子痫前期详细信息"""
    headache: Optional[bool] = Field(False, description="是否头痛/眼花")
    proteinuria: Optional[str] = Field(None, description="蛋白尿情况: 阴性/+ /++ /+++ /++++")

class ScarredUterusDetail(BaseModel):
    """瘢痕子宫详细信息"""
    cs_count: Optional[int] = Field(1, description="剖宫产次数")
    last_interval: Optional[float] = Field(None, description="末次手术间隔 (年)")
    lower_segment: Optional[float] = Field(None, description="子宫下段厚度 (mm)")

class GDMDetail(BaseModel):
    """妊娠期糖尿病详细信息"""
    fasting_glucose: Optional[float] = Field(None, description="空腹血糖")
    hba1c: Optional[float] = Field(None, description="糖化血红蛋白")

class HeartDiseaseDetail(BaseModel):
    """心脏病详细信息"""
    type: Optional[str] = Field(None, description="心脏病类型")
    nyha_class: Optional[str] = Field(None, description="NYHA心功能分级")

class ComorbiditiesDetail(BaseModel):
    """合并症详细信息联合模型"""
    胎盘早剥: Optional[PlacentalAbruptionDetail] = None
    前置胎盘: Optional[PlacentaPreviaDetail] = None
    胎膜早破: Optional[PROMDetail] = None
    子痫前期: Optional[PreeclampsiaDetail] = None
    瘢痕子宫: Optional[ScarredUterusDetail] = None
    妊娠期糖尿病: Optional[GDMDetail] = None
    心脏病: Optional[HeartDiseaseDetail] = None
    
    class Config:
        extra = "allow"  # 允许额外字段

# ============================================
# 基础模型
# ============================================

class LaborCase(BaseModel):
    """产程案例数据模型"""
    gestational_age: float = Field(..., description="孕周")
    parity: int = Field(..., description="产次")
    cervical_dilation: float = Field(..., description="宫口开大")
    fetal_presentation_level: int = Field(..., description="先露高低")
    fetal_heart_rate: int = Field(..., description="胎心率")
    blood_pressure: str = Field(..., description="血压")
    contraction_strength: str = Field(..., description="宫缩强度")
    amniotic_fluid: str = Field(..., description="羊水性状")
    fetal_biparietal_diameter: float = Field(..., description="胎儿双顶径")
    complications: dict = Field(default_factory=dict, description="孕妇合并症")
    blood_loss: float = Field(..., description="出血量")
    comorbidities: List[str] = Field(default_factory=list, description="合并症与高危因素列表")
    comorbidities_detail: Optional[Dict[str, Any]] = Field(default=None, description="合并症详细信息")

    class Config:
        extra = "allow"

class PPHCase(BaseModel):
    """产后出血复苏数据模型"""
    accumulated_blood_loss: float = Field(0, description="累积失血量 (ml)")
    heart_rate: float = Field(0, description="心率 (bpm)")
    systolic_bp: float = Field(0, description="收缩压 (mmHg)")
    diastolic_bp: float = Field(0, description="舒张压 (mmHg)")
    spo2: float = Field(99, description="血氧饱和度 (%)")
    urine_output: float = Field(0, description="每小时尿量 (ml/h)")
    gcs: int = Field(15, description="GCS昏迷评分 (3-15)")
    hemoglobin: Optional[float] = Field(None, description="血红蛋白 (g/L)")
    hematocrit: Optional[float] = Field(None, description="红细胞压积 (%)")
    fibrinogen: Optional[float] = Field(None, description="纤维蛋白原 (g/L)")
    lactate: Optional[float] = Field(None, description="乳酸 (mmol/L)")
    gestational_age: float = Field(39, description="孕周")
    parity: int = Field(0, description="产次")
    blood_type: Optional[str] = Field(None, description="血型")

class AnalyzeRequest(BaseModel):
    """统一分析请求模型"""
    case: LaborCase = Field(..., description="产程案例数据")
    type: Literal["labor", "pph"] = Field(..., description="分析类型：labor=产程评估, pph=PPH复苏")
