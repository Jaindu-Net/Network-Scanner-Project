import socket

def scan_port(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5) # Scanner eka stuck wenne nathi wenna timeout ekak
    try:
        if s.connect_ex((ip, port)) == 0:
            print(f"[+] Port {port} is OPEN on {ip}")
    except:
        pass
    finally:
        s.close()

def scan_port_range(ip, start_port, end_port):
    print(f"Scanning target {ip} from port {start_port} to {end_port}...")
    for port in range(start_port, end_port + 1):
        scan_port(ip, port)
    print("Scanning finished!")

if __name__ == "__main__":
    # Test karanna meka damme. Passe meka wenas wenawa.
    scan_port_range("127.0.0.1", 1, 1000)