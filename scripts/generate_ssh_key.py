#!/usr/bin/env python3
"""
SSH 密钥生成工具
使用 Python 生成 RSA 或 Ed25519 SSH 密钥对
"""

import sys
import os
from pathlib import Path
from datetime import datetime

try:
    import cryptography
    from cryptography.hazmat.primitives.asymmetric import rsa, ed25519
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend
except ImportError:
    print("❌ 缺少 cryptography 库")
    print("请安装: pip install cryptography")
    sys.exit(1)


def generate_rsa_key():
    """生成 RSA 密钥对"""
    print("🔐 生成 RSA 密钥对...")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
    )

    # 生成私钥（不加密）
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    # 生成公钥
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH
    )

    return private_pem.decode('utf-8'), public_pem.decode('utf-8')


def generate_ed25519_key():
    """生成 Ed25519 密钥对"""
    print("🔐 生成 Ed25519 密钥对...")
    private_key = ed25519.Ed25519PrivateKey.generate()

    # 生成私钥
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption()
    )

    # 生成公钥
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH
    )

    return private_pem.decode('utf-8'), public_pem.decode('utf-8')


def save_key_pair(private_key, public_key, key_type="id_rsa"):
    """保存密钥对到文件"""
    # 创建 .ssh 目录
    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(mode=0o700, exist_ok=True)

    # 保存私钥
    private_key_path = ssh_dir / key_type
    with open(private_key_path, "w") as f:
        f.write(private_key)
    private_key_path.chmod(0o600)
    print(f"✅ 私钥已保存: {private_key_path}")

    # 保存公钥
    public_key_path = ssh_dir / f"{key_type}.pub"
    with open(public_key_path, "w") as f:
        f.write(public_key)
    public_key_path.chmod(0o644)
    print(f"✅ 公钥已保存: {public_key_path}")

    return private_key_path, public_key_path


def main():
    print("=" * 60)
    print("🔑 SSH 密钥生成工具")
    print("=" * 60)
    print()

    # 选择密钥类型
    print("请选择密钥类型:")
    print("1. Ed25519 (推荐，更安全、更快)")
    print("2. RSA 4096 (兼容性更好)")
    choice = input("请输入选项 (1/2, 默认 1): ").strip() or "1"

    # 生成密钥
    if choice == "1":
        key_type = "id_ed25519"
        private_key, public_key = generate_ed25519_key()
    elif choice == "2":
        key_type = "id_rsa"
        private_key, public_key = generate_rsa_key()
    else:
        print("❌ 无效的选项")
        sys.exit(1)

    # 保存密钥
    print()
    print("💾 保存密钥对...")
    private_key_path, public_key_path = save_key_pair(private_key, public_key, key_type)

    # 显示公钥
    print()
    print("=" * 60)
    print("📤 公钥内容（复制以下内容到 GitHub）:")
    print("=" * 60)
    print()
    print(public_key)
    print()
    print("=" * 60)

    # 显示添加到 GitHub 的步骤
    print()
    print("📋 下一步操作:")
    print()
    print("1. 访问 GitHub SSH 设置:")
    print("   https://github.com/settings/keys")
    print()
    print("2. 点击 'New SSH key'")
    print()
    print("3. 粘贴上面显示的公钥")
    print()
    print("4. 点击 'Add SSH key'")
    print()
    print("5. 添加完成后，运行以下命令测试连接:")
    print(f"   ssh -T git@github.com -i {private_key_path}")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
