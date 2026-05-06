#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
贵州旅游综合推荐系统 - 启动脚本
自动检查环境并启动Flask应用
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 7):
        print("❌ 需要Python 3.7或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    print(f"✓ Python版本: {sys.version.split()[0]}")
    return True


def check_dependencies():
    """检查并安装依赖"""
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt文件不存在")
        return False

    try:
        import flask, flask_cors, pandas, jieba, wordcloud
        print("✓ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"⚠ 缺少依赖包: {e}")
        print("正在安装依赖...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✓ 依赖安装完成")
            return True
        except subprocess.CalledProcessError:
            print("❌ 依赖安装失败")
            return False


def check_data_files():
    """检查数据文件"""
    data_file = Path("贵州景点基本信息.csv")
    if not data_file.exists():
        print("⚠ 主数据文件不存在，正在创建示例数据...")
        try:
            from setup import create_sample_data
            create_sample_data()
            print("✓ 示例数据创建完成")
        except Exception as e:
            print(f"❌ 创建示例数据失败: {e}")
            return False
    else:
        print("✓ 数据文件存在")
    return True


def check_directories():
    """检查并创建必要目录"""
    directories = [
        'static/css', 'static/js', 'static/images',
        'templates', 'wordcloud_images', '景点评论'
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

    print("✓ 目录结构检查完成")
    return True


def start_server():
    """启动Flask服务器"""
    try:
        print("\n🚀 启动服务器...")
        print("=" * 50)
        print("📍 访问地址:")
        print("  - 主页: http://127.0.0.1:5000/")
        print("  - 景点推荐: http://127.0.0.1:5000/recommend")
        print("  - API文档: http://127.0.0.1:5000/api/")
        print("=" * 50)
        print("按 Ctrl+C 停止服务器\n")

        # 启动app.py
        import app
        app.app.run(debug=True, host='127.0.0.1', port=5000)

    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False
    return True


def main():
    """主函数"""
    print("🌟 贵州旅游综合推荐系统")
    print("=" * 50)

    # 检查Python版本
    if not check_python_version():
        sys.exit(1)

    # 检查依赖
    if not check_dependencies():
        sys.exit(1)

    # 检查目录结构
    if not check_directories():
        sys.exit(1)

    # 检查数据文件
    if not check_data_files():
        sys.exit(1)

    print("✅ 环境检查完成")

    # 启动服务器
    start_server()


if __name__ == "__main__":
    main()