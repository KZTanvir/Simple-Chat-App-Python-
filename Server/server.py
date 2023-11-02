import socket
import threading
import signal
import json
from bot import KZTJarvis, AccuWeatherAPI

class ChatServer:
    def __init__(self, host, port):
        self.HEADER = 64
        self.FORMAT = "utf-8"
        self.DISCONNECT_MSG = "DISCONNECT"
        self.PORT = port
        self.LOCAL_IP = host
        self.LOCAL_ADDR = (self.LOCAL_IP, self.PORT)

        self.server_link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_link.bind(self.LOCAL_ADDR)
        self.userlist = []

        # Add a global variable to control the server loop
        self.server_running = True
        # Register the signal handler for graceful shutdown on Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)

        # Send the message to the GPT bot
        self.my_bot = KZTJarvis()
        self.my_bot.set_auto_config()
        #weather comman
        self.accuweather = AccuWeatherAPI()
        
    def signal_handler(self, sig, frame):
        print()
        print("Stopping server...")
        self.stop_server()

    def start_server(self):
        self.server_link.listen()
        print(f"Server is started and listening on {self.LOCAL_IP}:{self.PORT}")

        while self.server_running:
            try:
                connection, address = self.server_link.accept()
                thread = threading.Thread(target=self.handler, args=(connection, address))
                thread.start()

                print(f"Active connections: {threading.active_count() - 1}")
                self.userlist.append((connection, address))
            except OSError as e:
                # Handle the case where the socket is closed during server shutdown
                if self.server_running:
                    print(f"Error accepting connection: {e}")

        # Close all connections when the server is stopped
        for user in self.userlist:
            user[0].close()

    def stop_server(self):
        for user in self.userlist:
            user[0].close()
        self.server_running = False
        #self.server_link.shutdown(socket.SHUT_RDWR)
        self.server_link.close()

    def send_message(self, user_link, data):
        data=json.dumps(data)
        #send the data
        sending_data = data.encode(self.FORMAT)
        data_length = len(sending_data)
        send_length = str(data_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER - len(send_length))
        user_link.send(send_length)
        user_link.send(sending_data)
        
    def broadcast(self, userdata, address=None):
        for user in self.userlist:
            try:
                if address:
                    userdata["is_self"] = "y" if user[1] == address else "n"
                        
                self.send_message(user[0], userdata)
            except BrokenPipeError:
                # Handle BrokenPipeError (client disconnected)
                print(f"User {user[1]} disconnected unexpectedly.")
                self.userlist.remove(user)
                
    def handler(self, connection, address):
        user_data = {
            "uname": "SYSTEM",
            "msg": f"Welcome To The Server [{address}]",
            "utype": "SYSTEM", #SYSTEM, BOT, USER, ERROR
            "color": "red", 
            "is_self": "n"
        }
        print(f"New user {address} connected.")
        self.send_message(connection, user_data)
        user_data["msg"] = "A New User Connected"
        self.broadcast(user_data)
        connected = True
        while connected:
            try:
                data_length = connection.recv(self.HEADER).decode(self.FORMAT)
                if data_length:
                    data_length = int(data_length)
                    user_data = connection.recv(data_length).decode(self.FORMAT)
                    user_data = json.loads(user_data)
                    username = user_data["uname"]
                    if user_data["msg"] == self.DISCONNECT_MSG:
                        connected = False
                    else:
                        print(f"Received from {address}: {username}")
                        # Broadcast the message to all users except the sender
                        self.broadcast(user_data, address)

                        user_data["is_self"] = "n"
                        if user_data["msg"].startswith("/Jarvis"):
                            response, reply = self.my_bot.send(f"{username} says {user_data['msg'][7:]}")
                            user_data["uname"] = "Jarvis"
                            user_data["msg"] = reply
                            user_data["utype"] = "BOT"
                            user_data["color"] = "cyan"
                            self.broadcast(user_data)

                        if user_data["msg"].startswith("/Weather"):
                            reply = self.accuweather.get_weather(user_data["msg"][8:])
                            user_data["uname"] = "AccuWeather:"
                            user_data["msg"] = reply
                            user_data["utype"] = "BOT"
                            user_data["color"] = "yellow"
                            self.broadcast(user_data)

            except ConnectionResetError:
                # Handle client disconnection
                connected = False
            except OSError as e:
                print("Error receiving message: " + str(e))
                break

        print(f"User {address} disconnected.({username})")
        connection.close()
        self.userlist.remove((connection, address))
        self.broadcast({"uname": "SYSTEM", "msg": f"{username} Disconnected", "utype": "SYSTEM", "color": "red", "is_self": "n"})

def get_system_ip():
    try:
        # Create a socket and connect to an external server (e.g., Google's DNS server)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        system_ip = s.getsockname()[0]
        s.close()
        return system_ip
    except socket.error:
        return "127.0.0.1"

if __name__ == "__main__":
    custom_ip = input("Do you want to run the server with a dynamic IP? (y/n): ").lower()
    
    if custom_ip == "y":
        server = ChatServer(get_system_ip(), port=4001)
    else:
        server = ChatServer(host="127.0.0.1", port=4001)
    
    server.start_server()
