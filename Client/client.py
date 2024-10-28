import socket
import threading
import json

class ChatClient:
    HEADER = 64
    FORMAT = "utf-8"
    DISCONNECT_MSG = "DISCONNECT"
    PORT = 4001
    SERVER_ADDR = "127.0.0.1"
    def __init__(self, message_callback=None):
        self.message_callback = message_callback    
    
    def parse_address(self, address):
        try:
            server_address, port_str = address.split(':')
            port = int(port_str)
            return server_address, port
        except Exception as ve:
            print(f"Error parsing port: {ve}")
            return None, None
        
    def run_client(self, custom_address=None):
        custom_ip, custom_port = self.parse_address(custom_address)
        if custom_ip:
            self.SERVER_ADDR = custom_ip
            if custom_port:
                self.PORT = int(custom_port)
        
        self.ADDR = (self.SERVER_ADDR, self.PORT)

        self.client_link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_link.connect(self.ADDR)
        except Exception as e:
            print("Server is not running: " + str(e))
            exit()
        # Start the background thread for receiving messages
        self.background_thread = threading.Thread(target=self.receive_and_print)
        self.background_thread.daemon = True
        self.background_thread.start()
    
    def receive_and_print(self):
        while True:
            try:
                data_length = self.client_link.recv(self.HEADER).decode(self.FORMAT)
                if data_length:
                    data_length = int(data_length)
                    user_data = self.client_link.recv(data_length).decode(self.FORMAT)                
                    if user_data:
                        user_data = json.loads(user_data)
                        self.message_callback(user_data)
            except ConnectionResetError:
                print("Server disconnected.")
                exit()
            except ValueError as ve:
                print(f"Error converting message length to int: {ve}")
            except:
                print("Something went wrong.")

    def send_message(self, data):
        data = json.dumps(data)
        user_data = data.encode(self.FORMAT)

        data_length = len(user_data)

        # Send data length
        send_length = str(data_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER - len(send_length))
        self.client_link.send(send_length)

        # Send data
        self.client_link.send(user_data)

    def disconnect(self, userdata):
        self.send_message(userdata)
        self.client_link.close()
        exit()

