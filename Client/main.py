import tkinter as tk
from tkinter import scrolledtext
from tkinter import simpledialog
from client import ChatClient
import random

class ChatApp:
    def __init__(self, master, client=None):
        self.master = master
        master.title("Simple Chat App")
        master.geometry("490x550")
        master.config(bg="#040D12")
        self.title_label = tk.Label(master, text="Simple Chat App", font=('Arial', 16, 'bold'), background='#040D12', width=40, fg="white")
        self.title_label.grid(row=0, column=0, columnspan=4, pady=10)

        self.client = client
        self.username_entry = None
        self.submit_username_button = None
        self.message_display = None
        self.message_entry = None
        self.send_button = None
        self.disconnect_button = None

        self.username = None
        self.server_addr = None
        self.user_color = random.choice(['green', 'blue', 'white', 'black', 'gray', 'orange', 'purple', 'pink'])

    def ask_ip(self):
        self.server_addr = simpledialog.askstring("Server IP", "Enter Server IP:")

    def setup_ui(self):
        self.ask_ip()
        self.create_devDetails()
        self.create_username_entry()
        self.create_submit_username_button()
        self.create_message_display()
        self.create_message_entry()
        self.create_send_button()
        self.create_disconnect_button()

    def create_devDetails(self):
        self.dev_frame = tk.Frame(self.master, background='#040D12')
        self.dev_frame.grid(row=1, column=0, columnspan=4, padx=5, pady=5)

        self.sec1 = tk.Frame(self.dev_frame, background='#040D12')
        self.sec1.grid(row=0, column=0, sticky=tk.W, padx=10)
        self.sec2 = tk.Frame(self.dev_frame, background='#040D12')
        self.sec2.grid(row=0, column=1, sticky=tk.E, padx=10)

        self.devDetails = tk.Label(self.sec1, text="Name         : Md.Kamruzzaman", font=('Arial', 10, 'bold'), background='#040D12', fg="#FAF0E6")
        self.devDetails.grid(row=0, column=0, sticky=tk.W, padx=4)
        self.devDetails = tk.Label(self.sec1, text="ID              : 201400059", font=('Arial', 10, 'bold'), background='#040D12', fg="#FAF0E6")
        self.devDetails.grid(row=2, column=0, sticky=tk.W, padx=4)
        self.devDetails = tk.Label(self.sec1, text="GitHub       : KZTanvir", font=('Arial', 10, 'bold'), background='#040D12', fg="#FAF0E6")
        self.devDetails.grid(row=3, column=0, sticky=tk.W, padx=4)
        self.devDetails = tk.Label(self.sec1, text="Completed : 02.11.23", font=('Arial', 10, 'bold'), background='#040D12', fg="#FAF0E6")
        self.devDetails.grid(row=5, column=0, sticky=tk.W, padx=4)
        self.devDetails = tk.Label(self.sec1, text="Web           : kamruzzaman.tech", font=('Arial', 10, 'bold'), background='#040D12', fg="#FAF0E6")
        self.devDetails.grid(row=4, column=0, sticky=tk.W, padx=4)

    def create_username_entry(self):
        self.usernameL = tk.Label(self.sec2, text="User Name", font=('Arial', 10, 'bold'), background='#040D12', fg="#FAF0E6")
        self.usernameL.grid(row=0, column=0, columnspan=2, pady=4, padx=2, sticky=tk.W)
        self.username_entry = tk.Entry(self.sec2, width=20, font=('Arial', 10, 'bold'), border=0, highlightthickness=0, background='#5C8374', fg="#FAF0E6")
        self.username_entry.grid(row=1, column=0, ipady=4, padx=4, pady=4)

    def create_submit_username_button(self):
        self.submit_username_button = tk.Button(self.sec2, text="Submit", border=0, highlightthickness=0, command=self.submit_username, font=('Arial',10,'bold'), background='#5C8374', fg="#FAF0E6")
        self.submit_username_button.grid(row=1, column=1, padx=2,)

    def create_message_display(self):
        self.message_display = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, width=50, height=20, state=tk.DISABLED, font=('Arial', 10, 'bold'), border=0, highlightthickness=0, background='#0E1F28', fg="#FAF0E6")
        self.message_display.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky=tk.W + tk.E + tk.N + tk.S)
        self.message_display.tag_config("USER_MSG", foreground="#FAF0E6")


    def create_message_entry(self):
        self.message_entry = tk.Entry(self.master, width=30, font=('Arial', 12, 'bold'), border=0, highlightthickness=0, background='#5C8374', fg="#FAF0E6")
        self.message_entry.grid(row=3, column=0, columnspan=2, ipady=4, padx=10, pady=10, sticky=tk.W + tk.E)

    def create_send_button(self):
        self.send_button = tk.Button(self.master, text="Send", command=self.send_message, font=('Arial', 12, 'bold'), border=0, highlightthickness=0, background='#5C8374', fg="#FAF0E6")
        self.send_button.grid(row=3, column=2, pady=10, sticky=tk.W + tk.E)

    def create_disconnect_button(self):
        self.disconnect_button = tk.Button(self.master, text="Disconnect", command=self.disconnect, font=('Arial', 12, 'bold'), border=0, highlightthickness=0, background='#5C8374', fg="#FAF0E6")
        self.disconnect_button.grid(row=3, column=3, columnspan=5, pady=10, padx=10, sticky=tk.W + tk.E)


    def submit_username(self):
        self.username = self.username_entry.get()
        if self.username:
            self.username_entry.config(state=tk.DISABLED)
            self.submit_username_button.config(state=tk.DISABLED)
            self.message_entry.focus()
            self.sec2.config(highlightthickness=0, border=0, relief=None)
            self.master.after(1000, lambda: self.client.run_client(custom_ip=self.server_addr))#run client after 1 second

    def send_message(self):
        message = self.message_entry.get()
        user_data = {
            "uname": f"{self.username}",
            "msg": f"{message}",
            "utype": "USER", #SYSTEM, BOT, USER, ERROR
            "color": self.user_color, 
            "is_self": "y"
        }
        if self.username and message:
            self.message_display.config(state=tk.NORMAL)
            self.client.send_message(user_data)
            self.message_display.config(state=tk.DISABLED)
            self.message_display.yview(tk.END)
            self.message_entry.delete(0, tk.END)
        
    def message_callback(self, user_data):
        if user_data:
            self.message_display.config(state=tk.NORMAL)
            self.message_display.tag_config(user_data['uname']+user_data['is_self'], foreground=user_data['color'])
            if user_data['utype'] == "USER":
                self.message_display.insert(tk.END, f"{user_data['uname']}{'(you)' if user_data['is_self'] == 'y' else ''}:", user_data['uname']+user_data['is_self'])
                self.message_display.insert(tk.END, f" {user_data['msg']}\n", "USER_MSG")
            elif user_data['utype'] == "BOT":
                self.message_display.insert(tk.END, f"{user_data['uname']}:\n{user_data['msg']}\n", user_data['uname']+user_data['is_self'])
            elif user_data['utype'] == "SYSTEM":
                self.message_display.insert(tk.END, f"{user_data['uname']}: {user_data['msg']}\n", user_data['uname']+user_data['is_self'])
            self.message_display.config(state=tk.DISABLED)
            self.message_display.see(tk.END)
    
    def disconnect(self):
        self.client.disconnect({"uname": self.username, "msg": "DISCONNECT", "utype": "USER", "color": "", "is_self": ""})
        self.master.destroy()

class ChatAppWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        # Create an instance of ChatClient and pass the display_message method as message_callback
        self.client = ChatClient(message_callback=self.message_callback)

        self.chat_app = ChatApp(self, client=self.client)
        #turningthe interface on
        self.chat_app.setup_ui()

    def message_callback(self, user_data):
        self.chat_app.message_callback(user_data)

if __name__ == "__main__":
    app = ChatAppWindow()
    app.mainloop()

