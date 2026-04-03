# Writing Ransomware (`ransomware.py`)

---

## Description
A Python script demonstrating ransomware techniques that:
1. Encrypts `my_secrets.txt` using AES-128-CBC
2. Encrypts the symmetric key with RSA-2048
3. Performs secure file deletion
4. Generates ransom note

---

## Prerequisites
- Kali Linux VM 
- Python 3.8+
- OpenSSL installed
- `cryptography` package

---

## Usage

### 1. Install Dependencies
```bash
sudo apt install openssl python3-pip
pip3 install cryptography

# Create test file with sample content
echo "This is a secret file for demo purposes" > my_secrets.txt

# Run the ransomware simulation
python3 ransomware.py