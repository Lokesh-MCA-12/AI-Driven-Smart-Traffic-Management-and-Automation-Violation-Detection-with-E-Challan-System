# Requirements and Prerequisites

## Operating Systems
- **Windows**: Windows 10 or 11 (64-bit) with WSL2 recommended.
- **Linux**: Ubuntu 20.04 LTS or newer.
- **macOS**: Apple Silicon M1/M2/M3 or Intel (macOS 12+).

## Minimum Hardware Requirements
- **CPU**: 4-Core x86_64 or ARM64 processor.
- **RAM**: 8 GB.
- **GPU**: NVIDIA GTX 1050 (or comparable) with 4GB VRAM for CUDA acceleration. (Optional, CPU fallback is supported).
- **Disk**: 10 GB free space (increases depending on video capture duration).

## Recommended Hardware Requirements
- **CPU**: 8-Core Intel Core i7 / AMD Ryzen 7.
- **RAM**: 16 GB.
- **GPU**: NVIDIA RTX 3060 or better with 12GB VRAM (highly recommended for multiple concurrent camera streams).

## Software Prerequisites
- **Python**: 3.11.x
- **Node.js**: 18.x or 20.x
- **PostgreSQL**: 15.x or 16.x
- **Docker**: Docker CE and Docker Compose v2
- **Nginx**: 1.24+ (if deployed bare-metal)
- **Git**: 2.40+
- **CUDA Toolkit & cuDNN**: Matching GPU specifications for GPU-accelerated PyTorch runs.
