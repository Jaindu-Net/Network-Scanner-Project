import socket
import argparse
import concurrent.futures 
import ipaddress 
from datetime import datetime
import json 

# Terminal color codes for professional output
G = '\033[92m'  # Green
C = '\033[96m'  # Cyan
Y = '\033[93m'  # Yellow
B = '\033[94m'  # Blue
RD = '\033[91m' # Red
R = '\033[0m'   # Reset

# ==============================================================
# PHASE 1: CORE NETWORKING & SCAN LOGIC
# Developed by Member 1: Jaindu
# ==============================================================

def get_service_name(port):
    """ Attempt to resolve the standard service name for a given TCP port """
    try:
        return socket.getservbyport(port, "tcp")
    except:
        return "unknown"

def scan_port(ip, port):
    """ Attempt a TCP connection to determine if the specified port is open """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.2) # Optimized for faster scanning
    try:
        result = s.connect_ex((ip, port))
        if result == 0:
            service = get_service_name(port)
            print(f"{G}  {port:>5}/TCP    {service:<15}  OPEN    ->  {ip}{R}")
            
            return {
                "ip": ip,
                "port": port,
                "service": service,
                "state": "OPEN"
            }
    except:
        pass
    finally:
        s.close()
    return None 

# ==============================================================
# PHASE 3: ADVANCED HYBRID MULTI-LEVEL THREADING ENGINE
# Developed by Member 3: Sathira 
# ==============================================================

def threaded_scan(target, start_port, end_port, threads):
    # ---------------------------------------------------------
    # SUBNET PARSING & DNS RESOLUTION LOGIC (START)
    # Developed by Member 1: Jaindu
    # ---------------------------------------------------------
    target_str = str(target)
    try:
        # First, try to parse as IP or CIDR Subnet
        network = ipaddress.ip_network(target, strict=False)
        if network.num_addresses == 1:
            ip_list = [str(network.network_address)]
        else:
            ip_list = [str(ip) for ip in network.hosts()]
    except ValueError:
        # If it fails, assume it's a domain name and try DNS Resolution
        try:
            resolved_ip = socket.gethostbyname(target)
            ip_list = [resolved_ip]
            print(f"\n{Y}[*] Resolved Domain: {C}{target}{Y} -> {G}{resolved_ip}{R}")
            target_str = f"{target} ({resolved_ip})"
        except socket.gaierror:
            print(f"\n{RD}[!] CRITICAL ERROR: Invalid Target IP or Unreachable Domain '{target}'.{R}")
            return None
    # ---------------------------------------------------------
    # SUBNET PARSING & DNS RESOLUTION LOGIC (END)
    # ---------------------------------------------------------

    range_info = f"{start_port} to {end_port}"
    time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    total_hosts = len(ip_list)

    # UI: Detailed Scan Information Table
    print(f"\n{B}┌──────────────────────────────────────────────────────────┐{R}")
    print(f"{B}│ {C}SCAN INFORMATION                                         {B}│{R}")
    print(f"{B}├──────────────────────────────────────────────────────────┤{R}")
    print(f"{B}│ {Y}Target(s)      : {C}{target_str:<39} {B}│{R}")
    print(f"{B}│ {Y}Total Hosts    : {C}{str(total_hosts):<39} {B}│{R}")
    print(f"{B}│ {Y}Port Range     : {C}{range_info:<39} {B}│{R}")
    print(f"{B}│ {Y}Threads Used   : {C}{str(threads):<39} {B}│{R}")
    print(f"{B}│ {Y}Started At     : {C}{time_now:<39} {B}│{R}")
    print(f"{B}└──────────────────────────────────────────────────────────┘{R}\n")
    
    t1 = datetime.now() 
    open_ports_data = [] 

    # ---------------------------------------------------------
    # HYBRID EXECUTION LOGIC (START)
    # Developed by Member 3: Sathira
    # ---------------------------------------------------------
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        scan_tasks = []
        for ip in ip_list:
            for port in range(start_port, end_port + 1):
                scan_tasks.append(executor.submit(scan_port, ip, port))
                
        for future in concurrent.futures.as_completed(scan_tasks):
            result_data = future.result()
            if result_data: 
                open_ports_data.append(result_data)
    # ---------------------------------------------------------
    # HYBRID EXECUTION LOGIC (END)
    # ---------------------------------------------------------
                
    t2 = datetime.now() 
    time_display = str(t2 - t1)[:-3] 
    
    # UI: Scan completion dashboard
    print(f"\n{B}┌──────────────────────────────────────────────────────────┐{R}")
    print(f"{B}│ {G}SCAN COMPLETE!                                           {B}│{R}")
    print(f"{B}├──────────────────────────────────────────────────────────┤{R}")
    print(f"{B}│ {Y}Total Time Taken : {C}{time_display:<37} {B}│{R}")
    print(f"{B}└──────────────────────────────────────────────────────────┘{R}\n")

    # ==============================================================
    # PHASE 5: ENTERPRISE REPORTING ENGINE (JSON EXPORT)
    # Developed by Member 1: Jaindu
    # ==============================================================
    print(f"{Y}[*] Generating Ultra-Premium JSON Report...{R}")
    
    critical_ports = {
        21: "FTP - Cleartext data transfer (High Risk)",
        23: "Telnet - Cleartext communication (Critical Risk)",
        22: "SSH - Secure but requires strong credentials",
        80: "HTTP - Unencrypted web traffic (Medium Risk)",
        443: "HTTPS - Encrypted web traffic (Low Risk)",
        445: "SMB - Target for Ransomware/WannaCry (Critical Risk)",
        3389: "RDP - Remote Desktop Protocol (High Risk)",
        3306: "MySQL - Database access (Medium Risk)"
    }

    structured_results = {}
    for entry in open_ports_data:
        ip = entry["ip"]
        port = entry["port"]
        
        if ip not in structured_results:
            structured_results[ip] = {
                "host_status": "UP",
                "total_open_ports": 0,
                "overall_risk": "Low",
                "open_ports": []
            }
            
        sec_note = critical_ports.get(port, "Standard network service")
        
        if port in [21, 23, 445, 3389]:
            structured_results[ip]["overall_risk"] = "Critical"
        elif port in [22, 80, 3306] and structured_results[ip]["overall_risk"] != "Critical":
            structured_results[ip]["overall_risk"] = "Medium"
            
        structured_results[ip]["open_ports"].append({
            "port": port, "service": entry["service"], "state": entry["state"], "security_note": sec_note
        })
        structured_results[ip]["total_open_ports"] += 1

    for ip in structured_results:
        structured_results[ip]["open_ports"] = sorted(structured_results[ip]["open_ports"], key=lambda x: x["port"])

    report_content = {
        "scan_metadata": {
            "tool_name": "NexScan Pro Auditing Suite",
            "version": "1.0",
            "target_network": target_str,
            "port_range_scanned": range_info,
            "scan_start_time": time_now,
            "total_execution_time": time_display,
            "thread_workers_used": threads,
            "total_active_hosts": len(structured_results)
        },
        "scan_results": structured_results
    }

    filename_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"scan_report_{filename_time}.json"

    with open(report_filename, "w") as json_file:
        json.dump(report_content, json_file, indent=4, sort_keys=True)

    print(f"{G}[+] Successfully saved enterprise report to: {report_filename}{R}")
    return report_filename 

# ==============================================================
# PHASE 4: CLI INTERFACE & ASCII BANNER
# Developed by Member 2: Dinara
# ==============================================================

if __name__ == "__main__":
    banner = f"""{C}
  _   _          _____                             _____  _____   ____  
 | \ | |        / ____|                           |  __ \|  __ \ / __ \ 
 |  \| | _____ | (___     ___ __ _ _ __           | |__) | |__) | |  | |
 | . ` |/ _ \ \/ \___ \  / __/ _` | '_  \         |  ___/|  _  /| |  | |
 | |\  |  __/>  <____) || (_| (_| | | | |         | |    | | \ \| |__| |
 |_| \_|\___/_/\_\_____/ \___\__,_|_| |_|         |_|    |_|  \_\\_____/ 
                                        
 {B}════════════════════════════════════════════════════════════════════════════════════
                        {Y}NexScan Pro - Network Auditing Suite
 {B}════════════════════════════════════════════════════════════════════════════════════{R}"""
    print(banner)
    
    parser = argparse.ArgumentParser(description="NexScan Pro - Professional Network Port Scanner")
    parser.add_argument("target", help="Target IP, CIDR, or Domain Name")
    parser.add_argument("-s", "--start", type=int, default=1, help="Start port")
    parser.add_argument("-e", "--end", type=int, default=100, help="End port")
    parser.add_argument("-t", "--threads", type=int, default=100, help="Threads")
    
    args = parser.parse_args()
    threaded_scan(args.target, args.start, args.end, args.threads)