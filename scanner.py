import socket
import argparse
import concurrent.futures 
import ipaddress 
from datetime import datetime
import json 
import logging
import threading 
import sys       

# ==============================================================================
# WINDOWS ERROR SILENCER (NINJA FIX)
# Suppresses specific Threading OSErrors (Errno 9) during Scapy teardown on Windows.
# ==============================================================================
def silent_thread_errors(args):
    """ Catch and suppress specific Threading OSErrors silently """
    if issubclass(args.exc_type, OSError) and getattr(args.exc_value, 'errno', None) == 9:
        pass
    else:
        sys.__excepthook__(args.exc_type, args.exc_value, args.exc_traceback)

threading.excepthook = silent_thread_errors

# Suppress Scapy runtime warnings for a cleaner CLI experience
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import IP, TCP, sr1

# ==============================================================================
# TERMINAL COLOR CODES
# ==============================================================================
G = '\033[92m'  # Green 
C = '\033[96m'  # Cyan 
Y = '\033[93m'  # Yellow 
B = '\033[94m'  # Blue 
RD = '\033[91m' # Red 
R = '\033[0m'   # Reset 

# ==============================================================================
# PHASE 1: CORE NETWORKING & SCAN LOGIC (STEALTH SYN UPGRADE)
# Primary Developer: Jaindu
# ==============================================================================

def get_service_name(port):
    """
    Attempts to resolve the standard service name (e.g., HTTP, SSH) 
    associated with a specific TCP port.
    """
    try:
        return socket.getservbyport(port, "tcp")
    except:
        return "unknown"

def stealth_scan_port(ip, port):
    """
    Executes a Stealth SYN (Half-Open) TCP scan using the Scapy library.
    Requires Administrative/Root privileges.
    """
    try:
        syn_packet = IP(dst=ip)/TCP(dport=port, flags="S")
        response = sr1(syn_packet, timeout=2.0, verbose=0)
        
        if response is None:
            return None 
            
        elif response.haslayer(TCP):
            if response.getlayer(TCP).flags == 0x12:
                service = get_service_name(port)
                
                print(f"{G}  {port:>5}/TCP    {service:<15}  OPEN (SYN)  ->  {ip}{R}")
                
                return {
                    "ip": ip,
                    "port": port,
                    "service": service,
                    "state": "OPEN"
                }
            
            elif response.getlayer(TCP).flags == 0x14:
                return None
                
    except Exception as e:
        pass
        
    return None

# ==============================================================================
# PHASE 2 & 3: TARGET PARSING & HYBRID MULTI-LEVEL THREADING ENGINE
# Primary Developer: Sathira
# ==============================================================================

def threaded_scan(target, start_port, end_port, threads):
    # ---------------------------------------------------------
    # SUBNET PARSING & DNS RESOLUTION LOGIC
    # Developed by: Jaindu
    # ---------------------------------------------------------
    target_str = str(target)
    try:
        network = ipaddress.ip_network(target, strict=False)
        if network.num_addresses == 1:
            ip_list = [str(network.network_address)]
        else:
            ip_list = [str(ip) for ip in network.hosts()]
    except ValueError:
        try:
            resolved_ip = socket.gethostbyname(target)
            ip_list = [resolved_ip]
            print(f"\n{Y}[*] Resolved Domain: {C}{target}{Y} -> {G}{resolved_ip}{R}")
            target_str = f"{target} ({resolved_ip})"
        except socket.gaierror:
            print(f"\n{RD}[!] CRITICAL ERROR: DNS Resolution failed for '{target}'. Target unreachable.{R}")
            return None

    range_info = f"{start_port} to {end_port}"
    time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    total_hosts = len(ip_list)

    print(f"\n{B}┌──────────────────────────────────────────────────────────┐{R}")
    print(f"{B}│ {C}SCAN INFORMATION (STEALTH SYN MODE)                      {B}│{R}")
    print(f"{B}├──────────────────────────────────────────────────────────┤{R}")
    print(f"{B}│ {Y}Target(s)      : {C}{target_str:<39} {B}│{R}")
    print(f"{B}│ {Y}Total Hosts    : {C}{str(total_hosts):<39} {B}│{R}")
    print(f"{B}│ {Y}Port Range     : {C}{range_info:<39} {B}│{R}")
    print(f"{B}│ {Y}Threads Used   : {C}{str(threads):<39} {B}│{R}")
    print(f"{B}│ {Y}Started At     : {C}{time_now:<39} {B}│{R}")
    print(f"{B}└──────────────────────────────────────────────────────────┘{R}\n")
    
    t1 = datetime.now() 
    open_ports_data = [] 

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        scan_tasks = []
        for ip in ip_list:
            for port in range(start_port, end_port + 1):
                scan_tasks.append(executor.submit(stealth_scan_port, ip, port))
                
        for future in concurrent.futures.as_completed(scan_tasks):
            result_data = future.result()
            if result_data: 
                open_ports_data.append(result_data)
                
    t2 = datetime.now() 
    time_display = str(t2 - t1)[:-3] 
    
    print(f"\n{B}┌──────────────────────────────────────────────────────────┐{R}")
    print(f"{B}│ {G}SCAN COMPLETE!                                           {B}│{R}")
    print(f"{B}├──────────────────────────────────────────────────────────┤{R}")
    print(f"{B}│ {Y}Total Time Taken : {C}{time_display:<37} {B}│{R}")
    print(f"{B}└──────────────────────────────────────────────────────────┘{R}\n")

    # ==============================================================================
    # PHASE 5: ENTERPRISE REPORTING ENGINE & RISK ASSESSMENT
    # Primary Developer: Jaindu
    # ==============================================================================
    print(f"{Y}[*] Generating Enterprise JSON Security Report...{R}")
    
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
            "version": "1.1 (Stealth SYN Mode)",
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

# ==============================================================================
# PHASE 4: COMMAND LINE INTERFACE (CLI) & ASCII BANNER
# Primary Developer: Dinara
# ==============================================================================

if __name__ == "__main__":
    banner = f"""{C}
  _   _          _____                             _____  _____   ____  
 | \ | |        / ____|                           |  __ \|  __ \ / __ \ 
 |  \| | _____ | (___     ___ __ _ _ __           | |__) | |__) | |  | |
 | . ` |/ _ \ \/ \___ \  / __/ _` | '_  \         |  ___/|  _  /| |  | |
 | |\  |  __/>  <____) || (_| (_| | | | |         | |    | | \ \| |__| |
 |_| \_|\___/_/\_\_____/ \___\__,_|_| |_|         |_|    |_|  \_\\_____/ 
                                        
 {B}════════════════════════════════════════════════════════════════════════════════════
               {Y}NexScan Pro - Network Auditing Suite {RD}[STEALTH MODE]{Y}
 {B}════════════════════════════════════════════════════════════════════════════════════{R}"""
    print(banner)
    
    parser = argparse.ArgumentParser(description="NexScan Pro - Professional Network Port Scanner")
    parser.add_argument("target", help="Target IP, CIDR, or Domain Name (e.g., 192.168.1.1, 10.0.0.0/24, example.com)")
    parser.add_argument("-s", "--start", type=int, default=1, help="Start port (Default: 1)")
    parser.add_argument("-e", "--end", type=int, default=100, help="End port (Default: 100)")
    parser.add_argument("-t", "--threads", type=int, default=100, help="Number of concurrent threads (Default: 100)")
    
    args = parser.parse_args()
    
    threaded_scan(args.target, args.start, args.end, args.threads)