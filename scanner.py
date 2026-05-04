import socket
import argparse
import concurrent.futures 
import ipaddress 
from datetime import datetime
import json 

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
    """ Attempt to resolve the standard service name for a given TCP port """
    try:
        return socket.getservbyport(port, "tcp")
    except:
        return "unknown"

def scan_port(ip, port):
    """ Attempt a TCP connection to determine if the specified port is open """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5) 
    try:
        result = s.connect_ex((ip, port))
        if result == 0:
            # Resolve the service name upon successful connection
            service = get_service_name(port)
            # Display the result via standard output
            print(f"{G}  {port:>5}/TCP    {service:<15}  OPEN    ->  {ip}{R}")
            
            # Return structured data for the reporting engine
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
    
    # Return None if the port is closed or unreachable
    return None 


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
        # Evaluate whether the target is a single IP address or a CIDR subnet block
        network = ipaddress.ip_network(target, strict=False)
        
        if network.num_addresses == 1:
            ip_list = [str(network.network_address)]
        else:
            # Generate a comprehensive list of host IP addresses within the subnet
            ip_list = [str(ip) for ip in network.hosts()]
            
    except ValueError:
        print(f"\n{RD}[!] CRITICAL ERROR: Invalid Target format.{R}")
        print(f"{Y}    Please use a valid IP or CIDR (e.g., 192.168.1.1 or 192.168.1.0/24){R}\n")
        return
    # ==========================================
    # END OF SUBNET PARSING LOGIC 
    # ==========================================

    # Define variables for reporting and UI formatting
    range_info = f"{start_port} to {end_port}"
    time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    target_str = str(target)

    # Render the scan initialization dashboard
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
    
    # Record the precise start time
    t1 = datetime.now() 
    
    # Initialize an array to collect data from successful connections
    open_ports_data = [] 

    # Execute the multi-threaded scanning sequence
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        for ip in ip_list:
            for port in range(start_port, end_port + 1):
                # Submit tasks to the thread pool and store the future objects
                futures.append(executor.submit(scan_port, ip, port))
                
        # Aggregate the results as each thread completes its execution
        for future in concurrent.futures.as_completed(futures):
            result_data = future.result()
            if result_data: 
                open_ports_data.append(result_data)
                
    # Record the precise completion time and calculate total duration
    t2 = datetime.now() 
    total_time = t2 - t1 
    time_display = str(total_time)[:-3] 
    
    # Render the scan completion dashboard
    print(f"\n{B}┌──────────────────────────────────────────────────────────┐{R}")
    print(f"{B}│ {G}SCAN COMPLETE!                                           {B}│{R}")
    print(f"{B}├──────────────────────────────────────────────────────────┤{R}")
    print(f"{B}│ {Y}Total Time Taken : {C}{time_display:<37} {B}│{R}")
    print(f"{B}└──────────────────────────────────────────────────────────┘{R}\n")

    # ==============================================================
    # PHASE 5: ENTERPRISE REPORTING ENGINE (JSON EXPORT)
    # Developed by Member 1: Jaindu
    # ==============================================================
    print(f"{Y}[*] Generating Advanced JSON Report...{R}")
    
    # Organize the flat list into a dictionary grouped by IP address
    structured_results = {}
    for entry in open_ports_data:
        ip = entry["ip"]
        if ip not in structured_results:
            structured_results[ip] = []
        
        structured_results[ip].append({
            "port": entry["port"],
            "service": entry["service"],
            "state": entry["state"]
        })

    # Sort the ports numerically for each IP to ensure a clean layout
    for ip in structured_results:
        structured_results[ip] = sorted(structured_results[ip], key=lambda x: x["port"])

    # Define the advanced data structure for the JSON report
    report_content = {
        "scan_metadata": {
            "target": target_str,
            "port_range": range_info,
            "start_time": time_now,
            "total_time_elapsed": time_display,
            "threads_used": threads,
            "total_open_ports_found": len(open_ports_data)
        },
        "scan_results": structured_results
    }

    # Generate a unique filename using the current date and time
    filename_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_filename = f"scan_report_{filename_time}.json"

    # Write the structured data into the JSON file with sorting and indentation
    with open(report_filename, "w") as json_file:
        json.dump(report_content, json_file, indent=4, sort_keys=True)

    print(f"{G}[+] Successfully saved advanced report to: {report_filename}{R}\n")


# ==============================================================
# PHASE 4: CLI INTERFACE & ASCII BANNER
# Developed by Member 2: Dinara
# ==============================================================

if __name__ == "__main__":
    # Define and render the application banner
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
    
    # Configure the argument parser for command-line inputs
    parser = argparse.ArgumentParser(description="Professional Network Port Scanner")
    parser.add_argument("target", help="Target IP or CIDR (e.g., 192.168.1.1 or 192.168.1.0/24)")
    parser.add_argument("-s", "--start", type=int, default=1, help="Start port")
    parser.add_argument("-e", "--end", type=int, default=100, help="End port")
    parser.add_argument("-t", "--threads", type=int, default=50, help="Threads")
    
    # Parse the arguments and trigger the primary scanning sequence
    args = parser.parse_args()
    threaded_scan(args.target, args.start, args.end, args.threads)