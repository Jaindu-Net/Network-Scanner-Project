import json
import os
import glob
from datetime import datetime

# Terminal color codes
G = '\033[92m'  
C = '\033[96m'  
Y = '\033[93m'  
R = '\033[0m'   

# ==============================================================
# PHASE 6: ENTERPRISE HTML DASHBOARD GENERATOR
# Developed by Member 2: Dinara
# Architecture: Decoupled Reporting Module
# ==============================================================

def create_html_dashboard(json_file_path=None):
    """ Reads the specified JSON report and generates an HTML Dashboard. 
        If no file is specified, it auto-detects the latest scan report. """
    
    if not json_file_path:
        print(f"{Y}[*] No file specified. Searching for the latest scan report...{R}")
        list_of_files = glob.glob('scan_report_*.json')
        if not list_of_files:
            print("[-] Error: No JSON scan reports found in the current directory.")
            return
        json_file_path = max(list_of_files, key=os.path.getctime)
        
    print(f"{C}[*] Processing data from: {json_file_path}{R}")

    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
    except Exception as e:
        print(f"[-] Error loading JSON file: {e}")
        return

    meta = data.get("scan_metadata", {})
    results = data.get("scan_results", {})
    
    target_str = meta.get("target_network", "Unknown")
    time_now = meta.get("scan_start_time", "Unknown")
    time_display = meta.get("total_execution_time", "Unknown")
    
    total_open_ports = sum(host_data.get("total_open_ports", 0) for host_data in results.values())

    # Updated HTML Structure with NexScan Pro Branding
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NexScan Pro - Security Audit Dashboard</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; margin: 0; padding: 30px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background-color: #1e272e; color: #fff; padding: 25px; border-radius: 8px; text-align: center; margin-bottom: 30px; border-top: 5px solid #0abde3; }}
        .header h1 {{ margin: 0; font-size: 32px; letter-spacing: 1px; }}
        .header p {{ margin: 10px 0 0; color: #808e9b; font-size: 15px; }}
        .summary-wrapper {{ display: flex; justify-content: space-between; margin-bottom: 30px; gap: 20px; flex-wrap: wrap; }}
        .card {{ background: #fff; padding: 20px; border-radius: 8px; flex: 1; text-align: center; border-bottom: 4px solid #0abde3; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
        .card h3 {{ margin: 0; font-size: 13px; color: #7f8c8d; text-transform: uppercase; letter-spacing: 1px; }}
        .card p {{ margin: 15px 0 0; font-size: 26px; font-weight: bold; color: #2c3e50; }}
        .results-section {{ background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
        .ip-block {{ margin-bottom: 40px; }}
        .ip-header {{ background-color: #f8f9fa; padding: 12px 20px; border-left: 5px solid #ee5253; font-size: 18px; font-weight: bold; margin-bottom: 15px; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 10px; }}
        th, td {{ padding: 12px 20px; text-align: left; border-bottom: 1px solid #dfe6e9; }}
        th {{ background-color: #f1f2f6; color: #576574; font-size: 13px; text-transform: uppercase; }}
        .badge-open {{ padding: 6px 12px; border-radius: 4px; font-size: 11px; font-weight: bold; color: #fff; background-color: #1dd1a1; }}
        .badge-critical {{ background-color: #ff4757; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ NexScan Pro Network Auditing Dashboard</h1>
            <p>Automated Security Posture & Vulnerability Report</p>
        </div>
        
        <div class="summary-wrapper">
            <div class="card"><h3>Target Network</h3><p>{target_str}</p></div>
            <div class="card"><h3>Start Time</h3><p>{time_now}</p></div>
            <div class="card"><h3>Execution Time</h3><p>{time_display}</p></div>
            <div class="card"><h3>Total Open Ports</h3><p>{total_open_ports}</p></div>
        </div>
        
        <div class="results-section">
            <h2>Detailed Asset Scan Results</h2>
"""

    if not results:
        html_content += "<p style='text-align: center;'>No open ports detected.</p>"
    else:
        for ip, host_data in results.items():
            risk_level = host_data.get("overall_risk", "Low")
            risk_badge = f"<span class='badge-critical'>RISK: {risk_level.upper()}</span>" if risk_level == "Critical" else ""
            
            html_content += f"""
            <div class="ip-block">
                <div class="ip-header">Host Device: {ip} {risk_badge}</div>
                <table>
                    <tr>
                        <th width="15%">Port</th>
                        <th width="25%">Service</th>
                        <th width="45%">Security Note</th>
                        <th width="15%">State</th>
                    </tr>"""
            
            for port_data in host_data.get("open_ports", []):
                html_content += f"""
                    <tr>
                        <td><strong>{port_data['port']} / TCP</strong></td>
                        <td>{port_data['service'].upper()}</td>
                        <td>{port_data.get('security_note', 'Standard service')}</td>
                        <td><span class="badge-open">{port_data['state']}</span></td>
                    </tr>"""
                    
            html_content += """
                </table>
            </div>"""
            
    html_content += """
        </div>
    </div>
</body>
</html>
"""

    filename_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    html_filename = f"scan_dashboard_{filename_time}.html"

    with open(html_filename, "w", encoding="utf-8") as html_file:
        html_file.write(html_content)
        
    print(f"{G}[+] Successfully generated HTML dashboard: {html_filename}{R}\n")

# ==============================================================
# STANDALONE EXECUTION GUARD
# ==============================================================
if __name__ == "__main__":
    create_html_dashboard()