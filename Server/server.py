import socket
import threading
import signal
import string
import json
import random
from pyngrok import ngrok
from bot import KZTJarvis, AccuWeatherAPI, GuessNumberGame

class ChatServer:
    HEADER = 64
    FORMAT = "utf-8"
    DISCONNECT_MSG = "DISCONNECT"
    userlist = []
    # Add a global variable to control the server loop
    server_running = True
    ngrok_tunnel = None
    def __init__(self, host, port):
        self.PORT = port
        self.LOCAL_IP = host
        self.LOCAL_ADDR = (self.LOCAL_IP, self.PORT)

        self.server_link = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server_link.bind(self.LOCAL_ADDR)
        except OSError as e:
            print(e)
            exit()
        # Register the signal handler for graceful shutdown on Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)

        # Send the message to the GPT bot
        self.my_bot = KZTJarvis()
        self.my_bot.set_auto_config()
        #weather bot
        self.accuweather = AccuWeatherAPI()
        #game bot
        self.guess = GuessNumberGame(min_number=1, max_number=10)
        
    def generate_random_id(self, length=10):
        characters = string.ascii_letters + string.digits
        random_id = ''.join(random.choice(characters) for i in range(length))
        return random_id
        
    def signal_handler(self, sig, frame):
        print()
        if self.ngrok_tunnel:
            print("stopping ngrok...")
            self.stop_ngrok()
        print("Stopping server...")
        self.stop_server()

    def start_server(self, is_global=False):
        if is_global:
            self.start_ngrok()
            print("Global Server Address is: " + self.ngrok_tunnel.public_url)

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

    def start_ngrok(self):
        self.ngrok_tunnel = ngrok.connect(self.PORT, "tcp")
        return self.ngrok_tunnel.public_url
    
    def stop_ngrok(self):
        try:
            ngrok.kill()
        except Exception as e:
            print(e)
    
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
            if address:
                    userdata["is_self"] = "y" if user[1] == address else "n"
            try:
                self.send_message(user[0], userdata)
            except BrokenPipeError:
                # Handle BrokenPipeError (client disconnected)
                print(f"User {user[1]} disconnected unexpectedly.")
                self.userlist.remove(user)
                
    def handler(self, connection, address):
        print(f"New user {address} connected.")
        self.send_message(connection, {"uname": "SYSTEM", "msg": f"Welcome To The Server [{address if self.ngrok_tunnel is None else self.ngrok_tunnel.public_url}]", "utype": "SYSTEM", "color": "red", "is_self": "n","uid":"SYSTEM"})
        self.broadcast({"uname": "SYSTEM", "msg": "A New User Connected", "utype": "SYSTEM", "color": "red", "is_self": "n", "uid":"SYSTEM"})
        u_id = self.generate_random_id(length=5)
        username = "Anonymous"
        connected = True
        while connected:
            try:
                data_length = connection.recv(self.HEADER).decode(self.FORMAT)
                if data_length:
                    data_length = int(data_length)
                    user_data = connection.recv(data_length).decode(self.FORMAT)
                    user_data = json.loads(user_data)

                    username = user_data["uname"]
                    user_data["uid"] = u_id
                    if user_data["msg"] == self.DISCONNECT_MSG:
                        connected = False
                    else:
                        print(f"Received from {address}: {username}")
                        # Broadcast the message to all users except the sender
                        
                        self.broadcast(user_data, address)

                        user_data["is_self"] = "n"
                        if user_data["msg"].startswith("/jarvis"):
                            response, reply = self.my_bot.send(f"{username} says {user_data['msg'][7:]}")
                            user_data["uname"] = "Jarvis"
                            user_data["msg"] = reply
                            user_data["utype"] = "BOT"
                            user_data["color"] = "cyan"
                            self.broadcast(user_data)

                        if user_data["msg"].startswith("/weather"):
                            reply = self.accuweather.get_weather(user_data["msg"][8:])
                            user_data["uname"] = "AccuWeather"
                            user_data["msg"] = reply
                            user_data["utype"] = "BOT"
                            user_data["color"] = "yellow"
                            self.broadcast(user_data)

                        if user_data["msg"].startswith("/guess"):
                            user_data["uname"] = "GuessGame"
                            user_data["utype"] = "BOT"
                            user_data["color"] = "green"
                            if user_data["msg"][7:].startswith("start"):
                                reply = self.guess.add_user(username, username + u_id)
                                user_data["msg"] = reply
                                self.broadcast(user_data)
                            elif user_data["msg"][7:].startswith("leaderboard"):
                                # Print table header
                                reply = "| {:<20} | {:<8} | {:<6} |".format("Name", "Attempts", "Score") + "\n|" + "-"*22 + "|" + "-"*10 + "|" + "-"*8 + "|"

                                # Print table rows
                                for item in self.guess.load_leaderboard():
                                    reply += "\n| {:<20} | {:<8} | {:<6} |".format(item['name'], item['attempts'], item['score'])
                                user_data["msg"] = reply
                                self.broadcast(user_data)
                            elif user_data["msg"][7:].startswith("play"):
                                try:
                                    reply = self.guess.play_game(username + u_id, int(user_data["msg"][11:]))
                                except:
                                    reply = "Invalid guess, " + username + "! Please enter a number between 1 and 10."
                                user_data["msg"] = reply
                                self.broadcast(user_data)
            except ConnectionResetError:
                # Handle client disconnection
                connected = False
            except OSError as e:
                print("Error receiving message: " + str(e))
                break
            except Exception as e:
                print("Error: " + str(e))

        print(f"User {address} disconnected.({username})")
        connection.close()
        self.userlist.remove((connection, address))
        self.broadcast({"uname": "SYSTEM", "msg": f"{username} Disconnected", "utype": "SYSTEM", "color": "red", "is_self": "n", "uid":"SYSTEM"})

def get_system_ip():
    try:
        # Create a socket and connect to an external server (e.g., Google's DNS server)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            system_ip = s.getsockname()[0]
        return system_ip
    except socket.error:
        return "127.0.0.1"

if __name__ == "__main__":
    
    print("Y = run on LAN only.\nN = run as LOCALHOST\nGlobal = run as a GLOBAL/PUBLIC server.\n")
    option = input("Do you want to run the server with a dynamic ADDRESS?: ").lower()
    if option == "y":
        custom_port = input("Enter the port you want this server to run on: ")
        host = get_system_ip()
        port = int(custom_port)
    elif option == "n" or option=="global":
        port = 4001
        host = "127.0.0.1"
    else:
        print("Something went wrong. Please try again. -Tanvir")
        exit()
    server = ChatServer(host=host, port=port)
    server.start_server(is_global= option =="global")
