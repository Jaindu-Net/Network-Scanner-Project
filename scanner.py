import socket
import argparse
import concurrent.futures 
import ipaddress # Added for Subnet/CIDR parsing
from datetime import datetime

# Terminal color codes for professional output
G = '\033[92m'  # Green
C = '\033[96m'  # Cyan
Y = '\033[93m'  # Yellow
R = '\033[0m'   # Reset (Revert to default color)

# ==============================================================
# PHASE 1: CORE NETWORKING & SCAN LOGIC
# Developed by Member 1: Jaindu
# ==============================================================

def scan_port(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5) 
    try:
        result = s.connect_ex((ip, port))
        if result == 0:
            # Print only open ports in green
            print(f"{G}[+] Port {port:<5} is OPEN on {ip}{R}")
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
        
        # If it's a single IP, extract it. If it's a subnet, extract all host IPs.
        if network.num_addresses == 1:
            ip_list = [str(network.network_address)]
        else:
            ip_list = [str(ip) for ip in network.hosts()]
            
    except ValueError:
        print(f"{Y}[!] Error: Invalid Target format. Please use a valid IP or CIDR (e.g., 192.168.1.0/24){R}")
        return
    # ==========================================
    # END OF SUBNET PARSING LOGIC (Jaindu)
    # ==========================================

    print(f"{C}\n[*] Scanning Target : {target}{R}")
    print(f"{C}[*] Total Hosts   : {len(ip_list)}{R}")
    print(f"{C}[*] Port Range    : {start_port} to {end_port}{R}")
    print(f"{C}[*] Threads Used  : {threads}{R}")
    print(f"{Y}[*] Scan Started  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{R}")
    print("-" * 60)
    
    # Record the start time
    t1 = datetime.now() 
    
    # Using ThreadPoolExecutor for concurrent scanning across multiple IPs and Ports
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        for ip in ip_list:
            for port in range(start_port, end_port + 1):
                # Submit tasks for all IPs and Ports
                executor.submit(scan_port, ip, port)
                
    # Record the end time
    t2 = datetime.now() 
    # Calculate total time taken
    total_time = t2 - t1 
    
    print("-" * 60)
    print(f"{Y}[*] Scanning Finished!{R}")
    print(f"{C}[*] Total Time Taken : {total_time}{R}\n")


# ==============================================================
# PHASE 4: CLI INTERFACE & ASCII BANNER
# Developed by Member 2: Dinara
# ==============================================================

if __name__ == "__main__":
    # ASCII Art Banner in Cyan color
    banner = f"""{C}
     _   _      _                      _      _____                                 
    | \ | | ___| |___      _____  _ __| | __ / ____|___ __ _ _ __  _ __   ___ _ __ 
    |  \| |/ _ \ __\ \ /\ / / _ \| '__| |/ /| (___ / __/ _` | '_ \| '_ \ / _ \ '__|
    | |\  |  __/ |_ \ V  V / (_) | |  |   <  \___ \ (_| (_| | | | | | | |  __/ |   
    |_| \_|\___|\__| \_/\_/ \___/|_|  |_|\_\ _____/\___\__,_|_| |_|_| |_|\___|_|   
    {R}"""
    print(banner)
    
    # Setup argparse for command-line arguments
    parser = argparse.ArgumentParser(description="Professional Network Port Scanner")
    # Updated description to indicate CIDR support
    parser.add_argument("target", help="Target IP address or CIDR block (e.g., 192.168.1.1 or 192.168.1.0/24)")
    parser.add_argument("-s", "--start", type=int, default=1, help="Start port (default: 1)")
    parser.add_argument("-e", "--end", type=int, default=100, help="End port (default: 100)")
    parser.add_argument("-t", "--threads", type=int, default=50, help="Number of concurrent threads (default: 50)")
    
    args = parser.parse_args()
    
    # Pass all arguments to Sathira's threaded scan function
    threaded_scan(args.target, args.start, args.end, args.threads)