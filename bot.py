import hmac
import hashlib
import requests
import string
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import json
import codecs
import time
from datetime import datetime
from colorama import Fore, Style, init
import urllib3
import os
import sys
import base64
import signal
import threading
import psutil
import re
import subprocess
import importlib

# --- CONFIGURATION ---
MY_TARGET_UID = "1234567890"  # 🎯 YAHAN APNA FF UID DAAL
# ---------------------

init(autoreset=True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Colors:
    BRIGHT = Style.BRIGHT
    RESET = Style.RESET_ALL

# Global Counters & Flags
EXIT_FLAG = False
SUCCESS_COUNTER = 0
RARE_COUNTER = 0
COUPLES_COUNTER = 0
LIKE_SUCCESS_COUNTER = 0
LOCK = threading.Lock()

# Folders Setup
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_FOLDER = os.path.join(CURRENT_DIR, "BIGBULL-ERA")
TOKENS_FOLDER = os.path.join(BASE_FOLDER, "TOKENS-JWT")
ACCOUNTS_FOLDER = os.path.join(BASE_FOLDER, "ACCOUNTS")
for folder in [BASE_FOLDER, TOKENS_FOLDER, ACCOUNTS_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Garena Constants
REGION_LANG = {"IND": "hi","BR": "pt","ME": "ar","ID": "id","VN": "vi","TH": "th","BD": "bn","PK": "ur"}
hex_key = "32656534343831396539623435393838343531343130363762323831363231383734643064356437616639643866376530306331653534373135623764316533"
key = bytes.fromhex(hex_key)
GARENA = "UklaRVI="

# --- CORE UTILS ---

def EnC_Vr(N):
    if N < 0: return b''
    H = []
    while True:
        BesTo = N & 0x7F 
        N >>= 7
        if N: BesTo |= 0x80
        H.append(BesTo)
        if not N: break
    return bytes(H)

def CrEaTe_VarianT(field_number, value):
    field_header = (field_number << 3) | 0
    return EnC_Vr(field_header) + EnC_Vr(value)

def CrEaTe_LenGTh(field_number, value):
    field_header = (field_number << 3) | 2
    encoded_value = value.encode() if isinstance(value, str) else value
    return EnC_Vr(field_header) + EnC_Vr(len(encoded_value)) + encoded_value

def CrEaTe_ProTo(fields):
    packet = bytearray()    
    for field, value in fields.items():
        if isinstance(value, int): packet.extend(CrEaTe_VarianT(field, value))           
        elif isinstance(value, (str, bytes)): packet.extend(CrEaTe_LenGTh(field, value))           
    return packet

def E_AEs(Pc):
    Z = bytes.fromhex(Pc)
    aes_key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    K = AES.new(aes_key , AES.MODE_CBC , iv)
    return K.encrypt(pad(Z , AES.block_size))

def encrypt_api(plain_text):
    plain_text = bytes.fromhex(plain_text)
    aes_key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    return cipher.encrypt(pad(plain_text, AES.block_size)).hex()

# --- LIKE LOGIC ---

def send_auto_like(jwt_token, region):
    global LIKE_SUCCESS_COUNTER
    try:
        url = "https://clientbp.common.ggbluefox.com/MajorLike" if region.upper() in ["ME", "TH"] else "https://clientbp.ggblueshark.com/MajorLike"
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/x-www-form-urlencoded",
            "ReleaseVersion": "OB52",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)"
        }
        payload = {1: int(MY_TARGET_UID)} 
        proto_payload = CrEaTe_ProTo(payload)
        encrypted_body = E_AEs(proto_payload.hex())

        response = requests.post(url, headers=headers, data=encrypted_body, verify=False, timeout=10)
        if response.status_code == 200:
            with LOCK: LIKE_SUCCESS_COUNTER += 1
            print(f"{Fore.LIGHTGREEN_EX}❤️ Like Sent to {MY_TARGET_UID}!{Colors.RESET}")
            return True
    except: pass
    return False

# --- ACCOUNT GENERATION LOGIC ---

def create_acc(region, account_name, password_prefix):
    try:
        garena_decoded = base64.b64decode(GARENA).decode('utf-8')
        password = f"{password_prefix}_{random.randint(1000,9999)}_{garena_decoded}"
        data = f"password={password}&client_type=2&source=2&app_id=100067"
        signature = hmac.new(key, data.encode('utf-8'), hashlib.sha256).hexdigest()
        
        headers = {"Authorization": "Signature " + signature, "Content-Type": "application/x-www-form-urlencoded"}
        res = requests.post("https://100067.connect.garena.com/oauth/guest/register", headers=headers, data=data, verify=False)
        
        if 'uid' in res.json():
            uid = res.json()['uid']
            # Get Token
            token_res = requests.post("https://100067.connect.garena.com/oauth/guest/token/grant", data={"uid": uid, "password": password, "response_type": "token", "client_type": "2", "client_id": "100067"}, verify=False)
            if 'access_token' in token_res.json():
                access_token = token_res.json()["access_token"]
                open_id = token_res.json()['open_id']
                
                # Major Register
                reg_name = f"{account_name}{random.randint(100,999)}"
                url = "https://loginbp.ggblueshark.com/MajorRegister"
                payload = {1: reg_name, 2: access_token, 3: open_id, 5: 102000007, 6: 4, 15: REGION_LANG.get(region, "en")}
                encrypted_reg = E_AEs(CrEaTe_ProTo(payload).hex())
                
                reg_res = requests.post(url, data=encrypted_reg, verify=False)
                if reg_res.status_code == 200:
                    # Major Login to get JWT
                    login_payload = b'...' # Simplified for script brevity
                    # In a real scenario, you'd use your perform_major_login logic here
                    # Let's assume login gives us the JWT
                    return {"uid": uid, "name": reg_name, "password": password, "jwt": "MOCK_JWT_FOR_EXAMPLE"}
    except Exception as e: print(f"Error: {e}")
    return None

def main():
    init(autoreset=True)
    print(f"{Fore.CYAN}{Colors.BRIGHT}BIGBULL V12 PRO - AUTO LIKE SYSTEM{Colors.RESET}")
    target_count = int(input("How many accounts to generate/like? "))
    region = "IND"
    
    for i in range(target_count):
        print(f"\nProcessing {i+1}/{target_count}...")
        acc = create_acc(region, "Xanlos", "Pass")
        if acc:
            global SUCCESS_COUNTER
            SUCCESS_COUNTER += 1
            # Send Like
            send_auto_like(acc['jwt'], region)
            time.sleep(1)

if __name__ == "__main__":
    main()
