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

# Initialize Colorama
init()

# --- UTILITY FUNCTIONS ---

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
    print(Fore.GREEN + "Be Invisible with J-Anonymous (Final)" + Style.RESET_ALL)
    print(Fore.GREEN + "Meet Me: https://jprojectplatform.com/" + Style.RESET_ALL)
    print(Fore.YELLOW + "Created By JH4CK3R\n" + Style.RESET_ALL)

def check_root():
    if os.getuid() != 0:
        print(Fore.RED + "[!] This script must be run as root!" + Style.RESET_ALL)
        sys.exit(1)

def check_dependencies():
    try:
        import socks
    except ImportError:
        print(Fore.YELLOW + "[*] Installing required dependency: PySocks..." + Style.RESET_ALL)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pysocks"])

# --- NETWORK INFO ---

def get_current_info():
    print(Fore.CYAN + "\n[*] Current Network Information:" + Style.RESET_ALL)
    
    # Get MAC address
    try:
        mac = subprocess.check_output("cat /sys/class/net/$(ip route show default | awk '/default/ {print $5}')/address", shell=True).decode().strip()
        print(f"MAC Address: {mac}")
    except:
        print("Could not determine MAC address")
    
    # Get LAN IP
    try:
        lan_ip = subprocess.check_output("hostname -I | awk '{print $1}'", shell=True).decode().strip()
        print(f"LAN IP: {lan_ip}")
    except:
        print("Could not determine LAN IP")
    
    # Get WAN IP
    try:
        wan_ip = requests.get('https://api.ipify.org', timeout=5).text
        print(f"WAN IP: {wan_ip}")
    except:
        print("Could not determine WAN IP")

# --- MAC CHANGER ---

def generate_random_mac():
    mac = [ 0x00, 
            random.randint(0x00, 0x7f),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff),
            random.randint(0x00, 0xff) ]
    return ':'.join(map(lambda x: "%02x" % x, mac))

def change_mac(interface=None):
    if not interface:
        try:
            interface = subprocess.check_output("ip route show default | awk '/default/ {print $5}'", shell=True).decode().strip()
        except:
            print(Fore.RED + "[!] Could not determine network interface" + Style.RESET_ALL)
            return False
    
    print(Fore.YELLOW + f"\n[*] Changing MAC address for {interface}..." + Style.RESET_ALL)
    
    try:
        subprocess.call(f"ifconfig {interface} down", shell=True)
        new_mac = generate_random_mac()
        subprocess.call(f"ifconfig {interface} hw ether {new_mac}", shell=True)
        subprocess.call(f"ifconfig {interface} up", shell=True)
        
        print(Fore.GREEN + f"[+] MAC address changed to: {new_mac}" + Style.RESET_ALL)
        return True
    except Exception as e:
        print(Fore.RED + f"[!] Failed to change MAC address: {str(e)}" + Style.RESET_ALL)
        return False

# --- TOR LAN ---

def change_lan_ip():
    print(Fore.YELLOW + "\n[*] Changing LAN IP using Tor..." + Style.RESET_ALL)
    
    try:
        tor_check = subprocess.call("which tor", shell=True)
        if tor_check != 0:
            print(Fore.RED + "[!] Tor is not installed. Installing now..." + Style.RESET_ALL)
            subprocess.call("apt-get install tor -y", shell=True)
        
        subprocess.call("service tor start", shell=True)
        subprocess.call("echo 'socks5 127.0.0.1 9050' > /etc/proxychains.conf", shell=True)
        
        print(Fore.GREEN + "[+] LAN IP changed through Tor network" + Style.RESET_ALL)
        return True
    except Exception as e:
        print(Fore.RED + f"[!] Failed to change LAN IP: {str(e)}" + Style.RESET_ALL)
        return False

# --- WAN IP & PROXY SECTION (UPDATED with Solution 1) ---

def check_and_install_tor():
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
    """
    Updated Robust Proxy Fetcher & Tester.
    INCLUDES INSTRUCTIONS FOR MANUAL BROWSER CONFIG.
    """
    
    PROXY_SOURCES = [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all",
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
    ]
    
    print(Fore.CYAN + "\n[*] Fetching fresh proxy list (SOCKS5)..." + Style.RESET_ALL)
    
    candidates = []
    
    for url in PROXY_SOURCES:
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                matches = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+", r.text)
                candidates.extend(matches)
        except:
            continue
            
    candidates = list(set(candidates))
    
    if not candidates:
        print(Fore.RED + "[!] No proxies found. Check internet connection." + Style.RESET_ALL)
        return False
        
    print(Fore.YELLOW + f"[*] Testing {min(20, len(candidates))} candidates (out of {len(candidates)} found)..." + Style.RESET_ALL)
    
    # Test Proxies
    for proxy in random.sample(candidates, min(20, len(candidates))):
        try:
            proxies = {
                'http': f'socks5://{proxy}',
                'https': f'socks5://{proxy}'
            }
            
            print(f"\rTesting: {proxy} ... ", end="", flush=True)
            
            response = requests.get('https://api.ipify.org?format=json', proxies=proxies, timeout=5)
            
            if response.status_code == 200:
                new_ip = response.json().get('ip')
                
                # --- UPDATED OUTPUT FOR USER ---
                print(Fore.GREEN + f"\n\n[✓] SUCCESS! Working Proxy Found!" + Style.RESET_ALL)
                print(Fore.GREEN + f"    Proxy Address: {proxy}" + Style.RESET_ALL)
                print(Fore.GREEN + f"    External IP seen by target: {new_ip}" + Style.RESET_ALL)
                
                print(Fore.YELLOW + "\n[!] ATTENTION: Your system IP has NOT changed automatically." + Style.RESET_ALL)
                print(Fore.YELLOW + f"    To browse anonymously, configure your browser manually:" + Style.RESET_ALL)
                
                print(Fore.CYAN + f"    1. Open Firefox > Settings > Network Settings" + Style.RESET_ALL)
                print(Fore.CYAN + f"    2. Select 'Manual proxy configuration'" + Style.RESET_ALL)
                
                # Parse IP and Port
                try:
                    ip_addr, port = proxy.split(':')
                    print(Fore.CYAN + f"    3. SOCKS Host: {ip_addr}  |  Port: {port}" + Style.RESET_ALL)
                except:
                    print(Fore.CYAN + f"    3. SOCKS Host: (Use IP from above) | Port: (Use Port from above)" + Style.RESET_ALL)
                    
                print(Fore.CYAN + f"    4. Check 'Proxy DNS when using SOCKS v5'" + Style.RESET_ALL)
                print(Fore.CYAN + f"    5. Click OK and browse." + Style.RESET_ALL)

                # Save working proxy
                with open("j-proxies-working.txt", "w") as f:
                    f.write(proxy)
                return True
                
        except:
            continue
                
    print(Fore.RED + "\n[!] Proxies timed out. Switching to Tor fallback..." + Style.RESET_ALL)
    return False

def enable_tor_mode():
    try:
        try:
            subprocess.run(["sudo", "systemctl", "is-active", "--quiet", "tor"])
        except:
            print(Fore.YELLOW + "[!] Starting Tor service..." + Style.RESET_ALL)
            subprocess.run(["sudo", "systemctl", "start", "tor"], check=True)
            time.sleep(5)

        print(Fore.CYAN + "[*] Switching to Tor Circuit..." + Style.RESET_ALL)
        
        try:
            tor_auth = "sudo cat /var/run/tor/control.authcookie | xxd -ps"
            auth_cookie = subprocess.run(tor_auth, shell=True, check=True, capture_output=True, text=True).stdout.strip()
            rotate_cmd = f"echo -e 'AUTHENTICATE {auth_cookie}\\nSIGNAL NEWNYM' | nc 127.0.0.1 9051"
            subprocess.run(rotate_cmd, shell=True, check=True)
            print(Fore.YELLOW + "[*] Rotating Tor identity..." + Style.RESET_ALL)
            time.sleep(5)
        except:
            pass 

        # Verify Tor IP (Script only check)
        try:
            new_ip = requests.get(
                "https://api.ipify.org",
                proxies={"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"},
                timeout=20
            ).text
            
            print(Fore.GREEN + f"[✓] Tor Active | New IP: {new_ip}" + Style.RESET_ALL)
            print(Fore.YELLOW + "[!] Configure browser to use SOCKS5 127.0.0.1:9050" + Style.RESET_ALL)
            return True
                
        except Exception as e:
            print(Fore.RED + f"[!] Tor check failed: {str(e)[:100]}" + Style.RESET_ALL)
            return False

    except Exception as e:
        print(Fore.RED + f"[!] Tor error: {str(e)[:100]}" + Style.RESET_ALL)
        return False

def change_wan_ip():
    print(Fore.YELLOW + "\n[*] Initializing WAN IP Finder..." + Style.RESET_ALL)
    check_dependencies()
    
    if not check_and_install_tor():
        print(Fore.RED + "[!] tor installation failed" + Style.RESET_ALL)
        return False
    
    # Try Proxies First
    if fetch_and_test_proxies():
        return True
    else:
        print(Fore.YELLOW + "[!] Proxy methods failed. Falling back to Tor..." + Style.RESET_ALL)
        return enable_tor_mode()

# --- VPN SECTIONS ---

def check_install_protonvpn():
    print(Fore.YELLOW + "\n[*] Checking ProtonVPN installation..." + Style.RESET_ALL)
    if 'VIRTUAL_ENV' in os.environ:
        venv_cli = os.path.join(os.environ['VIRTUAL_ENV'], 'bin', 'protonvpn')
        try:
            subprocess.run([venv_cli, "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return "cli-venv"
        except: pass
    try:
        subprocess.run(["protonvpn", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return "cli-system"
    except: pass
    try:
        subprocess.run(["proton-vpn", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return "gui"
    except:
        print(Fore.RED + "[!] No ProtonVPN installation found" + Style.RESET_ALL)
        return False

def enable_protonvpn():
    vpn_type = check_install_protonvpn()
    if not vpn_type: return False

    try:
        if vpn_type.startswith("cli"):
            protonvpn_path = os.path.join(os.environ.get('VIRTUAL_ENV', ''), 'bin', 'protonvpn') if vpn_type == "cli-venv" else "protonvpn"
            print(Fore.YELLOW + "[*] Connecting via CLI..." + Style.RESET_ALL)
            result = subprocess.run(["sudo", protonvpn_path, "connect", "--fastest"], capture_output=True, text=True)
            if "Connected" in result.stdout:
                vpn_ip = requests.get("https://api.ipify.org", timeout=10).text
                print(Fore.GREEN + f"[✓] VPN Connected | IP: {vpn_ip}" + Style.RESET_ALL)
                return True
        elif vpn_type == "gui":
            print(Fore.YELLOW + "[*] Launching GUI..." + Style.RESET_ALL)
            subprocess.Popen(["proton-vpn"])
            input("Press Enter AFTER you've established the VPN connection...")
            return True
    except Exception as e:
        print(Fore.RED + f"[!] VPN Error: {str(e)[:100]}" + Style.RESET_ALL)
        return False

def disable_protonvpn():
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

# --- OPENVPN (UPDATED with Credentials Support) ---

def get_tun_interface():
    try:
        output = subprocess.check_output(["ip", "addr"], text=True)
        match = re.search(r"(\btun\d+|\btap\d+):", output)
        return match.group(1) if match else None
    except: return None

def is_openvpn_connected():
    iface = get_tun_interface()
    if not iface: return False
    try:
        output = subprocess.check_output(["ip", "-4", "addr", "show", iface], text=True)
        return bool(re.search(r"inet\s+\d+\.\d+\.\d+\.\d+", output))
    except: return False

def connect_openvpn():
    config_dir = "openvpn"
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        print(Fore.RED + f"[!] Directory '{config_dir}' was missing." + Style.RESET_ALL)
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

    # --- CREDENTIALS INPUT ---
    print(Fore.YELLOW + "\n[*] Credentials Check:" + Style.RESET_ALL)
    print("If your VPN file requires a username/password, enter them now.")
    print("If not, just press Enter to skip.")
    username = input("Enter Username: ")
    
    auth_arg = []
    auth_file_path = f"openvpn/pass_{configs[choice]}.txt"

    if username:
        password = input("Enter Password: ")
        # Create temp auth file
        try:
            with open(auth_file_path, "w") as f:
                f.write(f"{username}\n{password}")
            os.chmod(auth_file_path, 0o600) # Secure file
            auth_arg = ["--auth-user-pass", auth_file_path]
        except Exception as e:
            print(Fore.RED + f"[!] Error saving credentials: {e}" + Style.RESET_ALL)
            return False
    # -------------------------

    log_path = f"report/openvpn_{configs[choice]}.log"
    os.makedirs("report", exist_ok=True)
    print(Fore.YELLOW + f"[*] Connecting to {configs[choice]}..." + Style.RESET_ALL)
    
    # Construct command
    command = ["sudo", "openvpn", "--config", config_path] + auth_arg

    with open(log_path, "w") as log_file:
        process = subprocess.Popen(
            command,
            stdout=log_file, stderr=log_file, preexec_fn=os.setsid
        )

    start_time = time.time()
    success = False
    
    while time.time() - start_time < 30:
        time.sleep(1)
        try:
            with open(log_path, "r") as log_file:
                logs = log_file.read()
                if "Initialization Sequence Completed" in logs:
                    success = True
                    break
                if "AUTH_FAILED" in logs:
                    print(Fore.RED + "[!] Authentication Failed (Wrong Username/Password)" + Style.RESET_ALL)
                    break
        except: pass
        if process.poll() is not None: break

    # Cleanup Auth File
    if os.path.exists(auth_file_path):
        try: os.remove(auth_file_path)
        except: pass

    if success and is_openvpn_connected():
        print(Fore.GREEN + f"[✓] Connected to {configs[choice]}" + Style.RESET_ALL)
        return True
    else:
        print(Fore.RED + "[!] Connection timed out or failed. Check log at: " + log_path + Style.RESET_ALL)
        try: os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        except: pass
        return False

def disconnect_openvpn():
    try:
        print(Fore.YELLOW + "[*] Disconnecting OpenVPN..." + Style.RESET_ALL)
        subprocess.run(["sudo", "pkill", "-f", "openvpn"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)
        iface = get_tun_interface()
        if iface:
            subprocess.run(["sudo", "ip", "link", "delete", iface], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(Fore.GREEN + "[✓] OpenVPN disconnected" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"[!] Failed to disconnect: {e}" + Style.RESET_ALL)

# --- MAIN MENU ---

def main_menu():
    while True:
        print(Fore.CYAN + "\nJ-Anonymous Main Menu:" + Style.RESET_ALL)
        print("1. Show current network information")
        print("2. Change MAC address")
        print("3. Change LAN IP (using Tor)")
        print("4. Find Proxy / Change WAN IP (Manual Set)")
        print("5. Change ALL (MAC, LAN, Proxy)")
        print("6. Connect ProtonVPN")
        print("7. Disconnect ProtonVPN")
        print("8. Connect OpenVPN (Any .ovpn file)")
        print("9. Disconnect OpenVPN")
        print("10. Exit")
        
        choice = input("\nEnter your choice (1-10): ")
        
        if choice == "1": get_current_info()
        elif choice == "2": change_mac()
        elif choice == "3": change_lan_ip()
        elif choice == "4": change_wan_ip()
        elif choice == "5":
            print(Fore.YELLOW + "\n[*] Changing ALL network identifiers..." + Style.RESET_ALL)
            change_mac()
            change_lan_ip()
            change_wan_ip()
            print(Fore.GREEN + "[+] Tasks completed." + Style.RESET_ALL)
        elif choice == "6": enable_protonvpn()
        elif choice == "7": disable_protonvpn()
        elif choice == "8": connect_openvpn()
        elif choice == "9": disconnect_openvpn()
        elif choice == "10":
            print(Fore.YELLOW + "\n Exiting J-Anonymous.\n Stay safe!" + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + "[-_-] Invalid choice. Please try again." + Style.RESET_ALL)

def main():
    show_banner()
    check_root()
    check_dependencies()
    main_menu()

if __name__ == "__main__":
     main()
