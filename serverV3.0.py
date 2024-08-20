import socket
import hashlib
import json
import os
from datetime import datetime

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345

USER_FILE = 'users.json'
LOG_FILE = 'server.log'
CONNECTION_FILE = 'connections.csv'

if not os.path.isfile(USER_FILE):
    with open(USER_FILE, 'w') as f:
        json.dump({}, f)

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def authenticate(username, password):
    with open(USER_FILE, 'r') as f:
        user_database = json.load(f)
    hashed_password = hash_password(password)
    return user_database.get(username) == hashed_password

def register(username, password):
    with open(USER_FILE, 'r') as f:
        user_database = json.load(f)
    
    if username in user_database:
        return False
    
    user_database[username] = hash_password(password)
    
    with open(USER_FILE, 'w') as f:
        json.dump(user_database, f)
    
    return True

def log_event(event):
    with open(LOG_FILE, 'a') as f:
        f.write(f"{datetime.now()}: {event}\n")

def log_connection(client_address):
    with open(CONNECTION_FILE, 'a') as f:
        f.write(f"{datetime.now()},{client_address[0]},{client_address[1]}\n")

def handle_client(client_socket, client_address):
    log_connection(client_address)
    
    try:
        client_socket.sendall("Welcome! Please register or login.".encode('utf-8'))
        
        authenticated = False
        
        while not authenticated:
            message = client_socket.recv(1024).decode('utf-8')
            
            if message.startswith("register "):
                try:
                    _, username, password = message.split(" ", 2)
                    if register(username, password):
                        client_socket.sendall("Registration successful. Please login.".encode('utf-8'))
                        log_event(f"New user registered: {username}")
                    else:
                        client_socket.sendall("Username already exists. Try another one.".encode('utf-8'))
                except ValueError:
                    client_socket.sendall("Invalid registration format. Use: register <username> <password>".encode('utf-8'))
            
            elif message.startswith("auth "):
                try:
                    _, username, password = message.split(" ", 2)
                    if authenticate(username, password):
                        client_socket.sendall("Authentication successful".encode('utf-8'))
                        authenticated = True
                        log_event(f"User authenticated: {username}")
                    else:
                        client_socket.sendall("Authentication failed".encode('utf-8'))
                except ValueError:
                    client_socket.sendall("Invalid authentication format. Use: auth <username> <password>".encode('utf-8'))
            
            else:
                client_socket.sendall("Invalid command. Use 'register' or 'auth'.".encode('utf-8'))

    except Exception as e:
        log_event(f"An error occurred: {e}")
        print(f"An error occurred: {e}")
    finally:
        client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")
    
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address}")
        handle_client(client_socket, client_address)

if __name__ == "__main__":
    start_server()
