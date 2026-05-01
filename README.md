# 🔍 Network Discovery & Auditing Tool

> A high-performance, multi-threaded TCP Port Scanner built with Python. This tool is designed for internal auditing and network discovery, providing a fast and professional command-line experience.

---

## 🚀 Features

- ⚡ High-Speed Scanning: Utilizes `concurrent.futures` for multi-threading, allowing hundreds of ports to be scanned in seconds.
- 💻 Professional CLI: Built with `argparse` for a smooth, hacker-style terminal interface.
- 🎯 Customizable Targets: Scan specific subnets, custom port ranges, and define your own thread counts.
- 🎨 Smart UI: Color-coded outputs (Open ports in Green) and automated time-calculation for performance tracking.
- 📦 Zero Dependencies: Uses only Python built-in libraries (`socket`, `argparse`, `threading`). No external installations required.

---

## 🛠️ Setup Instructions

1. Clone the repository:
```bash
git clone [https://github.com/Jaindu-Net/Network-Scanner-Project.git](https://github.com/Jaindu-Net/Network-Scanner-Project.git)

2. Navigate to the project directory:
```bash
cd Network-Scanner-Project


## 💻 Usage Guide

You can run the tool directly from your terminal. Here are the common commands:

1. View the Help Menu
```bash
python scanner.py -h

2. Basic Single Target Scan (Default: Ports 1-100, 50 Threads)
```bash
python scanner.py 192.168.1.1

3. Custom Port Range & Thread Count
```bash
python scanner.py 192.168.1.1 -s 1 -e 1000 -t 200

4. Bulk Subnet (CIDR) Scanning (Scans all hosts in the subnet for a specific port)
```bash
python scanner.py 192.168.1.0/24 -s 80 -e 80 -t 500


## 👥 Development Team
Jaindu De Zoysa (COHNDNE25.1F-011) - Core Networking Logic, Subnet/CIDR Parsing & Service Resolution

Dinara Ganhewage (COHNDNE25.1F-044) - CLI Architecture, ASCII Banner & UI/UX Design

Sathira Dananjaya (COHNDNE25.1F-009) - High-Performance Concurrency & Multi-threading Engine