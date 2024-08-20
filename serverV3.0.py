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
UPLOAD_DIR = 'uploads/'

if not os.path.isfile(USER_FILE):
    with open(USER_FILE, 'w') as f:
        json.dump({}, f)

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

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

def get_server_info():
    return "Server Info: Python Socket Server, version 1.0"

def get_server_time():
    return f"Server Time: {datetime.now()}"

def get_server_status():
    return "Server Status: Online. Active connections: 0"

def list_users():
    with open(USER_FILE, 'r') as f:
        users = json.load(f)
    return "Registered Users: " + ", ".join(users.keys()) if users else "No registered users."

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
            
            elif message.startswith("login "):
                try:
                    _, username, password = message.split(" ", 2)
                    if authenticate(username, password):
                        client_socket.sendall("Authentication successful".encode('utf-8'))
                        authenticated = True
                        log_event(f"User authenticated: {username}")
                    else:
                        client_socket.sendall("Authentication failed".encode('utf-8'))
                except ValueError:
                    client_socket.sendall("Invalid authentication format. Use: login <username> <password>".encode('utf-8'))
            
            else:
                client_socket.sendall("Invalid command. Use 'register' or 'login'.".encode('utf-8'))

        while True:
            command = client_socket.recv(1024).decode('utf-8')
            if not command:
                break
            
            response = process_command(command, client_socket)
            client_socket.sendall(response.encode('utf-8'))

    except Exception as e:
        log_event(f"An error occurred: {e}")
        print(f"An error occurred: {e}")
    finally:
        client_socket.close()

def process_command(command, client_socket):
    if command == "server_info":
        return get_server_info()
    
    elif command == "server_time":
        return get_server_time()
    
    elif command == "server_status":
        return get_server_status()
    
    elif command == "logout":
        return "Logged out. Please reconnect to login with a different account."
    
    elif command == "clear":
        return "Command not supported on server. (For client-side terminal clearing, use 'clear' or 'cls')."
    
    elif command.startswith("message "):
        try:
            _, username, message = command.split(" ", 2)
            return f"Message to {username}: {message}"
        except ValueError:
            return "Invalid message format. Use: message <username> <message>"

    elif command == "list_users":
        return list_users()

    elif command.startswith("upload "):
        try:
            _, filename = command.split(" ", 1)
            filepath = os.path.join(UPLOAD_DIR, filename)
            with open(filepath, 'wb') as f:
                while True:
                    file_data = client_socket.recv(1024)
                    if not file_data:
                        break
                    f.write(file_data)
            return f"File '{filename}' uploaded successfully."
        except ValueError:
            return "Invalid upload format. Use: upload <filename>"

    elif command.startswith("download "):
        try:
            _, filename = command.split(" ", 1)
            filepath = os.path.join(UPLOAD_DIR, filename)
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    while True:
                        file_data = f.read(1024)
                        if not file_data:
                            break
                        client_socket.sendall(file_data)
                return f"File '{filename}' downloaded successfully."
            else:
                return "File not found."
        except ValueError:
            return "Invalid download format. Use: download <filename>"

    elif command == "help":
        return ("Available commands:\n"
                "1. server_info - Get server information\n"
                "2. server_time - Get the current server time\n"
                "3. server_status - Get the status of the server\n"
                "4. logout - Log out of the current account\n"
                "5. clear - Clear the client terminal screen (client-side)\n"
                "6. message <username> <message> - Send a message to another user\n"
                "7. list_users - List all registered users\n"
                "8. upload <filename> - Upload a file to the server\n"
                "9. download <filename> - Download a file from the server\n"
                "10. help - Display this help message")

    else:
        return "Unknown command"

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
