import json

class JSONDatabase:
    def __init__(self, filename="data.json"):
        self.filename = filename

    def load_data(self):
        try:
            with open(self.filename, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            self.save_data({})
            return {}

    def save_data(self, data):
        with open(self.filename, "w") as file:
            json.dump(data, file, indent=4)

    def set_data(self, key, value):
        data = self.load_data()
        data[key] = value
        self.save_data(data)

    def get_data(self, key):
        data = self.load_data()
        return data.get(key, None)
        
db = JSONDatabase()

import socket
import threading
import signal
import sys

class TCPServer:
    def __init__(self, port, message_handler):
        self.ip = self.get_local_ip()
        self.port = port
        self.server_socket = None
        self.message_handler = message_handler
        self.clients = []
        print(f"TCP Sunucu {self.ip}:{self.port} adresinde çalışıyor...")

    def start(self):
        self.open_server_socket()
        signal.signal(signal.SIGINT, self.signal_handler)  # Ctrl+C sinyalini yakala
        while True:
            client_socket, address = self.server_socket.accept()
            print(f"Bağlantı alındı: {address}")
            self.clients.append(client_socket)
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def stop(self):
        self.close_server_socket()
        sys.exit(0)

    def signal_handler(self, sig, frame):
        print("\nCtrl+C algılandı. Sunucu durduruluyor...")
        self.stop()

    def open_server_socket(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Portu hızla yeniden kullanmak için
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(5)

    def close_server_socket(self):
        if self.server_socket:
            self.server_socket.close()
            print(f"TCP Sunucu {self.ip}:{self.port} adresinde durduruldu.")

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                self.message_handler(data.decode())
            except Exception as e:
                print(f"Hata: {e}")
                break
        client_socket.close()
        self.clients.remove(client_socket)

    def send_to_all(self, message):
        for client_socket in self.clients:
            try:
                client_socket.send(message.encode())
            except Exception as e:
                print(f"Hata: {e}")

    def get_local_ip(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(("8.8.8.8", 80))
            ip = sock.getsockname()[0]
            sock.close()
            return ip
        except Exception as e:
            print(f"IP adresi alınamadı: {e}")
            return "127.0.0.1"
            
def message_handler(message):
    data = message.strip()[1:-1].split(",")
    parsed_data = [item.strip() for item in data]
    if parsed_data[0] == "SET":
        db.set_data(parsed_data[1], parsed_data[2])
    if parsed_data[0] == "GET":
        getted_data = db.get_data(parsed_data[1];
        if(getted_data) server.send_to_all( "(" + getted_data + ")")
        else server.send_to_all( "(NULL)") 
        
server = TCPServer(12343, message_handler)
server.start()
