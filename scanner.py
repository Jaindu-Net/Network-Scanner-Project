import socket
import argparse
import concurrent.futures 
import ipaddress # Added for Subnet/CIDR parsing
from datetime import datetime

# Terminal color codes for professional output
G = '\033[92m'  # Green (Success/Open)
C = '\033[96m'  # Cyan (Info/Banner)
Y = '\033[93m'  # Yellow (Status/Warnings)
B = '\033[94m'  # Blue (Borders/Decorations)
RD = '\033[91m' # Red (Errors)
R = '\033[0m'   # Reset (Revert to default color)

# ==============================================================
# PHASE 1: CORE NETWORKING & SCAN LOGIC
# Developed by Member 1: Jaindu
# ==============================================================

def get_service_name(port):
    """ Attempt to find the service name for a given port """
    try:
        return socket.getservbyport(port, "tcp")
    except:
        return "unknown"

def scan_port(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5) 
    try:
        result = s.connect_ex((ip, port))
        if result == 0:
            # Service identification logic by Jaindu
            service = get_service_name(port)
            # Borderless Table alignment for scan results
            print(f"{G}  {port:>5}/TCP    {service:<15}  OPEN    ->  {ip}{R}")
    except:
        pass
    finally:
        s.close()


# ==============================================================
# PHASE 3: HIGH PERFORMANCE MULTI-THREADING & SUBNET SCANNING
# Developed by Member 3: Sathira
# ==============================================================

def threaded_scan(target, start_port, end_port, threads):
    # ==========================================
    # SUBNET PARSING LOGIC (START)
    # Developed by Member 1: Jaindu
    # ==========================================
    try:
        # Determine if the target is a single IP or a CIDR block
        network = ipaddress.ip_network(target, strict=False)
        
        if network.num_addresses == 1:
            ip_list = [str(network.network_address)]
        else:
            ip_list = [str(ip) for ip in network.hosts()]
            
    except ValueError:
        print(f"\n{RD}[!] CRITICAL ERROR: Invalid Target format.{R}")
        print(f"{Y}    Please use a valid IP or CIDR (e.g., 192.168.1.1 or 192.168.1.0/24){R}\n")
        return
    # ==========================================
    # END OF SUBNET PARSING LOGIC (Jaindu)
    # ==========================================

    # Formatting variables
    range_info = f"{start_port} to {end_port}"
    time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    target_str = str(target)

    # Professional UI Box for Scan Information
    print(f"\n{B}┌──────────────────────────────────────────────────────────┐{R}")
    print(f"{B}│ {C}SCAN INFORMATION                                         {B}│{R}")
    print(f"{B}├──────────────────────────────────────────────────────────┤{R}")
    print(f"{B}│ {Y}Target(s)      : {C}{target_str:<39} {B}│{R}")
    print(f"{B}│ {Y}Total Hosts    : {C}{str(len(ip_list)):<39} {B}│{R}")
    print(f"{B}│ {Y}Port Range     : {C}{range_info:<39} {B}│{R}")
    print(f"{B}│ {Y}Threads Used   : {C}{str(threads):<39} {B}│{R}")
    print(f"{B}│ {Y}Started At     : {C}{time_now:<39} {B}│{R}")
    print(f"{B}└──────────────────────────────────────────────────────────┘{R}")
    
    print(f"\n{Y}[*] Initiating scan sequence... Please wait.{R}\n")
    
    t1 = datetime.now() 
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        for ip in ip_list:
            for port in range(start_port, end_port + 1):
                executor.submit(scan_port, ip, port)
                
    t2 = datetime.now() 
    # Calculate time with milliseconds for high precision
    total_time = t2 - t1 
    time_display = str(total_time)[:-3] # Truncate to 3 decimal places for milliseconds
    
    # Professional UI Box for Scan Completion - Precision update
    print(f"\n{B}┌──────────────────────────────────────────────────────────┐{R}")
    print(f"{B}│ {G}SCAN COMPLETE!                                           {B}│{R}")
    print(f"{B}├──────────────────────────────────────────────────────────┤{R}")
    print(f"{B}│ {Y}Total Time Taken : {C}{time_display:<37} {B}│{R}")
    print(f"{B}└──────────────────────────────────────────────────────────┘{R}\n")


# ==============================================================
# PHASE 4: CLI INTERFACE & ASCII BANNER
# Developed by Member 2: Dinara
# ==============================================================

if __name__ == "__main__":
    banner = f"""{C}
  _   _      _                      _          _____                                 
 | \ | | ___| |___      _____  _ __| | __     / ____|___ __ _ _ __  _ __   ___ _ __ 
 |  \| |/ _ \ __\ \ /\ / / _ \| '__| |/ /    | (___ / __/ _` | '_ \| '_ \ / _ \ '__|
 | |\  |  __/ |_ \ V  V / (_) | |  |   <      \___ \ (_| (_| | | | | | | |  __/ |   
 |_| \_|\___|\__| \_/\_/ \___/|_|  |_|\_\     _____/\___\__,_|_| |_|_| |_|\___|_|   
                                                                                    
 {B}════════════════════════════════════════════════════════════════════════════════════
                  {Y}Professional Network Discovery & Auditing Tool
 {B}════════════════════════════════════════════════════════════════════════════════════{R}"""
    print(banner)
    
    parser = argparse.ArgumentParser(description="Professional Network Port Scanner")
    parser.add_argument("target", help="Target IP or CIDR (e.g., 192.168.1.1 or 192.168.1.0/24)")
    parser.add_argument("-s", "--start", type=int, default=1, help="Start port")
    parser.add_argument("-e", "--end", type=int, default=100, help="End port")
    parser.add_argument("-t", "--threads", type=int, default=50, help="Threads")
    
    args = parser.parse_args()
    threaded_scan(args.target, args.start, args.end, args.threads)