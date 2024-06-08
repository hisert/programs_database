import sqlite3
import socket
import threading
import signal
import sys

class SQLiteDatabase:
    def __init__(self, db_name="data.db"):
        self.db_name = db_name
        self.connection = self.create_connection()
        self.create_table()

    def create_connection(self):
        conn = sqlite3.connect(self.db_name, check_same_thread=False)
        return conn

    def create_table(self):
        with self.connection:
            self.connection.execute(
                "CREATE TABLE IF NOT EXISTS data (key TEXT PRIMARY KEY, value TEXT)"
            )

    def set_data(self, key, value):
        with self.connection:
            self.connection.execute(
                "REPLACE INTO data (key, value) VALUES (?, ?)", (key, value)
            )

    def get_data(self, key):
        cursor = self.connection.cursor()
        cursor.execute("SELECT value FROM data WHERE key = ?", (key,))
        result = cursor.fetchone()
        return result[0] if result else None

    def del_data(self, key):
        with self.connection:
            self.connection.execute("DELETE FROM data WHERE key = ?", (key,))

    def print_all_data(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT key, value FROM data")
        rows = cursor.fetchall()
        for row in rows:
            print(f"Key: {row[0]}, Value: {row[1]}")

class TCPServer:
    def __init__(self, port, message_handler):
        self.port = port
        self.server_socket = None
        self.message_handler = message_handler
        self.clients = []

    def start(self):
        self.open_server_socket()
        signal.signal(signal.SIGINT, self.signal_handler)
        while True:
            client_socket, address = self.server_socket.accept()
            self.clients.append(client_socket)
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def stop(self):
        self.close_server_socket()
        sys.exit(0)

    def signal_handler(self, sig, frame):
        self.stop()

    def open_server_socket(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("", self.port))
        self.server_socket.listen(5)

    def close_server_socket(self):
        if self.server_socket:
            for client in self.clients:
                client.close()
            self.server_socket.close()

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                self.message_handler(data.decode())
            except Exception as e:
                break
        client_socket.close()
        self.clients.remove(client_socket)

    def send_to_all(self, message):
        for client_socket in self.clients:
            try:
                client_socket.send(message.encode())
            except Exception as e:
                print(f"Hata: {e}")

    def get_host_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except Exception:
            ip = "127.0.0.1"
        return ip

def message_handler(message):
    data = message.strip()[1:-1].split(",")
    parsed_data = [item.strip() for item in data]
    if parsed_data[0] == "SET":
        db.set_data(parsed_data[1], parsed_data[2])
    elif parsed_data[0] == "GET":
        getted_data = db.get_data(parsed_data[1])
        if getted_data:
            server.send_to_all(f"({getted_data})")
        else:
            server.send_to_all("(NULL)")
    elif parsed_data[0] == "DEL":
        db.del_data(parsed_data[1])
    elif parsed_data[0] == "PRINT_ALL":
        db.print_all_data()

db = SQLiteDatabase()
server = TCPServer(4040, message_handler)
server.start()
