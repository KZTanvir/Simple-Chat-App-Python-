# Chat Application

## Introduction

The Chat Application is a Python-based project that aims to create a simple and user-friendly chat application with features like customizable usernames, a graphical user interface (GUI), message sending and receiving, and a dynamic server IP configuration. The project consists of multiple components, including a Chat Server, Chat Client, and a User Interface built with Tkinter.

## Project Components

### Chat Server

The Chat Server is responsible for managing client connections, handling messages, and providing a platform for users to interact. It offers the following features:

- **Socket Communication:** The server creates a socket to communicate with connected clients.
- **Server Configuration:** Parameters like header size, format, disconnect message, IP address, and port can be customized.
- **Graceful Shutdown:** The server can be stopped gracefully when a SIGINT (Ctrl+C) signal is received.
- **Message Handling:** It handles incoming messages from clients and processes specific commands like `/Jarvis` for AI responses and `/Weather` for weather information.
- **Dynamic IP Option:** The server can run with either a dynamically determined or custom IP address, providing flexibility.

### Chat Client

The Chat Client is the counterpart of the server, responsible for client-side communication. Its features include:

- **Socket Communication:** The Chat Client class uses sockets to connect to the server.
- **Custom Server IP:** Users can provide a custom server IP address.
- **Background Thread:** A background thread is employed for receiving and processing incoming messages.
- **Message Callback:** Users can define a custom function to handle incoming messages, allowing interaction with the user interface.
- **Message Sending:** The client can send messages to the server, which are tagged with the sender's username.
- **Disconnect Functionality:** The client can send a disconnect message to the server and close the socket connection.
- **Error Handling:** The client script includes error handling for various scenarios, enhancing reliability.

### User Interface

The User Interface is built using the Tkinter library, offering a visually appealing environment for users to interact with the chat application. Its features comprise:

- **Graphical User Interface (GUI):** The application includes various elements, such as username input, message display, message input, and buttons for sending messages and disconnecting.
- **Username Submission:** Users can submit their usernames, after which the input field and submit button become disabled.
- **Message Display:** Messages are displayed in a scrollable area, with different styles for user and system messages.
- **Message Formatting:** Messages sent by the user include the sender's username and are tagged with a specific style.
- **Disconnect Button:** Users can click the "Disconnect" button to gracefully exit the chat application.
- **Random User Color:** Each user is assigned a random color for message differentiation.
- **Server Configuration:** Users can enter the server's IP address when the application starts, making it adaptable for different servers.

## Developer Information

The project includes information about the developer, such as name, ID, GitHub profile, project completion date, and website. This information provides transparency and contact details for users interested in the project or seeking support.

## Conclusion

The Chat Application project combines the functionalities of a Chat Server, Chat Client, and User Interface to create a simple, visually appealing, and interactive chat environment. Users can join the chat, send messages, customize their usernames, and gracefully disconnect. The project's flexibility in server configuration, error handling, and message formatting enhances its reliability and usability.

The Chat Application project serves as a foundation for developing chat applications for various purposes, such as personal communication, team collaboration, or customer support. It can be further extended and customized to meet specific requirements and integrate additional features.

