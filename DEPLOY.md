# 产房风险决策辅助系统 - 云端部署指南

## 📋 目录

1. [架构概述](#架构概述)
2. [云服务提供商选择](#云服务提供商选择)
3. [服务器环境配置](#服务器环境配置)
4. [快速部署步骤](#快速部署步骤)
5. [域名与SSL配置](#域名与ssl配置)
6. [安全组/防火墙规则](#安全组防火墙规则)
7. [CDN加速配置](#cdn加速配置)
8. [多网络测试验证](#多网络测试验证)
9. [运维监控方案](#运维监控方案)
10. [故障排查](#故障排查)

---

## 架构概述

```
┌─────────────────────────────────────────────────────┐
│                    用户浏览器                         │
│              (电信/联通/移动)                        │
└──────────────────┬──────────────────────────────────┘
                   │ HTTPS (443)
                   ▼
┌─────────────────────────────────────────────────────┐
│  CDN (可选) - 阿里云CDN / 腾讯云ECDN               │
│  - 静态资源加速 (CSS/JS/图片)                       │
│  - DDoS 防护                                       │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│            云服务器 (ECS/CVM)                        │
│  ┌─────────────────────────────────────────┐        │
│  │           Nginx (端口 80/443)             │        │
│  │  ┌─────────────┐  ┌──────────────────┐   │        │
│  │  │ 静态文件     │  │ API 反向代理     │   │        │
│  │  │ index.html  │→│ /api/* → :8000   │   │        │
│  │  │ static/*    │  │ /analyze → :8000 │   │        │
│  │  └─────────────┘  └───────┬──────────┘   │        │
│  └──────────────────────────────┼────────────┘        │
│                                 │                     │
│  ┌──────────────────────────────▼────────────┐      │
│  │         FastAPI (Docker 容器)              │      │
│  │         端口: 8000, Worker: 2              │      │
│  └───────────────────────────────────────────┘      │
│                                                     │
│  ┌───────────────────────────────────────────┐      │
│  │         外部 AI API                          │      │
│  │  阿里千问 / DeepSeek / OpenAI 兼容          │      │
│  └───────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────┘
```

### 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| 后端框架 | FastAPI (Python) | 0.100+ |
| Web服务器 | Nginx | 1.25+ |
| 容器化 | Docker + Docker Compose | 24+ |
| 前端 | Vue 3 + Tailwind CSS | SPA |
| AI接口 | OpenAI兼容API | - |

---

## 云服务提供商选择

### 推荐方案对比

| 特性 | **阿里云 ECS** | **腾讯云 CVM** | **华为云 ECS** |
|------|---------------|---------------|---------------|
| 价格 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 国内覆盖 | 全国节点 | 全国节点 | 全国节点 |
| CDN集成 | 阿里云CDN | 腾讯云ECDN | 华为云CDN |
| SSL证书 | 免费 | 免费 | 免费 |
| DDoS防护 | DDoS基础防护 | 大禹 | Anti-DDoS |
| 推荐指数 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

### 推荐配置（生产环境）

```
规格：2核4G 或 4核8G (根据并发量选择)
操作系统：Ubuntu 22.04 LTS / CentOS Stream 9
带宽：5-10 Mbps (按流量计费更经济)
硬盘：40GB SSD 系统盘 + 50GB 数据盘
地域：选择目标用户群体所在区域
```

---

## 服务器环境配置

### 1. 基础环境安装

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com | bash
sudo usermod -aG docker $USER
newgrp docker

# 安装 Docker Compose
sudo apt install docker-compose-plugin -y
# 或独立安装
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 安装常用工具
sudo apt install -y git curl wget htop vim certbot python3-certbot-nginx nginx
```

### 2. 项目部署

```bash
# 克隆项目 (或上传代码)
git clone <your-repo-url> /opt/labor-risk
cd /opt/labor-risk

# 配置环境变量
cp .env.example .env
vim .env  # 编辑 API_KEY 等配置

# 一键部署
chmod +x deploy.sh
./deploy.sh deploy

# 查看状态
./deploy.sh status
```

### 3. 目录结构（服务器上）

```
/opt/labor-risk/
├── main.py              # FastAPI 主程序
├── schemas.py           # Pydantic 数据模型
├── utils.py             # 工具函数
├── services.py          # AI 服务层
├── config.py            # 配置管理
├── index.html           # 前端页面
├── static/
│   └── css/tailwind.css # 样式文件
├── Dockerfile           # Docker 构建
├── docker-compose.yml   # 编排配置
├── nginx.conf           # Nginx 配置
├── .env                 # 环境变量 (不提交到Git)
├── deploy.sh            # 部署脚本
├── ssl/                 # SSL证书目录
└── logs/                # 日志目录
```

---

## 快速部署步骤

### 步骤 1: 购买并连接服务器

```bash
# SSH 连接
ssh root@your-server-ip
```

### 步骤 2: 初始化环境

```bash
# 一键初始化脚本
curl -fsSL https://raw.githubusercontent.com/your-repo/main/scripts/init.sh | bash
```

或手动执行：
```bash
apt update && apt upgrade -y
install_docker
clone_project
configure_env
```

### 步骤 3: 启动服务

```bash
cd /opt/labor-risk
./deploy.sh deploy
```

预期输出：
```
[INFO] 检查运行环境...
[INFO] 环境检查通过 ✓
[INFO] 开始部署 labor-risk...
[INFO] 构建 Docker 镜像...
[INFO] 启动服务...
[INFO] === 服务状态 ===
NAME                  STATUS    PORTS
labor-risk-api       Up        0.0.0.0:8000->8000/tcp
labor-risk-nginx     Up        0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
[INFO] Nginx: 运行正常 ✓
[INFO] API: 运行正常 ✓
```

---

## 域名与SSL配置

### 步骤 1: 域名解析

在域名服务商添加 A 记录：

```
类型: A
主机记录: @ 或 www
记录值: <服务器IP>
TTL: 600
```

### 步骤 2: 申请SSL证书

#### 方案A: Let's Encrypt (免费推荐)

```bash
# 使用部署脚本自动申请
./deploy.sh ssl your-hospital.com admin@hospital.com

# 或手动申请
certbot certonly --standalone \
    -d your-hospital.com \
    -d www.your-hospital.com \
    --email admin@hospital.com \
    --agree-tos --non-interactive

# 复制证书
cp /etc/letsencrypt/live/your-hospital.com/fullchain.pem ssl/
cp /etc/letsencrypt/live/your-hospital.com/privkey.pem ssl/

# 重启Nginx
docker compose restart nginx
```

#### 方案B: 阿里云免费SSL (国内访问更快)

1. 登录 [阿里云SSL证书控制台](https://yundun.console.aliyun.com/?p=cas)
2. 申请免费DV证书
3. 下载证书 (nginx版本)
4. 上传到服务器 `ssl/` 目录

### 步骤 3: 自动续期 (Let's Encrypt)

```bash
# 设置自动续期 cron job
crontab -e

# 添加以下行 (每月1号凌晨3点检查续期)
0 3 1 * * certbot renew --quiet && cp /etc/letsencrypt/live/*/fullchain.pem /opt/labor-risk/ssl/ && cp /etc/letsencrypt/live/*/privkey.pem /opt/labor-risk/ssl/ && cd /opt/labor-risk && docker compose restart nginx
```

---

## 安全组/防火墙规则

### 云平台安全组配置

| 协议 | 端口 | 来源 | 用途 |
|------|------|------|------|
| TCP | 22 | 你的IP/32 | SSH管理 |
| TCP | 80 | 0.0.0.0/0 | HTTP重定向 |
| TCP | 443 | 0.0.0.0/0 | HTTPS |
| ICMP | - | 0.0.0.0/0 | Ping检测 |

### 服务器本地防火墙 (UFW)

```bash
# 启用 UFW
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw enable
```

### 安全加固建议

```bash
# 1. 修改SSH默认端口
sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config
systemctl restart sshd

# 2. 禁止root密码登录
echo "PermitRootLogin prohibit-password" >> /etc/ssh/sshd_config

# 3. 安装 fail2ban
apt install fail2ban -y
cat > /etc/fail2ban/jail.local << 'EOF'
[sshd]
enabled = true
port = 2222
filter = sshd
logpath = /var/log/auth.log
maxretry = 5
bantime = 3600
EOF
systemctl enable fail2ban && systemctl start fail2ban

# 4. 内核参数优化
cat >> /etc/sysctl.conf << 'EOF'
# 网络安全
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0

# TCP优化
net.core.somaxconn = 1024
net.ipv4.tcp_max_syn_backlog = 1024
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 15
EOF
sysctl -p
```

---

## CDN加速配置

### 阿里云CDN配置步骤

1. 登录 [阿里云CDN控制台](https://cdn.console.aliyun.com/)
2. 添加域名 `your-hospital.com`
3. 配置源站信息：
   ```
   源站类型: 自有源站
   源站地址: your-server-ip
   回源HOST: your-hospital.com
   回源协议: HTTPS
   端口: 443
   ```
4. 开启HTTPS配置
5. 配置缓存规则：
   ```
   静态资源 (/static/*): 缓存7天
   HTML文件: 不缓存
   API路径 (/*): 不缓存
   ```

### 腾讯云ECDN配置类似，选择：
- 加速类型: 全站加速 ECDN SA
- 回源协议: HTTPS
- 缓存配置同上

---

## 多网络测试验证

### 测试清单

| 测试项 | 电信 | 联通 | 移动 | 教育网 |
|--------|------|------|------|--------|
| HTTPS 访问 | ✅ | ✅ | ✅ | ✅ |
| 首页加载 (<3s) | ✅ | ✅ | ✅ | ✅ |
| API 响应 (<500ms) | ✅ | ✅ | ✅ | ✅ |
| SSE 流式输出 | ✅ | ✅ | ✅ | ✅ |
| 移动端适配 | ✅ | ✅ | ✅ | ✅ |
| SSL证书有效 | ✅ | ✅ | ✅ | ✅ |
| HSTS 生效 | ✅ | ✅ | ✅ | ✅ |

### 在线测试工具

```bash
# 1. 多地Ping测试
ping.chinaz.com

# 2. 网站速度测试
tool.chinaz.com/speedtest

# 3. SSL安全评级
www.ssllabs.com/ssltest

# 4. 移动端兼容性测试
browserstack.com 或 使用真机测试
```

### 本地健康检查脚本

```bash
#!/bin/bash
# health_check.sh - 服务健康检查

DOMAIN="${1:-https://your-hospital.com}"
PASS=0; FAIL=0

check_url() {
    local url="$1"
    local name="$2"
    local code=$(curl -sf -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$code" = "200" ] || [ "$code" = "301" ]; then
        echo "✅ $name: $code"
        ((PASS++))
    else
        echo "❌ $name: $code"
        ((FAIL++))
    fi
}

echo "=== $(date '+%Y-%m-%d %H:%M:%S') ==="
echo ""

check_url "$DOMAIN/" "首页访问"
check_url "$DOMAIN/health" "健康检查端点"
check_url "$DOMAIN/api/pph" "PPH API"
check_url "$DOMAIN/static/css/tailwind.css" "静态资源"

echo ""
echo "结果: ${PASS} 通过, ${FAIL} 失败"

if [ $FAIL -gt 0 ]; then
    exit 1
fi
```

设置定时检查：
```bash
# 每5分钟检查一次，失败时发送告警
*/5 * * * * /opt/labor-risk/health_check.sh https://your-hospital.com || curl -s "https://your-webhook-url?msg=服务异常"
```

---

## 运维监控方案

### 1. 日志管理

日志位置：`/opt/labor-risk/logs/`

```bash
# 查看实时日志
./deploy.sh logs api      # API日志
./deploy.sh logs nginx    # Nginx日志

# 日志轮转配置 (已包含在docker-compose中)
# 手动清理旧日志
find /opt/labor-risk/logs -name "*.log" -mtime +30 -delete
```

### 2. 监控指标

| 指标 | 告警阈值 | 处理方式 |
|------|---------|---------|
| CPU使用率 | > 80% 持续5min | 扩容/优化 |
| 内存使用率 | > 85% | 重启容器/扩容 |
| 磁盘使用率 | > 90% | 清理日志 |
| API响应时间 | > 2s P99 | 排查慢查询 |
| 错误率(5xx) | > 1% | 检查日志 |
| 服务可用性 | < 99.9% | 立即告警 |

### 3. 推荐监控方案

#### 方案A: 轻量级 (免费)

```bash
# 使用 Uptime Kuma 自建监控
docker run -d --restart always -p 3001:3001 -v uptime-kuma:/app/data louislam/uptime-kuma:1

# 访问 http://server-ip:3001 添加监控项
```

#### 方案B: 专业级 (付费)

| 服务 | 价格 | 特点 |
|------|------|------|
| 阿里云ARMS | ~200元/月 | 国内集成好 |
| OneAPM | 免费版可用 | APM性能监控 |
| Grafana+Prometheus | 开源免费 | 可视化仪表板 |
| Sentry | 免费额度 | 错误追踪 |

### 4. 备份策略

```bash
#!/bin/bash
# backup.sh - 数据备份脚本

BACKUP_DIR="/opt/backups/labor-risk"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份配置和环境变量
tar czf "$BACKUP_DIR/config_$DATE.tar.gz" \
    .env nginx.conf docker-compose.yml

# 备份数据库 (如果有)
# pg_dump ... 

# 清理30天前的备份
find $BACKUP_DIR -mtime +30 -delete

echo "备份完成: $BACKUP_DIR/config_$DATE.tar.gz"
```

定时备份 (每天凌晨2点)：
```bash
0 2 * * * /opt/labor-risk/backup.sh
```

### 5. 自动恢复策略

```yaml
# docker-compose.yml 中已配置 restart: unless-stopped
# Docker会自动重启崩溃的容器

# 更高级的自动恢复:
# 1. 使用 systemd 管理 Docker
# 2. 配置健康检查 + 自动重启
# 3. 多实例负载均衡
```

---

## 故障排查

### 常见问题

#### 1. 服务无法启动

```bash
# 检查容器状态
docker ps -a

# 查看启动日志
docker logs labor-risk-api
docker logs labor-risk-nginx

# 常见原因:
# - .env 文件未配置 → 复制 .env.example 并填写
# - 端口被占用 → lsof -i :8000 / lsof -i :80
# - 权限问题 → chmod +x deploy.sh
```

#### 2. API返回502 Bad Gateway

```bash
# 检查API是否正常运行
curl http://localhost:8000/

# 检查Nginx配置
docker exec labor-risk-nginx nginx -t

# 重启Nginx
docker compose restart nginx
```

#### 3. SSL证书错误

```bash
# 检查证书是否存在
ls -la ssl/

# 检查证书有效期
openssl x509 -in ssl/fullchain.pem -noout -dates

# 重新申请
./deploy.sh ssl your-domain.com
```

#### 4. 性能缓慢

```bash
# 检查资源占用
docker stats

# 检查AI API响应时间
time curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"case":{...},"type":"labor"}'

# 优化措施:
# - 增加 worker 数量
# - 启用 Gzip 压缩 (已在nginx.conf中配置)
# - 配置CDN缓存静态资源
```

---

## 附录: 成本估算

| 资源 | 月费用估算 |
|------|-----------|
| ECS 2核4G | ¥100-150 |
| 带宽 5Mbps | ¥50-80 |
| 域名 | ¥10 (首年) |
| SSL证书 | 免费 (Let's Encrypt) |
| CDN (按量) | ¥20-50 |
| **合计** | **¥180-290/月** |

如需更高可用性，可考虑双机热备 + 负载均衡，成本约翻倍。

---

> 📞 如需技术支持或有疑问，请查看项目 Wiki 或提交 Issue。
>
> 最后更新: 2025-04-07
