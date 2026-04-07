# 产房风险决策辅助工具 (Labor Risk Decision Support System)

这是一个基于 FastAPI 和 Pydantic 的产科风险分析和决策支持系统，旨在为助产士小组提供实时、符合医学指南的建议。系统涵盖了产程评估（Labor Assessment）和产后出血（PPH）紧急复苏工作站。

## 目录结构

- `main.py`: 主程序，定义 FastAPI 路由和异常处理
- `config.py`: 配置管理（API Key，模型参数等）
- `schemas.py`: Pydantic 数据模型定义
- `services.py`: 核心业务逻辑，包括 AI 提示词构建与外部 API 调用
- `utils.py`: 临床指标计算工具（休克指数、MAP、复苏方案计算等）
- `index.html` & `pph_station.html`: 前端界面（支持产程评估和PPH指标监控）
- `tests/`: 单元与集成测试套件

## 功能特性

- **零高危安全漏洞**: 移除硬编码 API 密钥，使用环境变量管理敏感信息。
- **模块化架构**: 将路由、模型、服务与工具类解耦，极大提升了代码的可维护性与可扩展性。
- **临床规则计算优先**: PPH 模块基于《产后出血预防与处理指南（2023年版）》实时计算 MTP 和补液量。
- **AI 智能增强**: 基于权威指南生成结构化的临床建议。
- **流式响应**: 支持 SSE（Server-Sent Events）实现 AI 分析的打字机流式输出。
- **健壮性**: 全局异常处理和请求验证，确保运行稳定。

## 快速开始

### 1. 安装依赖

请确保系统已安装 Python 3.10+ 环境。

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件，并设置相关环境变量：

```ini
API_KEY=your_api_key_here
API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
MODEL_NAME=deepseek-chat
```

### 3. 启动服务

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

后端启动后，可以直接在浏览器中打开 `index.html` 或者访问 `http://localhost:8000/docs` 查看 Swagger API 文档。

## 测试

本项目包含完备的单元测试，涵盖了工具函数和 API 路由：

```bash
python -m pytest tests/
```

## 技术栈
- Backend: Python, FastAPI, Pydantic, OpenAI SDK
- Frontend: Vue 3, Tailwind CSS
- Testing: Pytest, HTTPX
