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
from colorama import Fore, Style, init
import urllib3
import os
import threading

# ================= CONFIGURATION =================
MY_TARGET_UID = "7318254145"  # 🎯 Tera UID screenshot se uthaya hai
# =================================================

init(autoreset=True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Colors:
    BRIGHT = Style.BRIGHT
    RESET = Style.RESET_ALL

SUCCESS_COUNTER = 0
LIKE_SUCCESS_COUNTER = 0
LOCK = threading.Lock()

hex_key = "32656534343831396539623435393838343531343130363762323831363231383734643064356437616639643866376530306331653534373135623764316533"
key = bytes.fromhex(hex_key)

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

# --- Fixed Like Function ---
def send_like(jwt_token, region):
    global LIKE_SUCCESS_COUNTER
    try:
        # Region selection
        url = "https://client.ind.freefiremobile.com/MajorLike" if region == "IND" else "https://clientbp.ggblueshark.com/MajorLike"
        
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/x-www-form-urlencoded",
            "ReleaseVersion": "OB52",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; ASUS_Z01QD Build/PI)",
            "X-GA": "v1 1"
        }
        
        # Like Payload (Field 1: Target UID, Field 2: Type/Action)
        payload = {1: int(MY_TARGET_UID), 2: 1} 
        proto_payload = CrEaTe_ProTo(payload)
        encrypted_body = E_AEs(proto_payload.hex())
        
        res = requests.post(url, headers=headers, data=encrypted_body, verify=False, timeout=10)
        
        if res.status_code == 200:
            with LOCK: LIKE_SUCCESS_COUNTER += 1
            return True
    except: pass
    return False

def generate_guest_and_like(region, name_prefix):
    global SUCCESS_COUNTER
    try:
        password = f"{name_prefix}{random.randint(100,999)}RIZER"
        reg_data = f"password={password}&client_type=2&source=2&app_id=100067"
        sig = hmac.new(key, reg_data.encode(), hashlib.sha256).hexdigest()
        
        headers = {"Authorization": "Signature " + sig, "Content-Type": "application/x-www-form-urlencoded"}
        r = requests.post("https://100067.connect.garena.com/oauth/guest/register", headers=headers, data=reg_data, verify=False)
        
        if 'uid' in r.json():
            uid = r.json()['uid']
            t_res = requests.post("https://100067.connect.garena.com/oauth/guest/token/grant", data={"uid": uid, "password": password, "response_type": "token", "client_type": "2", "client_id": "100067"}, verify=False)
            
            if 'access_token' in t_res.json():
                token = t_res.json()["access_token"]
                open_id = t_res.json()['open_id']
                
                # Registering Name
                final_name = f"{name_prefix}{random.randint(10,99)}"
                reg_payload = {1: final_name, 2: token, 3: open_id, 15: "hi"}
                requests.post("https://login.ind.freefiremobile.com/MajorRegister", data=E_AEs(CrEaTe_ProTo(reg_payload).hex()), verify=False)
                
                # 🔥 Send Like
                with LOCK: SUCCESS_COUNTER += 1
                like_done = send_like(token, region)
                
                status_clr = Fore.GREEN if like_done else Fore.RED
                print(f"{Fore.CYAN}[{SUCCESS_COUNTER}] Guest: {final_name} | UID: {uid} | Like: {status_clr}{'SUCCESS' if like_done else 'FAILED'}{Colors.RESET}")
                return True
    except Exception as e: print(f"Error: {e}")
    return False

def main():
    os.system('clear')
    print(f"{Fore.LIGHTMAGENTA_EX}{Colors.BRIGHT}   BIGBULL AUTO-LIKE FIX")
    print(f"{Fore.YELLOW}🎯 Target UID: {MY_TARGET_UID}")
    print("-" * 35)
    
    count = int(input("Kitne Likes chahiye?: "))
    region = "IND" # Shortcut for you
    prefix = input("Bot Name Prefix: ")

    print(f"\n{Fore.GREEN}🚀 Starting Fix Bot...{Colors.RESET}\n")
    
    for _ in range(count):
        generate_guest_and_like(region, prefix)
        time.sleep(1.5)

    print(f"\n{Fore.GREEN}✅ DONE! Total Guests: {SUCCESS_COUNTER} | Total Likes: {LIKE_SUCCESS_COUNTER}")

if __name__ == "__main__":
    main()
