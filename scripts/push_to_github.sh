#!/bin/bash

# ============================================================
# Git 推送辅助脚本
# ============================================================

echo "Docker Agent 代码推送脚本"
echo "========================"
echo ""
echo "当前分支: $(git branch --show-current)"
echo ""
echo "待推送的提交:"
git log origin/dev..HEAD --oneline
echo ""
echo "请选择推送方式:"
echo "1. 使用 HTTPS (需要 GitHub Token)"
echo "2. 使用 SSH (需要 SSH 密钥)"
echo "3. 手动推送"
echo ""
read -p "请输入选项 (1/2/3): " choice

case $choice in
    1)
        echo ""
        echo "使用 HTTPS 推送..."
        echo ""
        echo "请输入 GitHub Token (Personal Access Token):"
        read -s token
        echo ""
        echo ""
        # 使用 Token 推送
        git remote set-url origin https://$token@github.com/fanjn-zetyun/docker-Agent.git
        git push origin dev
        # 恢复原始 URL
        git remote set-url origin https://github.com/fanjn-zetyun/docker-Agent.git
        ;;
    2)
        echo ""
        echo "使用 SSH 推送..."
        git remote set-url origin git@github.com:fanjn-zetyun/docker-Agent.git
        git push origin dev
        ;;
    3)
        echo ""
        echo "请手动执行以下命令:"
        echo ""
        echo "git push origin dev"
        echo ""
        ;;
    *)
        echo "无效的选项"
        exit 1
        ;;
esac

echo ""
echo "推送完成！"
