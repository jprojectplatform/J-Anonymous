#!/usr/bin/env python3

import os
import random
import subprocess
import time
import requests
import re
import signal
import sys
from colorama import Fore, Style, init

# Hapa tambua colorama
init()

# Banner
def show_banner():
    print(Fore.RED + r"""
    
	      _   ____            _           _      
	    | | |  _ \ _ __ ___ (_) ___  ___| |_    
	 _  | | | |_) | '__/ _ \| |/ _ \/ __| __|   
	| |_| | |  __/| | | (_) | |  __/ (__| |_    
	 \___/ _|_|   |_|  \___// |\___|\___|\__|   	 
	|  _ \| | __ _| |_ / _|__/_  _ __ _ __ ___  
	| |_) | |/ _` | __| |_ / _ \| '__| '_ ` _ \ 
	|  __/| | (_| | |_|  _| (_) | |  | | | | | |
	|_|   |_|\__,_|\__|_|  \___/|_|  |_| |_| |_|
    
    """ + Style.RESET_ALL)
    print(Fore.GREEN + "Be Invisible with J-Anonymous" + Style.RESET_ALL)
    print(Fore.GREEN + "Meet Me: https://jprojectplatform.com/" + Style.RESET_ALL)
    print(Fore.YELLOW + "Created By JH4CK3R\n" + Style.RESET_ALL)


# Lazima kuwa ROOT
def check_root():
    if os.getuid() != 0:
        print(Fore.RED + "[!] This script must be run as root!" + Style.RESET_ALL)
        exit(1)

# Check for SOCKS support (Required for new proxy logic)
def check_dependencies():
    try:
        import socks
    except ImportError:
        print(Fore.YELLOW + "[*] Installing required dependency: PySocks..." + Style.RESET_ALL)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pysocks"])

# Taarifa zote za NETWORK kwa mda huo hpa
def get_current_info():
    print(Fore.CYAN + "\n[*] Current Network Information:" + Style.RESET_ALL)
    
    # Pata MAC address
    try:
        mac = subprocess.check_output("cat /sys/class/net/$(ip route show default | awk '/default/ {print $5}')/address", shell=True).decode().strip()
        print(f"MAC Address: {mac}")
    except:
        print("Could not determine MAC address")
    
    # Tambua LAN IP
    try:
        lan_ip = subprocess.check_output("hostname -I | awk '{print $1}'", shell=True).decode().strip()
        print(f"LAN IP: {lan_ip}")
    except:
        print("Could not determine LAN IP")
    
    # Tambua WAN IP
    try:
        wan_ip = requests.get('https://api.ipify.org', timeout=5).text
        print(f"WAN IP: {wan_ip}")
    except:
        print("Could not determine WAN IP")


# Generate random MAC address
def generate_random_mac():
    mac = [ 0x00, 
            random.randint(0x00, 0x7f),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff) ]
    return ':'.join(map(lambda x: "%02x" % x, mac))


# Badili MAC address
def change_mac(interface=None):
    if not interface:
        try:
            interface = subprocess.check_output("ip route show default | awk '/default/ {print $5}'", shell=True).decode().strip()
        except:
            print(Fore.RED + "[!] Could not determine network interface" + Style.RESET_ALL)
            return False
    
    print(Fore.YELLOW + f"\n[*] Changing MAC address for {interface}..." + Style.RESET_ALL)
    
    try:
        # interface down kwanza
        subprocess.call(f"ifconfig {interface} down", shell=True)
        
        # Generate and set new MAC
        new_mac = generate_random_mac()
        subprocess.call(f"ifconfig {interface} hw ether {new_mac}", shell=True)
        
        # Kisha interface up
        subprocess.call(f"ifconfig {interface} up", shell=True)
        
        print(Fore.GREEN + f"[+] MAC address changed to: {new_mac}" + Style.RESET_ALL)
        return True
    except Exception as e:
        print(Fore.RED + f"[!] Failed to change MAC address: {str(e)}" + Style.RESET_ALL)
        return False


# Change LAN IP (kwa Tor)
def change_lan_ip():
    print(Fore.YELLOW + "\n[*] Changing LAN IP using Tor..." + Style.RESET_ALL)
    
    try:
        # Check if Tor is installed
        tor_check = subprocess.call("which tor", shell=True)
        if tor_check != 0:
            print(Fore.RED + "[!] Tor is not installed. Installing now..." + Style.RESET_ALL)
            subprocess.call("apt-get install tor -y", shell=True)
        
        # Start Tor service
        subprocess.call("service tor start", shell=True)
        
        # Configure system to use Tor
        subprocess.call("echo 'socks5 127.0.0.1 9050' > /etc/proxychains.conf", shell=True)
        
        print(Fore.GREEN + "[+] LAN IP changed through Tor network" + Style.RESET_ALL)
        return True
    except Exception as e:
        print(Fore.RED + f"[!] Failed to change LAN IP: {str(e)}" + Style.RESET_ALL)
        return False


# --- WAN IP & PROXY SECTION (UPDATED) ---

def check_and_install_tor():
    """Check if tor is installed, install if missing"""
    try:
        subprocess.run(["tor", "--version"], 
                      check=True, 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL)
        return True
    except:
        print(Fore.YELLOW + "[!] Installing tor..." + Style.RESET_ALL)
        return subprocess.run(["sudo", "apt", "install", "tor", "-y"], 
                            check=False).returncode == 0

def fetch_and_test_proxies():
    """Updated Robust Proxy Fetcher & Tester"""
    
    # 1. Sources targeting SOCKS5 and HTTPS (better for anonymity/SSL)
    PROXY_SOURCES = [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all",
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=https&timeout=10000&country=all",
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
        "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt"
    ]
    
    print(Fore.CYAN + "\n[*] Fetching fresh proxy list (SOCKS5/HTTPS)..." + Style.RESET_ALL)
    
    candidates = []
    
    # 2. Fetch and Parse
    for url in PROXY_SOURCES:
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                # Regex to extract only valid IP:PORT patterns, ignoring HTML junk
                matches = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+", r.text)
                candidates.extend(matches)
        except:
            continue
            
    # Remove duplicates
    candidates = list(set(candidates))
    
    if not candidates:
        print(Fore.RED + "[!] No proxies found. Check internet connection." + Style.RESET_ALL)
        return False
        
    print(Fore.YELLOW + f"[*] Testing {min(20, len(candidates))} candidates (out of {len(candidates)} found)..." + Style.RESET_ALL)
    
    # 3. Test Proxies (Prioritize SOCKS5)
    for proxy in random.sample(candidates, min(20, len(candidates))):
        try:
            # Try as SOCKS5 first (requires 'pysocks' installed)
            proxies = {
                'http': f'socks5://{proxy}',
                'https': f'socks5://{proxy}'
            }
            
            print(f"\rTesting: {proxy} ... ", end="", flush=True)
            
            # Use short timeout for testing
            response = requests.get('https://api.ipify.org?format=json', proxies=proxies, timeout=5)
            
            if response.status_code == 200:
                new_ip = response.json().get('ip')
                print(Fore.GREEN + f"\n[✓] SUCCESS! SOCKS5 Proxy locked: {proxy}" + Style.RESET_ALL)
                print(Fore.GREEN + f"[+] New WAN IP: {new_ip}" + Style.RESET_ALL)
                
                # Save working proxy
                with open("j-proxies-working.txt", "w") as f:
                    f.write(proxy)
                return True
                
        except:
            # Fallback: Try as standard HTTPS
            try:
                proxies = {
                    'http': f'http://{proxy}',
                    'https': f'http://{proxy}'
                }
                response = requests.get('https://api.ipify.org?format=json', proxies=proxies, timeout=5)
                if response.status_code == 200:
                    new_ip = response.json().get('ip')
                    print(Fore.GREEN + f"\n[✓] SUCCESS! HTTPS Proxy locked: {proxy}" + Style.RESET_ALL)
                    print(Fore.GREEN + f"[+] New WAN IP: {new_ip}" + Style.RESET_ALL)
                    return True
            except:
                continue
                
    print(Fore.RED + "\n[!] Proxies timed out. Switching to Tor fallback..." + Style.RESET_ALL)
    return False

def enable_tor_mode():
    """Enhanced Tor mode with proper authentication and timeout handling"""
    try:
        # 1. Verify Tor service is running
        try:
            subprocess.run(["sudo", "systemctl", "is-active", "--quiet", "tor"])
        except:
            print(Fore.YELLOW + "[!] Starting Tor service..." + Style.RESET_ALL)
            subprocess.run(["sudo", "systemctl", "start", "tor"], check=True)
            time.sleep(5)  # Wait for Tor to initialize

        # 2. Get current IP through Tor
        print(Fore.CYAN + "[*] Switching to Tor Circuit..." + Style.RESET_ALL)
        
        # 3. Rotate IP (if authentication is set up)
        try:
            tor_auth = "sudo cat /var/run/tor/control.authcookie | xxd -ps"
            auth_cookie = subprocess.run(tor_auth, shell=True, check=True, capture_output=True, text=True).stdout.strip()
            rotate_cmd = f"echo -e 'AUTHENTICATE {auth_cookie}\\nSIGNAL NEWNYM' | nc 127.0.0.1 9051"
            subprocess.run(rotate_cmd, shell=True, check=True)
            print(Fore.YELLOW + "[*] Rotating Tor identity..." + Style.RESET_ALL)
            time.sleep(5)
        except:
            pass # Continue if auth fails, might still work with default circuit

        # 4. Verify new IP
        try:
            new_ip = requests.get(
                "https://api.ipify.org",
                proxies={"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"},
                timeout=20
            ).text
            
            print(Fore.GREEN + f"[✓] Tor Active | New IP: {new_ip}" + Style.RESET_ALL)
            return True
                
        except Exception as e:
            print(Fore.RED + f"[!] Tor check failed: {str(e)[:100]}" + Style.RESET_ALL)
            return False

    except Exception as e:
        print(Fore.RED + f"[!] Tor error: {str(e)[:100]}" + Style.RESET_ALL)
        return False

def change_wan_ip():
    print(Fore.YELLOW + "\n[*] Initializing WAN IP change..." + Style.RESET_ALL)
    
    # Ensure dependencies
    check_dependencies()
    
    if not check_and_install_tor():
        print(Fore.RED + "[!] tor installation failed" + Style.RESET_ALL)
        return False
    
    # Try Proxies First
    if fetch_and_test_proxies():
        return True
    else:
        # Fallback to Tor
        print(Fore.YELLOW + "[!] Proxy methods failed. Falling back to Tor..." + Style.RESET_ALL)
        return enable_tor_mode()
        
# --- PROTONVPN SECTION ---

def check_install_protonvpn():
    """Check for both CLI (venv or system) and GUI installations"""
    print(Fore.YELLOW + "\n[*] Checking ProtonVPN installation..." + Style.RESET_ALL)
    
    # Check for CLI in virtual environment first
    if 'VIRTUAL_ENV' in os.environ:
        venv_cli = os.path.join(os.environ['VIRTUAL_ENV'], 'bin', 'protonvpn')
        try:
            subprocess.run([venv_cli, "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(Fore.CYAN + "[✓] ProtonVPN CLI detected in virtual environment" + Style.RESET_ALL)
            return "cli-venv"
        except:
            pass
    
    # Check for system-wide CLI
    try:
        subprocess.run(["protonvpn", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(Fore.CYAN + "[✓] ProtonVPN CLI detected system-wide" + Style.RESET_ALL)
        return "cli-system"
    except:
        pass
    
    # Check for GUI version
    try:
        subprocess.run(["proton-vpn", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(Fore.CYAN + "[✓] ProtonVPN GUI detected" + Style.RESET_ALL)
        return "gui"
    except:
        print(Fore.RED + "[!] No ProtonVPN installation found" + Style.RESET_ALL)
        return False

def enable_protonvpn():
    """Connect using available ProtonVPN version"""
    vpn_type = check_install_protonvpn()
    
    if not vpn_type:
        print(Fore.RED + "[!] Install ProtonVPN first." + Style.RESET_ALL)
        return False

    try:
        if vpn_type.startswith("cli"):
            protonvpn_path = os.path.join(os.environ.get('VIRTUAL_ENV', ''), 'bin', 'protonvpn') if vpn_type == "cli-venv" else "protonvpn"
            
            print(Fore.YELLOW + "[*] Connecting via CLI..." + Style.RESET_ALL)
            result = subprocess.run(
                ["sudo", protonvpn_path, "connect", "--fastest"],
                capture_output=True,
                text=True
            )
            
            if "Connected" in result.stdout:
                vpn_ip = requests.get("https://api.ipify.org", timeout=10).text
                print(Fore.GREEN + f"[✓] VPN Connected | IP: {vpn_ip}" + Style.RESET_ALL)
                return True
        
        elif vpn_type == "gui":
            print(Fore.YELLOW + "[*] Launching GUI - please connect manually..." + Style.RESET_ALL)
            subprocess.Popen(["proton-vpn"])
            input("Press Enter AFTER you've established the VPN connection...")
            return True
            
        print(Fore.RED + f"[!] Connection failed" + Style.RESET_ALL)
        return False
        
    except Exception as e:
        print(Fore.RED + f"[!] VPN Error: {str(e)[:100]}" + Style.RESET_ALL)
        return False

def disable_protonvpn():
    """Disconnect based on installed version"""
    vpn_type = check_install_protonvpn()
    
    try:
        if vpn_type.startswith("cli"):
            protonvpn_path = os.path.join(os.environ.get('VIRTUAL_ENV', ''), 'bin', 'protonvpn') if vpn_type == "cli-venv" else "protonvpn"
            subprocess.run(["sudo", protonvpn_path, "disconnect"], check=True, stdout=subprocess.PIPE)
        elif vpn_type == "gui":
            subprocess.run(["proton-vpn", "--disconnect"], check=True, stdout=subprocess.PIPE)
            
        print(Fore.GREEN + "[✓] VPN disconnected" + Style.RESET_ALL)
        return True
        
    except Exception as e:
        print(Fore.RED + f"[!] Disconnect failed: {str(e)[:100]}" + Style.RESET_ALL)
        return False
        
        
# --- OPENVPN SECTION (UPDATED) ---       
        
def get_tun_interface():
    """Find active tun/tap interface"""
    try:
        output = subprocess.check_output(["ip", "addr"], text=True)
        match = re.search(r"(\btun\d+|\btap\d+):", output)
        return match.group(1) if match else None
    except:
        return None

def is_openvpn_connected():
    """Check if OpenVPN tunnel has an IP"""
    iface = get_tun_interface()
    if not iface:
        return False
    try:
        output = subprocess.check_output(["ip", "-4", "addr", "show", iface], text=True)
        return bool(re.search(r"inet\s+\d+\.\d+\.\d+\.\d+", output))
    except:
        return False

def connect_openvpn():
    config_dir = "openvpn"
    
    # FIX: Create directory if it doesn't exist
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        print(Fore.RED + f"[!] Directory '{config_dir}' was missing." + Style.RESET_ALL)
        print(Fore.YELLOW + f"[*] Created '{config_dir}'. Please put your .ovpn files inside it and try again." + Style.RESET_ALL)
        return False

    configs = sorted([f for f in os.listdir(config_dir) if f.endswith(".ovpn")])
    if not configs:
        print(Fore.RED + f"[!] No .ovpn configs found in '{config_dir}'" + Style.RESET_ALL)
        return False

    print(Fore.CYAN + "\nAvailable VPN Configs:" + Style.RESET_ALL)
    [print(f"{i+1}. {name}") for i, name in enumerate(configs)]
    
    try:
        choice = int(input(Fore.YELLOW + f"\nSelect config (1-{len(configs)}): " + Style.RESET_ALL)) - 1
        if choice < 0 or choice >= len(configs): raise ValueError
        config_path = f"{config_dir}/{configs[choice]}"
    except:
        print(Fore.RED + "[!] Invalid selection" + Style.RESET_ALL)
        return False

    log_path = f"report/openvpn_{configs[choice]}.log"
    os.makedirs("report", exist_ok=True)

    print(Fore.YELLOW + f"[*] Connecting to {configs[choice]}..." + Style.RESET_ALL)
    
    # Start OpenVPN
    with open(log_path, "w") as log_file:
        process = subprocess.Popen(
            ["sudo", "openvpn", "--config", config_path],
            stdout=log_file,
            stderr=log_file,
            preexec_fn=os.setsid # Create new process group
        )

    # Wait for connection
    success = False
    start_time = time.time()
    
    # Spinner loop
    while time.time() - start_time < 30:
        time.sleep(1)
        try:
            with open(log_path, "r") as log_file:
                logs = log_file.read()
                if "Initialization Sequence Completed" in logs:
                    success = True
                    break
        except:
            pass

        if process.poll() is not None:
            # Process died
            with open(log_path, "r") as log_file:
                print(Fore.RED + "[!] OpenVPN failed:\n" + log_file.read()[-300:] + Style.RESET_ALL)
            return False

    if success and is_openvpn_connected():
        print(Fore.GREEN + f"[✓] Connected to {configs[choice]}" + Style.RESET_ALL)
        try:
            vpn_ip = requests.get('https://api.ipify.org', timeout=5).text
            print(Fore.CYAN + f"[*] External IP: {vpn_ip}" + Style.RESET_ALL)
        except:
            pass
        return True
    else:
        print(Fore.RED + "[!] Connection timed out" + Style.RESET_ALL)
        # Kill process group
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except:
            pass
        return False

def disconnect_openvpn():
    """Stop any running OpenVPN process"""
    try:
        print(Fore.YELLOW + "[*] Disconnecting OpenVPN..." + Style.RESET_ALL)
        subprocess.run(["sudo", "pkill", "-f", "openvpn"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)

        iface = get_tun_interface()
        if iface:
            # Force kill interface if still up
            subprocess.run(["sudo", "ip", "link", "set", iface, "down"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["sudo", "ip", "link", "delete", iface], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        print(Fore.GREEN + "[✓] OpenVPN disconnected" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"[!] Failed to disconnect: {e}" + Style.RESET_ALL)

        

# J DashBoard Main Sasa
def main_menu():
    while True:
        print(Fore.CYAN + "\nJ-Anonymous Main Menu:" + Style.RESET_ALL)
        print("1. Show current network information")
        print("2. Change MAC address")
        print("3. Change LAN IP (using Tor)")
        print("4. Change WAN IP (using Proxies/Tor)")
        print("5. Change ALL (MAC, LAN, WAN)")
        print("6. Connect ProtonVPN")
        print("7. Disconnect ProtonVPN")
        print("8. Connect OpenVPN (Any .ovpn file)")
        print("9. Disconnect OpenVPN")
        print("10. Exit")
        
        choice = input("\nEnter your choice (1-10): ")
        
        if choice == "1":
            get_current_info()
        elif choice == "2":
            change_mac()
        elif choice == "3":
            change_lan_ip()
        elif choice == "4":
            change_wan_ip()
        elif choice == "5":
            print(Fore.YELLOW + "\n[*] Changing ALL network identifiers..." + Style.RESET_ALL)
            change_mac()
            change_lan_ip()
            change_wan_ip()
            print(Fore.GREEN + "[+] All network identifiers changed!" + Style.RESET_ALL)
        elif choice == "6":
            enable_protonvpn()
        elif choice == "7":
            disable_protonvpn()
        elif choice == "8":
            connect_openvpn()
        elif choice == "9":
            disconnect_openvpn()
        elif choice == "10":
            print(Fore.YELLOW + "\n Exiting J-Anonymous.\n Enjoy With J Project Platforom \n Stay safe!" + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + "[-_-] Invalid choice. Please try again." + Style.RESET_ALL)


# Main function
def main():
    show_banner()
    check_root()
    check_dependencies()
    main_menu()


if __name__ == "__main__":
     main()
