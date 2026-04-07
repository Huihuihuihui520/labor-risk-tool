#!/bin/bash
# ============================================
# 产房风险决策辅助系统 - 一键部署脚本
# ============================================
# 使用方法: chmod +x deploy.sh && ./deploy.sh [命令]
# 命令: deploy | update | stop | restart | logs | status | ssl

set -e

PROJECT_NAME="labor-risk"
DOCKER_COMPOSE="docker compose"
SERVER_IP="${1:-}"
DOMAIN="${2:-}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_prerequisites() {
    log_info "检查运行环境..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose 未安装"
        exit 1
    fi
    
    log_info "环境检查通过 ✓"
}

init_env() {
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            log_warn "已创建 .env 文件，请编辑配置 API_KEY 等参数"
        else
            log_error ".env.example 文件不存在"
            exit 1
        fi
    fi
}

create_directories() {
    mkdir -p ssl logs static/css
}

deploy() {
    check_prerequisites
    init_env
    create_directories
    
    log_info "开始部署 ${PROJECT_NAME}..."
    
    # 构建镜像
    log_info "构建 Docker 镜像..."
    $DOCKER_COMPOSE build --no-cache api
    
    # 启动服务
    log_info "启动服务..."
    $DOCKER_COMPOSE up -d
    
    # 等待健康检查
    log_info "等待服务启动..."
    sleep 10
    
    # 检查状态
    status
}

update() {
    log_info "更新 ${PROJECT_NAME}..."
    
    # 拉取最新代码 (如果是 Git 仓库)
    if [ -d .git ]; then
        git pull origin main || true
    fi
    
    # 重新构建并启动
    $DOCKER_COMPOSE build api
    $DOCKER_COMPOSE up -d --force-recreate api nginx
    
    log_info "更新完成 ✓"
}

stop() {
    log_info "停止服务..."
    $DOCKER_COMPOSE down
}

restart() {
    stop
    sleep 2
    deploy
}

logs() {
    $DOCKER_COMPOSE logs -f --tail=100 ${1:-}
}

status() {
    echo ""
    log_info "=== 服务状态 ==="
    $DOCKER_COMPOSE ps
    
    echo ""
    log_info "=== 服务健康检查 ==="
    
    if curl -sf http://localhost/health > /dev/null 2>&1; then
        log_info "Nginx: 运行正常 ✓"
    else
        log_warn "Nginx: 无法访问"
    fi
    
    if curl -sf http://localhost:8000/ > /dev/null 2>&1; then
        log_info "API: 运行正常 ✓"
    else
        log_warn "API: 无法访问"
    fi
    
    echo ""
    log_info "=== 资源使用 ==="
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

ssl_setup() {
    DOMAIN=$1
    EMAIL=${2:-admin@your-domain.com}
    
    if [ -z "$DOMAIN" ]; then
        log_error "用法: ./deploy.sh ssl <域名> [邮箱]"
        exit 1
    fi
    
    log_info "申请 SSL 证书: ${DOMAIN}"
    
    # 安装 certbot
    if ! command -v certbot &> /dev/null; then
        apt-get update && apt-get install -y certbot python3-certbot-nginx
    fi
    
    # 申请证书
    certbot certonly --standalone -d "$DOMAIN" --email "$EMAIL" --agree-tos --non-interactive
    
    # 复制证书到项目目录
    cp "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" ssl/fullchain.pem
    cp "/etc/letsencrypt/live/${DOMAIN}/privkey.pem" ssl/privkey.pem
    
    log_info "SSL 证书安装完成 ✓"
    log_info "重启 Nginx 使配置生效..."
    $DOCKER_COMPOSE restart nginx
}

case "${1:-help}" in
    deploy)   deploy ;;
    update)  update ;;
    stop)    stop ;;
    restart) restart ;;
    logs)    logs "${2:-}" ;;
    status)  status ;;
    ssl)     ssl_setup "$2" "$3" ;;
    help|*)   echo "
产房风险决策辅助系统 - 部署脚本
=====================================

用法: ./deploy.sh <命令> [参数]

命令:
  deploy              首次部署（构建+启动）
  update              更新代码并重新部署
  stop                停止所有服务
  restart             重启所有服务
  logs [service]      查看日志 (api/nginx)
  status              查看服务状态和健康检查
  ssl <domain> [email]  申请SSL证书

示例:
  ./deploy.sh deploy                    # 首次部署
  ./deploy.sh update                   # 更新部署
  ./deploy.sh logs api                  # 查看API日志
  ./deploy.sh ssl your-hospital.com admin@hospital.com  # 配置SSL
"
esac
