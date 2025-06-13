#!/usr/bin/env python3
"""
Environment check script for Danmu TTS Server
Verifies all dependencies and system requirements
"""

import sys
import subprocess
import importlib
import os
from pathlib import Path


def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major == 3 and 9 <= version.minor <= 11:
        print("✅ Python version is compatible")
        return True
    else:
        print(
            f"⚠️  Python {version.major}.{version.minor} may have compatibility issues"
        )
        print("   Recommended: Python 3.9-3.11")
        return False


def check_package(package_name, import_name=None, required=True):
    """Check if a package is installed and importable"""
    if import_name is None:
        import_name = package_name

    try:
        module = importlib.import_module(import_name)
        version = getattr(module, "__version__", "unknown")
        status = "✅" if required else "📦"
        print(f"{status} {package_name}: {version}")
        return True
    except ImportError:
        status = "❌" if required else "⚪"
        print(f"{status} {package_name}: not installed")
        return not required


def check_gpu():
    """Check GPU availability and CUDA support"""
    print("\n🎮 GPU Information:")

    # Check NVIDIA driver
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,driver_version",
                "--format=csv,noheader",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    gpu_info = line.split(", ")
                    if len(gpu_info) >= 3:
                        print(f"  GPU: {gpu_info[0]}")
                        print(f"  Memory: {gpu_info[1]}")
                        print(f"  Driver: {gpu_info[2]}")
        else:
            print("❌ NVIDIA driver not found")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ nvidia-smi not available")
        return False

    # Check PyTorch CUDA
    try:
        import torch

        if torch.cuda.is_available():
            print(f"✅ PyTorch CUDA available")
            print(f"  CUDA version: {torch.version.cuda}")
            print(f"  cuDNN version: {torch.backends.cudnn.version()}")

            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                print(f"  Device {i}: {props.name}")
                print(f"    Memory: {props.total_memory / 1024**3:.1f} GB")
                print(f"    Compute: {props.major}.{props.minor}")
            return True
        else:
            print("⚠️  PyTorch installed but CUDA not available")
            return False
    except ImportError:
        print("❌ PyTorch not installed")
        return False


def check_audio_system():
    """Check audio system components"""
    print("\n🎵 Audio System:")

    # Check audio libraries
    audio_libs = [
        ("librosa", "librosa"),
        ("soundfile", "soundfile"),
        ("scipy", "scipy"),
        ("numpy", "numpy"),
    ]

    all_good = True
    for pkg, import_name in audio_libs:
        if not check_package(pkg, import_name):
            all_good = False

    return all_good


def check_tts_backends():
    """Check TTS backend availability"""
    print("\n🗣️  TTS Backends:")

    # Edge TTS
    edge_available = check_package("edge-tts", "edge_tts", required=False)

    # Piper TTS
    piper_available = False
    try:
        result = subprocess.run(["piper", "--help"], capture_output=True, timeout=5)
        if result.returncode == 0:
            print("✅ Piper TTS: available")
            piper_available = True
        else:
            print("❌ Piper TTS: not working")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Piper TTS: not installed")

    # XTTS (TTS library)
    xtts_available = False
    try:
        from TTS.api import TTS

        print("✅ XTTS (TTS library): available")
        xtts_available = True
    except ImportError:
        print("❌ XTTS (TTS library): not installed")

    return edge_available, piper_available, xtts_available


def check_web_dependencies():
    """Check web framework dependencies"""
    print("\n🌐 Web Framework:")

    web_deps = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("websockets", "websockets"),
        ("pydantic", "pydantic"),
    ]

    all_good = True
    for pkg, import_name in web_deps:
        if not check_package(pkg, import_name):
            all_good = False

    return all_good


def check_directories():
    """Check required directories"""
    print("\n📁 Directory Structure:")

    required_dirs = [
        "src",
        "src/backends",
        "logs",
        "cache",
        "models",
        "models/piper",
        "models/xtts",
    ]

    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✅ {dir_path}/")
        else:
            print(f"⚠️  {dir_path}/ (will be created)")
            path.mkdir(parents=True, exist_ok=True)


def check_config():
    """Check configuration files"""
    print("\n⚙️  Configuration:")

    config_files = [
        ("config.yaml", "Main configuration"),
        ("pyproject.toml", "Project metadata"),
        (".env", "Environment variables (optional)"),
    ]

    for file_path, description in config_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}: {description}")
        else:
            print(f"⚪ {file_path}: {description} (missing)")


def check_uv():
    """Check UV package manager"""
    print("\n📦 UV Package Manager:")

    try:
        result = subprocess.run(
            ["uv", "--version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ UV: {version}")
            return True
        else:
            print("❌ UV: not working")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ UV: not installed")
        print("   Install with: curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False


def performance_recommendations():
    """Provide performance recommendations"""
    print("\n🚀 Performance Recommendations:")

    # Check available memory
    try:
        import psutil

        memory = psutil.virtual_memory()
        print(f"💾 System RAM: {memory.total / 1024**3:.1f} GB")

        if memory.total < 8 * 1024**3:
            print("⚠️  Consider adding more RAM for better performance")
        elif memory.total < 16 * 1024**3:
            print("✅ RAM sufficient for basic usage")
        else:
            print("✅ Excellent RAM for high-performance usage")
    except ImportError:
        print("💾 Install psutil to check system memory")

    # Check disk space
    try:
        import shutil

        free_space = shutil.disk_usage(".").free
        print(f"💿 Free disk space: {free_space / 1024**3:.1f} GB")

        if free_space < 5 * 1024**3:
            print("⚠️  Low disk space, consider cleanup")
        else:
            print("✅ Sufficient disk space")
    except:
        print("💿 Could not check disk space")


def main():
    """Main check function"""
    print("🔍 Danmu TTS Server Environment Check")
    print("=" * 50)

    # Core checks
    python_ok = check_python_version()
    web_ok = check_web_dependencies()
    audio_ok = check_audio_system()

    # GPU check
    gpu_ok = check_gpu()

    # TTS backends
    edge_ok, piper_ok, xtts_ok = check_tts_backends()

    # Structure checks
    check_directories()
    check_config()

    # Tools
    uv_ok = check_uv()

    # Performance info
    performance_recommendations()

    # Summary
    print("\n📊 Summary:")
    print("=" * 30)

    essential_ok = python_ok and web_ok and audio_ok and edge_ok

    if essential_ok:
        print("✅ Essential components: READY")
    else:
        print("❌ Essential components: INCOMPLETE")

    if gpu_ok and xtts_ok:
        print("✅ GPU acceleration: READY")
    else:
        print("⚠️  GPU acceleration: LIMITED")

    if uv_ok:
        print("✅ UV package manager: READY")
    else:
        print("⚠️  UV package manager: MISSING (recommended)")

    print("\n🎯 Next Steps:")

    if not essential_ok:
        print("1. Install missing essential dependencies")
        print("   Run: ./setup.sh")

    if not gpu_ok and xtts_ok:
        print("2. Setup GPU acceleration for best quality")
        print("   Install: PyTorch with CUDA")

    if not uv_ok:
        print("3. Install UV for faster package management")
        print("   Run: curl -LsSf https://astral.sh/uv/install.sh | sh")

    if essential_ok:
        print("🚀 Ready to start server!")
        print("   Run: ./start_server.sh")
        print("   Or:  ./dev.sh (development mode)")


if __name__ == "__main__":
    main()
