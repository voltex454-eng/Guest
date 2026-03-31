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
import threading

# ================= CONFIGURATION =================
MY_TARGET_UID = "1234567890"  # 🎯 YAHAN APNA FF UID DALO
# =================================================

init(autoreset=True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Colors:
    BRIGHT = Style.BRIGHT
    RESET = Style.RESET_ALL

# Global Counters
SUCCESS_COUNTER = 0
LIKE_SUCCESS_COUNTER = 0
LOCK = threading.Lock()

# Folders Setup
BASE_FOLDER = "BIGBULL-ERA"
TOKENS_FOLDER = os.path.join(BASE_FOLDER, "TOKENS-JWT")
os.makedirs(TOKENS_FOLDER, exist_ok=True)

# Garena Keys & Data
REGION_LANG = {"IND": "hi","BR": "pt","ME": "ar","ID": "id","VN": "vi","TH": "th","BD": "bn","PK": "ur"}
hex_key = "32656534343831396539623435393838343531343130363762323831363231383734643064356437616639643866376530306331653534373135623764316533"
key = bytes.fromhex(hex_key)

# --- ENCRYPTION & PROTOBUF UTILS ---

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

def CrEaTe_ProTo(fields):
    packet = bytearray()    
    for field, value in fields.items():
        if isinstance(value, int):
            header = (field << 3) | 0
            packet.extend(EnC_Vr(header) + EnC_Vr(value))
        elif isinstance(value, (str, bytes)):
            header = (field << 3) | 2
            data = value.encode() if isinstance(value, str) else value
            packet.extend(EnC_Vr(header) + EnC_Vr(len(data)) + data)
    return packet

def E_AEs(Pc):
    Z = bytes.fromhex(Pc)
    aes_key = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iv = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    K = AES.new(aes_key, AES.MODE_CBC, iv)
    return K.encrypt(pad(Z, AES.block_size))

# --- 🔥 AUTO-LIKE FUNCTION 🔥 ---

def send_like(jwt_token, region):
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
        encrypted_body = E_AEs(CrEaTe_ProTo(payload).hex())
        res = requests.post(url, headers=headers, data=encrypted_body, verify=False, timeout=10)
        if res.status_code == 200:
            with LOCK: LIKE_SUCCESS_COUNTER += 1
            print(f"{Fore.LIGHTGREEN_EX}❤️  LIKE SENT! | Total Likes: {LIKE_SUCCESS_COUNTER}{Colors.RESET}")
            return True
    except: pass
    return False

# --- ACCOUNT LOGIC ---

def generate_guest_and_like(region, name_prefix):
    global SUCCESS_COUNTER
    try:
        # 1. Register Guest
        password = f"{name_prefix}_{random.randint(1000,9999)}_RIZER"
        reg_data = f"password={password}&client_type=2&source=2&app_id=100067"
        sig = hmac.new(key, reg_data.encode(), hashlib.sha256).hexdigest()
        
        headers = {"Authorization": "Signature " + sig, "Content-Type": "application/x-www-form-urlencoded"}
        r = requests.post("https://100067.connect.garena.com/oauth/guest/register", headers=headers, data=reg_data, verify=False)
        
        if 'uid' in r.json():
            uid = r.json()['uid']
            # 2. Get Access Token
            t_res = requests.post("https://100067.connect.garena.com/oauth/guest/token/grant", data={"uid": uid, "password": password, "response_type": "token", "client_type": "2", "client_id": "100067"}, verify=False)
            
            if 'access_token' in t_res.json():
                token = t_res.json()["access_token"]
                open_id = t_res.json()['open_id']
                
                # 3. Major Register (Name Setup)
                final_name = f"{name_prefix}{random.randint(10,99)}"
                reg_payload = {1: final_name, 2: token, 3: open_id, 15: REGION_LANG.get(region, "en")}
                requests.post("https://loginbp.ggblueshark.com/MajorRegister", data=E_AEs(CrEaTe_ProTo(reg_payload).hex()), verify=False)
                
                # 4. 🔥 Send Like Using Token
                with LOCK: SUCCESS_COUNTER += 1
                print(f"{Fore.CYAN}[{SUCCESS_COUNTER}] Guest: {final_name} | UID: {uid}{Colors.RESET}")
                send_like(token, region)
                return True
    except Exception as e:
        print(f"Error: {e}")
    return False

# --- MAIN INTERFACE ---

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"""{Fore.LIGHTMAGENTA_EX}{Colors.BRIGHT}
    ██████╗░██╗░██████╗░██████╗░██╗░░░██╗██╗░░░░░
    ██╔══██╗██║██╔════╝░██╔══██╗██║░░░██║██║░░░░░
    ██████╦╝██║██║░░██╗░██████╦╝██║░░░██║██║░░░░░
    ██╔══██╗██║██║░░╚██╗██╔══██╗██║░░░██║██║░░░░░
    ██████╦╝██║╚██████╔╝██████╦╝╚██████╔╝███████╗
    {Colors.RESET}""")
    print(f"{Fore.YELLOW}🎯 Target UID: {MY_TARGET_UID}{Colors.RESET}")
    print("-" * 45)
    
    count = int(input(f"{Fore.WHITE}Kitne Likes chahiye?: {Colors.RESET}"))
    region = input(f"{Fore.WHITE}Region (IND/BR/ME): {Colors.RESET}").upper()
    prefix = input(f"{Fore.WHITE}Bot Name Prefix: {Colors.RESET}")

    print(f"\n{Fore.GREEN}🚀 Starting Auto-Like Bot...{Colors.RESET}\n")
    
    for _ in range(count):
        generate_guest_and_like(region, prefix)
        time.sleep(1.2) # Garena protection ke liye safe delay

    print(f"\n{Fore.GREEN}✅ DONE! Total Guests: {SUCCESS_COUNTER} | Total Likes: {LIKE_SUCCESS_COUNTER}{Colors.RESET}")

if __name__ == "__main__":
    main()
