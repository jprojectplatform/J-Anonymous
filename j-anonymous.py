#!/usr/bin/env python3

import os
import random
import subprocess
import time
import requests
import re
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
        wan_ip = requests.get('https://api.ipify.org').text
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


# Change WAN IP (kwa VPN or proxy)

def check_and_install_curl():
    """Check if curl is installed, install if missing"""
    try:
        subprocess.run(["curl", "--version"], 
                      check=True, 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL)
        return True
    except:
        print(Fore.YELLOW + "[!] Installing curl..." + Style.RESET_ALL)
        return subprocess.run(["sudo", "apt", "install", "curl", "-y"], 
                            check=False).returncode == 0

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
    """Attempt to fetch and test proxies from multiple sources"""
    PROXY_APIS = [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all",
        "https://www.proxy-list.download/api/v1/get?type=http",
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"
    ]
    
    for api_url in PROXY_APIS:
        try:
            print(Fore.CYAN + f"[*] Attempting proxy source: {api_url.split('/')[2]}" + Style.RESET_ALL)
            
            result = subprocess.run(
                f'curl --connect-timeout 10 --retry 1 "{api_url}" -o J-Proxies.txt',
                shell=True,
                stderr=subprocess.PIPE,
                timeout=15
            )
            
            if result.returncode != 0:
                raise Exception(result.stderr.decode().strip())
                
            with open("J-Proxies.txt", "r") as f:
                proxies = [p.strip() for p in f.readlines() if p.strip()]
                
            if not proxies:
                raise Exception("Empty proxy list")
                
            print(Fore.GREEN + f"[+] Retrieved {len(proxies)} proxies" + Style.RESET_ALL)
            
            for proxy in random.sample(proxies, min(5, len(proxies))):
                try:
                    test_ip = requests.get(
                        "https://api.ipify.org?format=json",
                        proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"},
                        timeout=5
                    ).json().get("ip")
                    
                    if test_ip:
                        print(Fore.GREEN + f"[✓] Working proxy: {proxy}" + Style.RESET_ALL)
                        print(Fore.GREEN + f"[+] New WAN IP: {test_ip}" + Style.RESET_ALL)
                        return True
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(Fore.RED + f"[!] Proxy source failed: {str(e)[:100]}" + Style.RESET_ALL)
            continue
            
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
        try:
            old_ip = requests.get(
                "https://api.ipify.org",
                proxies={"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"},
                timeout=15
            ).text
            print(Fore.CYAN + f"[*] Current Tor IP: {old_ip}" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"[!] Initial Tor check failed: {str(e)[:100]}" + Style.RESET_ALL)
            old_ip = None

        # 3. Rotate IP (with proper authentication)
        tor_auth = "sudo cat /var/run/tor/control.authcookie | xxd -ps"
        auth_cookie = subprocess.run(tor_auth, shell=True, check=True, capture_output=True, text=True).stdout.strip()
        
        rotate_cmd = f"echo -e 'AUTHENTICATE {auth_cookie}\\nSIGNAL NEWNYM' | nc 127.0.0.1 9051"
        subprocess.run(rotate_cmd, shell=True, check=True)
        print(Fore.YELLOW + "[*] Rotating Tor circuit..." + Style.RESET_ALL)
        time.sleep(10)  # Wait for circuit rebuild

        # 4. Verify new IP
        try:
            new_ip = requests.get(
                "https://api.ipify.org",
                proxies={"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"},
                timeout=20
            ).text
            
            if new_ip != old_ip:
                print(Fore.GREEN + f"[✓] Tor IP rotated: {new_ip}" + Style.RESET_ALL)
                return True
            else:
                print(Fore.RED + "[!] Tor IP unchanged after rotation" + Style.RESET_ALL)
                return False
                
        except Exception as e:
            print(Fore.RED + f"[!] Final Tor check failed: {str(e)[:100]}" + Style.RESET_ALL)
            return False

    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"[!] Tor control failed: {str(e)[:100]}" + Style.RESET_ALL)
        return False
    except Exception as e:
        print(Fore.RED + f"[!] Tor error: {str(e)[:100]}" + Style.RESET_ALL)
        return False

def change_wan_ip():
    print(Fore.YELLOW + "\n[*] Initializing WAN IP change..." + Style.RESET_ALL)
    
    if not check_and_install_curl():
        print(Fore.RED + "[!] curl installation failed" + Style.RESET_ALL)
        return False
        
    if not check_and_install_tor():
        print(Fore.RED + "[!] tor installation failed" + Style.RESET_ALL)
        return False
    
    if not fetch_and_test_proxies():
        print(Fore.YELLOW + "[!] Proxy methods failed. Falling back to Tor..." + Style.RESET_ALL)
        return enable_tor_mode()
        
    return True
        
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
        print(Fore.RED + "[!] Install ProtonVPN first:" + Style.RESET_ALL)
        print(Fore.YELLOW + "For CLI in virtual environment:\n" +
              "1. Activate venv: source j-anonymous-env/bin/activate\n" +
              "2. Install: pip3 install protonvpn-cli\n" +
              "3. Initialize: sudo $(which protonvpn) init\n\n" +
              "For system-wide CLI:\n" +
              "sudo apt install openvpn dialog python3-pip && " +
              "sudo pip3 install protonvpn-cli && " +
              "sudo protonvpn init\n\n" +
              "For GUI version:\n" +
              "Download from https://protonvpn.com/download" + Style.RESET_ALL)
        return False

    try:
        if vpn_type.startswith("cli"):
            # Use venv path if available
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
            print(Fore.CYAN + "[!] Please click 'Quick Connect' in the ProtonVPN GUI window" + Style.RESET_ALL)
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
            print(Fore.YELLOW + "[*] Disconnecting via CLI..." + Style.RESET_ALL)
            subprocess.run(
                ["sudo", protonvpn_path, "disconnect"],
                check=True,
                stdout=subprocess.PIPE
            )
        elif vpn_type == "gui":
            print(Fore.YELLOW + "[*] Disconnecting via GUI..." + Style.RESET_ALL)
            subprocess.run(
                ["proton-vpn", "--disconnect"],
                check=True,
                stdout=subprocess.PIPE
            )
            
        print(Fore.GREEN + "[✓] VPN disconnected" + Style.RESET_ALL)
        return True
        
    except Exception as e:
        print(Fore.RED + f"[!] Disconnect failed: {str(e)[:100]}" + Style.RESET_ALL)
        return False
        
        
 # Nimeongeza OpenVPN kwa .ovpn Files       
        
def check_install_openvpn():
    """Check if OpenVPN is installed"""
    try:
        subprocess.run(["openvpn", "--version"], 
                      check=True, 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE)
        return True
    except:
        return False


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
    configs = sorted([f for f in os.listdir(config_dir) if f.endswith(".ovpn")])
    if not configs:
        print(Fore.RED + "[!] No .ovpn configs found" + Style.RESET_ALL)
        main_menu()  # fallback to menu
        return False

    print(Fore.CYAN + "\nAvailable VPN Configs:" + Style.RESET_ALL)
    [print(f"{i+1}. {name}") for i, name in enumerate(configs)]
    
    try:
        choice = int(input(Fore.YELLOW + f"\nSelect config (1-{len(configs)}): " + Style.RESET_ALL)) - 1
        config_path = f"{config_dir}/{configs[choice]}"
    except:
        print(Fore.RED + "[!] Invalid selection" + Style.RESET_ALL)
        main_menu()
        return False

    log_path = f"report/openvpn_{configs[choice]}.log"
    os.makedirs("report", exist_ok=True)

    print(Fore.YELLOW + f"[*] Connecting to {configs[choice]}..." + Style.RESET_ALL)
    with open(log_path, "w") as log_file:
        process = subprocess.Popen(
            ["sudo", "openvpn", "--config", config_path],
            stdout=log_file,
            stderr=log_file
        )

    # Wait for connection
    success = False
    start_time = time.time()
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
            with open(log_path, "r") as log_file:
                print(Fore.RED + "[!] OpenVPN crashed:\n" + log_file.read()[-500:] + Style.RESET_ALL)
            main_menu()
            return False

    if success and is_openvpn_connected():
        print(Fore.GREEN + f"[✓] Connected to {configs[choice]}" + Style.RESET_ALL)
        try:
            vpn_ip = requests.get('https://api.ipify.org', timeout=5).text
            print(Fore.CYAN + f"[*] VPN IP: {vpn_ip}" + Style.RESET_ALL)
        except:
            print(Fore.YELLOW + "[!] Could not verify external IP" + Style.RESET_ALL)
    else:
        print(Fore.RED + "[!] Connection timed out or failed" + Style.RESET_ALL)
        process.terminate()

    # Continue to main menu regardless
    main_menu()
    return True

def disconnect_openvpn():
    """Stop any running OpenVPN process"""
    try:
        print(Fore.YELLOW + "[*] Disconnecting OpenVPN..." + Style.RESET_ALL)
        subprocess.run(["sudo", "pkill", "-f", "openvpn"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)

        iface = get_tun_interface()
        if iface:
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
        print("4. Change WAN IP (using Proxies/Tor) [Partial]")
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
    main_menu()


if __name__ == "__main__":
     main()
