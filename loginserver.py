import socket
import json
import threading
import shelve
import secrets
import string
from datetime import datetime
import ssl
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import bcrypt


HOST = "0.0.0.0"
PORT = 12346
DB_FILE = "users.db"
BUFFER_SIZE = 1024
LOCK = threading.Lock()

# TLS Certificate and generated key
CERT_FILE = 'PyWavesClientCert.pem'
KEY_FILE = 'PyWavesServerPrivateKey.pem'

# In-memory token list
active_tokens = {}
certificates_found = False # tells the server if certificates were loaded


def hash_password(password):
    """Hash a password using bcrypt with automatic salt generation"""
    # Convert string to bytes
    password_bytes = password.encode('utf-8')

    # Generate salt and hash in one step
    # The salt is automatically included in the returned hash
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed


def verify_password(password, hashed):
    """Verify a password against its bcrypt hash"""
    password_bytes = password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed)


def hash_password_with_rounds(password, rounds=12):
    """Hash password with custom work factor (rounds)

    Args:
        password: The password to hash
        rounds: Work factor (4-31). Higher = more secure but slower
                Default 12 is good for most applications
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=rounds)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed


def generate_token(length=20):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

def generate_AES_key():
    return AESGCM.generate_key(bit_length=128)

def save_token(token, index, key):
    tokenindexdict = {'token':token,'key': key, 'timestamp' : datetime.now()}
    active_tokens[index] = tokenindexdict


def handle_client(clientsocket, addr, context):
    print(f"[+] Connected by {addr}")
    try:
        with context.wrap_socket(clientsocket, server_side=True) as ssock:
            data = ssock.recv(BUFFER_SIZE).decode('utf-8')
            print(f"[>] Received: {data}")
            message = json.loads(data)

            username = message.get("username", "").strip()
            password = message.get("password", "").strip()
            action_type = message.get("type", "").strip().lower()

            if not username or not password or action_type not in ("login", "register"):
                ssock.sendall(b"fail")
                return

            with LOCK:
                with shelve.open(DB_FILE, writeback=True) as db:
                    if action_type == "register":
                        if username in db:
                            ssock.sendall(b"already exists")
                        else:
                            db[username] = hash_password(password)
                            print (username, password, db[username])
                            token = generate_token(20)
                            index = generate_token(10)
                            key = generate_AES_key()
                            save_token(token, index, key)
                            response = {"status": "success", "token": token, "index": index, "key": base64.b64encode(key).decode('utf-8')}
                            ssock.sendall(json.dumps(response).encode('utf-8'))
                            print(f"[+] Registered user: {username} | Token: {token}")

                    elif action_type == "login":
                        if username in db:
                            if verify_password(password, db[username]):
                                token = generate_token(20)
                                index = generate_token(10)
                                key = generate_AES_key()
                                save_token(token, index, key)
                                response = {"status": "success", "token": token, "index": index, "key": base64.b64encode(key).decode('utf-8')}
                                ssock.sendall(json.dumps(response).encode('utf-8'))
                                print(f"[+] Logged in user: {username} | Token: {token} | Index: " + index)
                            else:
                                ssock.sendall(b"fail")
                        else:
                            ssock.sendall(b"fail")
    except Exception as e:
        print(f"[!] Error: {e}")
        try:
            ssock.sendall(b"fail")
        except:
            pass
    finally:
        clientsocket.close()
        print(f"[-] Disconnected {addr}")

def start_server():
    print(f"[*] Starting server on port {PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)

        print("[*] Server is listening...")

        while True:
            clientsocket, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(clientsocket, addr, context), daemon=True).start()

if __name__ == "__main__":
    start_server()
