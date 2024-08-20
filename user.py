import socket
import os

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))

    try:
        welcome_message = client_socket.recv(1024).decode('utf-8')
        print("Server:", welcome_message)
        
        while True:
            action = input("Do you want to register or login? (type 'register' or 'login'): ").strip().lower()
            if action not in ['register', 'login']:
                print("Invalid choice. Please type 'register' or 'login'.")
                continue

            username = input("Enter your username: ").strip()
            password = input("Enter your password: ").strip()

            command = f"{action} {username} {password}"
            client_socket.sendall(command.encode('utf-8'))

            response = client_socket.recv(1024).decode('utf-8')
            print("Server response:", response)

            if "Authentication successful" in response:
                print("Logged in successfully.")
                break
            elif "Registration successful" in response:
                print("Now please login using your credentials.")
            
        while True:
            command = input("Enter command: ").strip()
            if not command:
                continue
            
            if command == "clear":
                clear_screen()
                continue

            if command.startswith("upload "):
                filename = command[7:]
                with open(filename, 'rb') as f:
                    while True:
                        file_data = f.read(1024)
                        if not file_data:
                            break
                        client_socket.sendall(file_data)
                print("File uploaded successfully.")
            
            client_socket.sendall(command.encode('utf-8'))

            response = client_socket.recv(1024).decode('utf-8')
            print("Server response:", response)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()
