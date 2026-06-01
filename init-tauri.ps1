#!/bin/bash
# Tauri 项目初始化脚本

echo "开始初始化 Tauri 项目..."

# 检查 Rust 是否安装
if ! command -v rustc &> /dev/null; then
    echo "❌ Rust 未安装，请先安装 Rust"
    echo "下载地址: https://rustup.rs/"
    exit 1
fi

# 检查 Node.js 是否安装
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js"
    echo "下载地址: https://nodejs.org/"
    exit 1
fi

echo "✅ 环境检查通过"
echo ""
echo "下一步操作："
echo "1. 在终端中运行: npx tauri init"
echo "2. 按照提示输入配置信息"
echo "3. 然后运行: npm run tauri dev"
echo ""
echo "或者直接运行以下命令一键初始化："
echo "npm run tauri dev"
