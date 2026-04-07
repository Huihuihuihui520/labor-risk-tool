# 🆓 产房风险决策辅助系统 - 免费云端部署方案

## 📋 免费方案一览

| 方案 | 平台 | 免费额度 | 国内速度 | 推荐度 |
|------|------|---------|--------|-------|
| **方案A** | **Zeabur** | 100h/月 + CDN | ⭐⭐⭐⭐⭐ | 🥇 首选 |
| 方案B | Railway | 500h/月 | ⭐⭐⭐ | 备选 |
| 方案C | Render | 750h/月 | ⭐⭐⭐ | 备选 |
| 方案D | Vercel + Cloudflare | 无限静态 | ⭐⭐⭐⭐⭐ | 前端首选 |

---

## 🏆 方案A：Zeabur（强烈推荐）

### 为什么选 Zeabur？
- ✅ **国内节点**，访问速度快（服务器在香港/日本）
- ✅ **自带全球CDN**，无需额外配置
- ✅ **自动SSL证书**
- ✅ 支持 Docker 一键部署
- ✅ 免费 100 小时/月（每天约3小时，够用了）
- ✅ 界面中文友好

### 部署步骤（5分钟搞定）

#### 步骤1：注册账号

1. 打开 [zeabur.com](https://zeabur.com)
2. 使用 GitHub / GitLab 账号登录（推荐GitHub）
3. 完成注册

#### 步骤2：推送代码到 GitHub

```bash
# 如果还没有Git仓库，先创建一个
cd d:\zhuchanzhushou\zhuchanzhushou

# 初始化Git仓库（如果还没有）
git init
git add main.py schemas.py utils.py services.py config.py index.html Dockerfile docker-compose.yml nginx.conf requirements.txt zeabur.yml .env.example .dockerignore deploy.sh DEPLOY.md
git commit -m "feat: 产房风险决策辅助系统 v2.1"

# 在 GitHub 上创建新仓库 (private 或 public)
# 然后关联并推送
git remote add origin https://github.com/你的用户名/labor-risk.git
git push -u origin main
```

#### 步骤3：在 Zeabur 上部署

1. 登录 Zeabur → 点击 **"New Project"** → **"Deploy from GitHub"**
2. 选择你刚推送的 `labor-risk` 仓库
3. 配置服务：
   ```
   Service Type: Worker (或 Prebuilt)
   Build Context: ./
   Dockerfile: ./Dockerfile
   Port: 8000
   ```
4. 设置环境变量：
   ```
   API_KEY = sk-your-api-key-here
   API_BASE = https://dashscope.aliyuncs.com/compatible-mode/v1
   MODEL_NAME = deepseek-chat
   ```
5. 点击 **Deploy**

#### 步骤4：获取免费域名 + SSL

Zeabur 会自动分配一个免费子域名：
```
your-app-name.zeabur.app
```
- ✅ 自动配置 HTTPS (Let's Encrypt)
- ✅ 自带 CDN 加速
- ✅ 无需额外操作！

#### 步骤5：绑定自定义域名（可选）

如果你有自己的域名：
1. 在 Zeabur 项目设置中 → Domains → Add Domain
2. 输入你的域名（如 `ob.yourhospital.com`）
3. 按提示添加 DNS CNAME 记录指向 Zeabur
4. SSL 证书自动申请

---

## 🔶 方案B：Railway（最简单）

### 优点
- 界面极简，部署只需点击几下
- 免费额度大：$5/月（≈500小时计算时间）
- 支持自动从 GitHub 部署

### 部署步骤

1. 打开 [railway.app](https://railway.app)
2. GitHub 登录 → **"New Project"** → **"Deploy from GitHub repo"**
3. 选择仓库 → **Add Variables**:
   ```
   API_KEY = sk-your-key
   API_BASE = https://dashscope.aliyuncs.com/compatible-mode/v1
   MODEL_NAME = deepseek-chat
   ```
4. Railway 会自动检测 Dockerfile 并构建
5. 部署完成后获得 `xxx.up.railway.app` 域名
6. **注意**：Railway 的国内速度一般，建议配合 Cloudflare CDN

---

## 🔵 方案C：Render（额度最大）

### 优点
- 免费额度最大：750小时/月 Web Service
- 支持持久化数据库（免费PostgreSQL）
- 自动 SSL

### 部署步骤

1. 打开 [render.com](https://render.com)
2. **"New +"** → **"Web Service"**
3. 连接 GitHub 仓库
4. 配置：
   ```
   Runtime: Docker
   Dockerfile Path: Dockerfile
   Command: uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
   ```
5. 添加环境变量（同上）
6. Deploy!

---

## 💜 方案D：Vercel + Cloudflare Workers（前端+API分离）

### 适用场景
- 只需要前端展示（静态页面）
- 或者用 Cloudflare Workers 跑后端 API（每日10万次请求免费）

### 部署前端到 Vercel（完全免费）

```bash
# 1. 创建 vercel.json
```

```json
{
  "version": 2,
  "name": "labor-risk",
  "builds": [{
    "src": ".",
    "use": "@vercel/static",
    "config": { "distDir": "." }
  }],
  "routes": [
    { "src": "/api/(.*)", "dest": "https://your-api-endpoint/$1", "headers": { "Access-Control-Allow-Origin": "*" } },
    { "src": "/(.*)", "dest": "/index.html" }
  ]
}
```

```bash
# 2. 安装 Vercel CLI 并部署
npm i -g vercel
vercel --prod
```

---

## 🌐 免费域名方案

| 方案 | 域名格式 | 价格 | 说明 |
|------|---------|------|------|
| **Zeabur自带** | `xxx.zeabur.app` | 免费 | 推荐！ |
| **Railway自带** | `xxx.up.railway.app` | 免费 | 速度一般 |
| **Render自带** | `xxx.onrender.com` | 免费 | 速度一般 |
| **Vercel自带** | `xxx.vercel.app` | 免费 | 国内需翻墙 |
| **Cloudflare Pages** | `xxx.pages.dev` | 免费 | 速度快 |
| **Freenom** | `.tk` / `.ml` / `.ga` | 免费 | 需定期续期 |
| **eu.org** | `xxx.eu.org` | 免费 | 申请需审核 |

### 推荐：使用平台自带域名（零配置）

直接用 `xxx.zeabur.app` 这样的域名，省去所有配置麻烦。

---

## 🚀 最快上手路径（推荐）

```
┌─────────────────────────────────────────────┐
│           5分钟免费部署流程                  │
├─────────────────────────────────────────────┤
│                                             │
│  ① 注册 GitHub (github.com)                │
│     ↓                                        │
│  ② 推送代码到 GitHub                        │
│     git push origin main                    │
│     ↓                                        │
│  ③ 登录 zeabur.com                         │
│     ↓                                        │
│  ④ 选择仓库 → Deploy                      │
│     ↓                                        │
│  ⑤ 填写 API_KEY 等环境变量                   │
│     ↓                                        │
│  ⑥ 完成！获得 https://xxx.zeabur.app       │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 💰 成本对比

| 方案 | 月费用 | 备注 |
|------|--------|------|
| Zeabur 免费版 | **¥0** | 100h/月，够个人/小团队用 |
| Railway 免费版 | **$0** | $5/月credit，用完降速 |
| Render 免费版 | **$0** | 750h/月，超了休眠 |
| 自建云服务器 | ¥180-290/月 | 之前文档的付费方案 |

> **结论**：对于医疗辅助工具这类低并发应用，**免费方案完全够用**。等用户量大了再考虑升级。

---

## ⚠️ 注意事项

1. **免费服务可能休眠**：长时间无访问会进入休眠状态，首次请求会慢几秒（冷启动）
2. **数据备份**：免费平台不保证数据持久化，重要数据建议定期导出
3. **流量限制**：免费额度有限制，超出会暂停服务
4. **生产环境建议**：正式上线医院内网使用时，建议至少用最低配付费方案保证稳定性

---

> 💡 **我的建议**：先用 **Zeabur 免费版** 测试和内部试用，确认功能稳定后再考虑是否需要付费升级。
