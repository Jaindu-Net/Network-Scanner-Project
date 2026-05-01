# 🔍 Network Discovery & Auditing Tool

> A high-performance, multi-threaded TCP Port Scanner built with Python. This tool is designed for internal auditing, network discovery, and vulnerability assessment, providing a fast and professional command-line experience.

---

## 🚀 Features

- ⚡ **High-Speed Scanning:** Utilizes `concurrent.futures` for multi-threading, allowing hundreds of ports to be scanned across multiple hosts in milliseconds.
- 🌐 **Advanced Subnet Support:** Seamlessly scan entire network blocks (CIDR notation, e.g., `192.168.1.0/24`) or target individual IP addresses.
- 🕵️ **Intelligent Service Detection:** Automatically resolves and displays the active service name (HTTP, SSH, FTP, etc.) for every open port.
- 💻 **Professional CLI:** Built with `argparse` to provide a smooth, hacker-style terminal interface with custom ASCII banners.
- 🎨 **Smart UI & Precision Tracking:** Features a borderless, color-coded table layout (Open ports in Green) and high-precision execution timing (calculated in milliseconds).
- 📦 **Zero Dependencies:** Uses only Python built-in libraries (`socket`, `argparse`, `ipaddress`, `concurrent.futures`). No external installations required.

---

## 🛠️ Setup Instructions

1. Clone the repository:
```bash
git clone [https://github.com/Jaindu-Net/Network-Scanner-Project.git](https://github.com/Jaindu-Net/Network-Scanner-Project.git)