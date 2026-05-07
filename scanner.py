import socket
import argparse
import concurrent.futures 
import ipaddress 
from datetime import datetime
import json 
import logging
import threading 
import sys       
import time

# ==============================================================================
# CROSS-PLATFORM OS HANDLER & WINDOWS ERROR SILENCER
# ==============================================================================
if sys.platform.startswith('win'):
    def silent_thread_errors(args):
        if issubclass(args.exc_type, OSError) and getattr(args.exc_value, 'errno', None) in (9, 22):
            pass
        else:
            sys.__excepthook__(args.exc_type, args.exc_value, args.exc_traceback)

    threading.excepthook = silent_thread_errors

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import IP, TCP, send, sniff

# ==============================================================================
# TERMINAL COLOR CODES
# ==============================================================================
G = '\033[92m'  
C = '\033[96m'  
Y = '\033[93m'  
B = '\033[94m'  
RD = '\033[91m' 
R = '\033[0m'   

# ==============================================================================
# START OF PHASE 1: CORE NETWORKING & SCAN LOGIC (SINGLE SNIFFER ARCHITECTURE)
# Primary Developer: Jaindu
# Features: Async Packet Sending, Centralized Sniffing, Banner Grabbing
# ==============================================================================

def get_service_name(port):
    try:
        return socket.getservbyport(port, "tcp")
    except:
        return "unknown"

def grab_banner(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.5)
        s.connect((ip, port))
        
        if port in [80, 8080, 443]:
            s.send(b"HEAD / HTTP/1.1\r\n\r\n")
            
        banner = s.recv(1024).decode('utf-8', errors='ignore').strip()
        s.close()
        
        if banner:
            return banner.split('\n')[0].strip()[:40]
    except:
        pass
    return "Version Unknown"

def send_syn_packet(ip, port):
    """ Fire-and-forget raw SYN packet sender """
    try:
        syn_packet = IP(dst=ip)/TCP(dport=port, flags="S")
        send(syn_packet, verbose=0)
    except Exception:
        pass

def background_sniffer(target_ips, stop_event, open_ports_data):
    """ Single centralized sniffer to catch all SYN-ACK replies """
    def packet_callback(packet):
        if packet.haslayer(TCP) and packet.haslayer(IP):
            if packet[IP].src in target_ips and packet.getlayer(TCP).flags == 0x12:
                ip = packet[IP].src
                port = packet.getlayer(TCP).sport 
                
                if not any(d.get('port') == port and d.get('ip') == ip for d in open_ports_data):
                    service = get_service_name(port)
                    version = grab_banner(ip, port)
                    
                    if version != "Version Unknown":
                        service_display = f"{service} [{version}]"
                    else:
                        service_display = service
                    
                    print(f"{G}  {port:>5}/TCP    {service_display:<35}  OPEN (SYN)  ->  {ip}{R}")
                    
                    open_ports_data.append({
                        "ip": ip,
                        "port": port,
                        "service": service_display,
                        "state": "OPEN"
                    })

    target_filter = " or ".join([f"src host {ip}" for ip in target_ips])
    sniff_filter = f"tcp and ({target_filter})"

    while not stop_event.is_set():
        sniff(filter=sniff_filter, prn=packet_callback, store=0, timeout=1)

# ==============================================================================
# END OF PHASE 1: CORE NETWORKING & SCAN LOGIC (Jaindu)
# ==============================================================================


# ==============================================================================
# START OF PHASE 2 & 3: TARGET PARSING & HYBRID MULTI-LEVEL THREADING ENGINE
# Primary Developer: Sathira (Orchestration logic by Dinara)
# Subnet Parsing Developer: Jaindu
# ==============================================================================

def threaded_scan(target, start_port, end_port, threads):
    # ---------------------------------------------------------
    # START OF SUBNET PARSING & DNS RESOLUTION LOGIC
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
    # ---------------------------------------------------------
    # END OF SUBNET PARSING & DNS RESOLUTION LOGIC (Jaindu)
    # ---------------------------------------------------------

    range_info = f"{start_port} to {end_port}"
    time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    total_hosts = len(ip_list)

    print(f"\n{B}┌──────────────────────────────────────────────────────────┐{R}")
    print(f"{B}│ {C}SCAN INFORMATION (PRO SNIFFER ENGINE)                    {B}│{R}")
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
    # START OF SNIFFER ORCHESTRATION & ASYNC EXECUTION
    # Developed by: Dinara
    # ---------------------------------------------------------
    stop_event = threading.Event()

    # Start the background sniffer thread
    sniffer_thread = threading.Thread(
        target=background_sniffer,
        args=(ip_list, stop_event, open_ports_data),
        daemon=True
    )
    sniffer_thread.start()

    # Dispatch SYN packets using Sathira's thread pool architecture
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        for ip in ip_list:
            for port in range(start_port, end_port + 1):
                executor.submit(send_syn_packet, ip, port)

    # Allow 2 seconds for late packets to arrive (Dinara)
    time.sleep(2.0)
    
    # Signal sniffer to stop and wait for it to finish
    stop_event.set()
    sniffer_thread.join()
    # ---------------------------------------------------------
    # END OF SNIFFER ORCHESTRATION & ASYNC EXECUTION (Dinara)
    # ---------------------------------------------------------
    
    t2 = datetime.now() 
    time_display = str(t2 - t1)[:-3] 
    
    print(f"\n{B}┌──────────────────────────────────────────────────────────┐{R}")
    print(f"{B}│ {G}SCAN COMPLETE!                                           {B}│{R}")
    print(f"{B}├──────────────────────────────────────────────────────────┤{R}")
    print(f"{B}│ {Y}Total Time Taken : {C}{time_display:<37} {B}│{R}")
    print(f"{B}└──────────────────────────────────────────────────────────┘{R}\n")

# ==============================================================================
# END OF PHASE 2 & 3: TARGET PARSING & HYBRID THREADING ENGINE (Sathira/Dinara)
# ==============================================================================


    # ==============================================================================
    # START OF PHASE 5: ENTERPRISE REPORTING ENGINE & RISK ASSESSMENT
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
            "version": "2.0 (Unified Sniffer Engine)",
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
    # END OF PHASE 5: ENTERPRISE REPORTING ENGINE & RISK ASSESSMENT (Jaindu)
    # ==============================================================================


# ==============================================================================
# START OF PHASE 4: COMMAND LINE INTERFACE (CLI) & ASCII BANNER
# Primary Developer: Dinara
# ==============================================================================

if __name__ == "__main__":
    banner = f"""{C}
  _   _          _____                                  _____  _____   ____  
 | \ | |        / ____|                                |  __ \|  __ \ / __ \ 
 |  \| | _____ | (___   ___ __ _ _ __                  | |__) | |__) | |  | |
 | . ` |/ _ \ \/ \___ \ / __/ _` | '_ \\                |  ___/|  _  /| |  | |
 | |\  |  __/>  <____) | (_| (_| | | | |               | |    | | \ \| |__| |
 |_| \_|\___/_/\_\_____/ \___\__,_|_| |_|              |_|    |_|  \_\\____/ 
                                        
 {B}════════════════════════════════════════════════════════════════════════════════════
         {Y}NexScan Pro - Network Auditing Suite {RD}[STEALTH + VERSION MODE]{Y}
 {B}════════════════════════════════════════════════════════════════════════════════════{R}"""
    print(banner)
    
    parser = argparse.ArgumentParser(description="NexScan Pro - Professional Network Port Scanner")
    parser.add_argument("target", help="Target IP, CIDR, or Domain Name (e.g., 192.168.1.1, 10.0.0.0/24, example.com)")
    parser.add_argument("-s", "--start", type=int, default=1, help="Start port (Default: 1)")
    parser.add_argument("-e", "--end", type=int, default=100, help="End port (Default: 100)")
    parser.add_argument("-t", "--threads", type=int, default=100, help="Number of concurrent threads (Default: 100)")
    
    args = parser.parse_args()
    
    threaded_scan(args.target, args.start, args.end, args.threads)

# ==============================================================================
# END OF PHASE 4: COMMAND LINE INTERFACE (CLI) (Dinara)
# ==============================================================================