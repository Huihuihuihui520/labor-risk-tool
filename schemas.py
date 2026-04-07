from typing import Optional, List, Literal, Dict, Any
from pydantic import BaseModel, Field

class LaborCase(BaseModel):
    """产程案例数据模型"""
    gestational_age: float = Field(..., description="孕周")
    parity: int = Field(..., description="产次")
    cervical_dilation: float = Field(..., description="宫口开大")
    fetal_presentation_level: int = Field(..., description="先露高低")
    fetal_heart_rate: int = Field(..., description="胎心率")
    blood_pressure: str = Field(..., description="血压 (如：120/80)")
    contraction_strength: str = Field(..., description="宫缩强度")
    amniotic_fluid: str = Field(..., description="羊水性状")
    fetal_biparietal_diameter: float = Field(..., description="胎儿双顶径")
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
    gestational_age: float = Field(39, description="孕周")
    parity: int = Field(0, description="产次")

    class Config:
        extra = "allow"

class AnalyzeRequest(BaseModel):
    """统一分析请求模型"""
    case: LaborCase = Field(..., description="产程案例数据")
    type: Literal["labor", "pph"] = Field(..., description="分析类型：labor=产程评估, pph=PPH复苏")

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
