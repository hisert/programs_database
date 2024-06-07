import socket
import threading

class TCPServer:
    def __init__(self, port, message_handler):
        self.ip = self.get_local_ip()
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(5)
        self.message_handler = message_handler
        self.clients = []
        print(f"TCP Sunucu {self.ip}:{self.port} adresinde çalışıyor...")

    def start(self):
        while True:
            client_socket, address = self.server_socket.accept()
            print(f"Bağlantı alındı: {address}")
            self.clients.append(client_socket)
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                self.message_handler(data.decode())
                processed_data = data.decode().upper()
                self.send_to_all(processed_data)  # Tüm bağlı istemcilere işlenmiş veriyi gönder
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
    print("Gelen mesaj:", message)

def main():
    port = 12345
    server = TCPServer(port, message_handler)
    server.start()

if __name__ == "__main__":
    main()
