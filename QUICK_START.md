# 产房风险决策系统 - 快速开始指南

## 🚀 快速启动

### 1. 环境准备
```bash
# 创建 .env 文件
API_KEY=your_api_key
API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
MODEL_NAME=deepseek-chat
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 启动服务
```bash
# 开发模式
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 访问
# UI: http://localhost:8000/
# API文档: http://localhost:8000/docs
```

## 📁 核心文件说明

| 文件 | 行数 | 功能 |
|-----|-----|------|
| `index.html` | 2000+ | Vue 3 前端应用，产程评估+PPH两个模块 |
| `main.py` | 300+ | FastAPI后端，5个API端点 |
| `schemas.py` | 50+ | Pydantic数据模型（简化版） |
| `services.py` | 230+ | AI调用和提示词构造 |
| `utils.py` | 150+ | 临床计算函数 |

## 🔌 API端点

### 统一分析接口
```http
POST /analyze
Content-Type: application/json

{
  "type": "labor",
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
```

### 流式分析接口
```http
POST /analyze/stream
# 同上，支持 Server-Sent Events (SSE) 流式输出
```

### PPH专用接口
```http
POST /pph/analyze
# 同上但type改为"pph"
```

## ✨ 核心功能

### 产程评估
1. 输入产程和患者数据
2. 系统检测是否存在紧急指标
3. 若有紧急情况，直接显示警报和建议联系人员
4. 若正常，调用AI获得结构化分析
5. 展示新生儿NRP预案（如需要）

### PPH复苏
1. 输入失血量和生命体征
2. 计算休克指数（SI = 心率/收缩压）
3. 判断是否需要启动MTP预案（blood_loss>1000或SI>1.0）
4. 计算分阶段补液量、输血单位数
5. 提供具体的药物和操作指导

## 🎯 医学参考

本系统基于以下权威指南：
- 《妇产科学（第10版）》
- ACOG Practice Bulletin
- 中国《产后出血预防与处理指南（2023年版）》
- NRP第8版（新生儿复苏教程）

## 📱 手机端特性

- ✅ 完全响应式（320px-2560px）
- ✅ 虚拟键盘自适应（禁用自动缩放）
- ✅ 安全区域适配（刘海屏、Home Indicator）
- ✅ 弱网保护（30秒API超时）
- ✅ 离线配置保存（localStorage）

## 🔐 关键改进点

1. **数据准确性**
   - PPH分析从实际患者数据计算，而非硬编码值
   - 休克指数基于真实的心率和血压

2. **代码清晰性**
   - 移除冗余的数据模型类
   - 整合配置管理到services.py
   - 最小化调试日志

3. **功能完整性**
   - 所有临床计算算法完整保留
   - AI提示词包含完整的医学指南
   - 紧急情况检测机制不变

## 🐛 已知限制

- 依赖于外部AI服务（需要有效的API Key）
- 前端不支持IE 11（需要现代浏览器）
- 流式分析需要服务器支持SSE和Transfer-Encoding

## 📞 故障排除

### API连接失败
- 检查 `.env` 中的 `API_KEY` 和 `API_BASE`
- 验证网络连接和防火墙设置

### localStorage错误
- 无痕模式下配置自动降级到内存存储
- 刷新页面后需重新输入API Key

### UI显示异常
- 清除浏览器缓存
- 强制刷新 (Ctrl+Shift+R)
- 检查浏览器开发者工具中的错误

---

**版本**: 2.1.0 (清理优化版)  
**最后更新**: 2026-04-07  
**维护状态**: 生产就绪 ✅
