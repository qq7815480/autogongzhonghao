#!/bin/bash
# wechat-publisher 安装验证脚本
# 运行: bash ~/.hermes/skills/wechat-publisher/scripts/verify-setup.sh

set -e
SKILL_DIR="$HOME/.hermes/skills/wechat-publisher"
SCRIPTS="$SKILL_DIR/scripts"

echo "=== wechat-publisher 安装验证 ==="

# 1. 检查配置文件
if [ -f "$SKILL_DIR/wechat-publisher.yaml" ]; then
    echo "✅ wechat-publisher.yaml 存在"
else
    echo "❌ 缺少 wechat-publisher.yaml"
    echo "   运行: cp $SKILL_DIR/wechat-publisher.yaml.example $SKILL_DIR/wechat-publisher.yaml"
    exit 1
fi

# 2. 检查 Python 依赖
python3 -c "import requests, yaml" 2>/dev/null && echo "✅ requests + pyyaml 已安装" || {
    echo "❌ 缺少依赖"
    python3 -m pip install requests pyyaml
}

# 3. 验证 API 连通
cd "$SCRIPTS"
python3 -c "
from wechat_api import get_access_token
token = get_access_token()
print(f'✅ API 连通: {token[:10]}...')
" 2>&1 | grep -v NotOpenSSLWarning || echo "❌ API 连接失败，检查 AppID/AppSecret 和 IP 白名单"

# 4. 检查工作目录
mkdir -p "$SKILL_DIR/sunwork"
echo "✅ 工作目录: $SKILL_DIR/sunwork/"

echo ""
echo "=== 验证完成 ==="
