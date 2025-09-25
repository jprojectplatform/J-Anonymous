# 🚀 **J-Anonymous: Universal Network Privacy Toolkit**  

![Banner](https://i.imgur.com/sUH82c5.png) 

**Be Invisible. Stay Secure. Take Control.**  

---

## 🔥 **About J-Anonymous**  
J-Anonymous is an advanced network privacy toolkit designed for cybersecurity professionals, ethical hackers, and privacy-conscious users. This Python-based tool allows you to:  
- 🛡️ **Change MAC addresses** dynamically  
- 🌐 **Rotate LAN/WAN IPs** via Tor, proxies, or VPNs  
- 🔄 **Spoof network identities** with one click  
- ⚡ **Integrate with ProtonVPN & OpenVPN** seamlessly  

**Project Platform:** [J Project Platform](https://jprojectplatform.com/)  
**Created By:** [JH4CK3R](https://portfolio.jprojectplatform.com/)  

---

## 🛠️ **Features**  
| Feature | Description |  
|---------|-------------|  
| **MAC Changer** | Generate and set random MAC addresses |  
| **Tor Integration** | Route traffic through Tor network |  
| **Proxy Rotation** | Auto-fetch and test working HTTP proxies |  
| **VPN Control** | Supports ProtonVPN (CLI/GUI) and OpenVPN configs |  
| **Network Obfuscation** | Change ALL identifiers (MAC+LAN+WAN) simultaneously |  

---

## ⚡ **Installation Guide (Kali Linux)**  

### **1. Clone the Repository**  
```bash
git clone https://github.com/jprojectplatform/J-Anonymous.git
cd J-Anonymous
```

### **2. Install Dependencies**  
```bash
# Update system
sudo apt update

# Install Python3 and pip
sudo apt install python3 python3-pip -y

# Install requirements
python3 -m venv j-anonymous-env
source j-anonymous-env/bin/activate
pip install -r requirements.txt


# Install system dependencies
sudo apt install tor proxychains curl openvpn -y

# Setup TOR
A) sudo mousepad /etc/tor/torrc
		# Add hizi
		ControlPort 9051
		CookieAuthentication 1

B) sudo apt install xxd -y
```

### **3. Set Up ProtonVPN (Optional)**  
```bash
# For CLI version:
source j-anonymous-env/bin/activate
sudo apt install openvpn dialog python3-pip
pip3 install protonvpn-cli
sudo $(which protonvpn) init   # Follow setup wizard

# For GUI version:
Download from https://protonvpn.com/download
```

### **4. Add OpenVPN Configs**  
Place your `.ovpn` files in the `openvpn/` directory.  

---

## 🚦 **Usage**  
Run as root:  
```bash
sudo python3 j-anonymous.py
```

### **Menu Options**  
1. **Show current network info**  
2. **Change MAC address**  
3. **Change LAN IP (Tor)**  
4. **Change WAN IP (Proxies/Tor)**  
5. **Change ALL identifiers**  
6. **Connect ProtonVPN**  
7. **Disconnect ProtonVPN**  
8. **Connect OpenVPN**  
9. **Disconnect OpenVPN**  

---

## 📺 Video Tutorial (Click Image Below)
*Watch the step-by-step guide to install and use J-Anonymous:*  

[![How to Use J-Anonymous](https://i.imgur.com/DAku3VY.png)](https://youtu.be/SzQUwJZf2NU?si=rMS0kpewT4EdObqK)

---

## 📜 **License**  
This project is licensed under **J Project License (JPL)**.  
*Use responsibly and only on networks you own or have permission to test.*  

---

## 🌟 **Why J-Anonymous?**  
- ✅ **All-in-One** privacy toolkit  
- ✅ **No external dependencies** (except VPN services)  
- ✅ **Works out-of-the-box** on Kali Linux  
- ✅ **Active development** with regular updates  

---

## 🤝 **Contribute**  
Found a bug? Want a new feature?  
- Open an **Issue**  
- Submit a **Pull Request**  
- Join our community at [J Project Platform](https://jprojectplatform.com/)  

---

💙 **Enjoy With J Project Platform**  
**"Hands With Universal Technology"**  

```bash
# Start your privacy journey now!
sudo python3 j-anonymous.py
```  

![Footer](https://i.imgur.com/cMkRvyf.png)  

---  
*Start Your Hacking Journey Safe*
---
*Disclaimer: This tool is for educational and authorized testing only. Misuse violates laws in many countries.*
