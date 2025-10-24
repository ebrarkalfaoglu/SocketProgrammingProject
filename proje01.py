import socket
import time
import argparse
import json
import sys
import ntplib
from time import ctime
import datetime
import psutil

#server parameters
host = 'localhost'
data_payload = 2048 #maks data payload
backlog = 5 #max no. of queued connections

def print_machine_info(): #this function prints machine info
    host_name = socket.gethostname()
    ip_address = socket.gethostbyname(host_name)
    print("Host name: %s" % host_name)
    print("IP address: %s" % ip_address)
    print("\n")

    net_inf = psutil.net_if_addrs()  #list all network interfaces

    for interface_name, addresses in net_inf.items():
        print(f"Network Interfaces: {interface_name}")

def echo_server(port): #this function is echo server
    """A simple echo server"""
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create TCP socket
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #enable reuse port
    #address binding
    server_address = (host, port)
    print("\nStarting up echo server on %s port %s" % server_address)
    sock.bind(server_address) #bind socket to port
    sock.listen(backlog) #listen to clients

    while True:
        print("\nWaiting to receive message from client")
        client, address = sock.accept() #add a new connection
        data = client.recv(data_payload) #receive data from client
        if data:
            print("Data received:", data.decode())
            client.send(data) #send data back to client
            print("Sent back to", address)
        client.close() #end connection

def get_sntp_time():
    try:
        client = ntplib.NTPClient()
        response = client.request('pool.ntp.org') #request time from SNTP server
        print("Current time from SNTP server:", ctime(response.tx_time))

        local_time = datetime.datetime.now() #get local system time
        print("Local system time:", local_time.ctime())

        difference = response.tx_time - local_time.timestamp() #calculate time difference
        print("Time difference (seconds):", difference)

    except Exception as e:
        print("Error fetching SNTP time:", e)
          
      
def chat_server():
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 12345))  #accept connections on all interfaces
    server_socket.listen(1)
    print("Chat server started, waiting for connection...")

    conn, addr = server_socket.accept()
    print(f"{addr} connected.") 

    with open("chat_log.txt", "a") as f: #save chat log to file
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            print("Client:", data)
            f.write(f"[{ctime()}] Client: {data}\n")

            msg = input("You: ") #send message to client
            conn.send(msg.encode())
            f.write(f"[{ctime()}] Server: {msg}\n")

    conn.close()
    server_socket.close()


def chat_client():
    client_socket = socket.socket()
    client_socket.connect(('127.0.0.1', 12345))  #connect to server
    print("Connected to server!")

    with open("chat_log.txt", "a") as f: #save chat log to file
        while True:
            msg = input("You: ")
            client_socket.send(msg.encode())
            f.write(f"[{ctime()}] Client: {msg}\n")

            data = client_socket.recv(1024).decode()
            if not data:
                break
            print("Server:", data)
            f.write(f"[{ctime()}] Server: {data}\n")

    client_socket.close()

def configure_socket_settings(sock):
    
    sock.settimeout(3) #set timeout to 3 seconds
    
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4096) #set send buffer size
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8192) #set receive buffer size
    
    sock.setblocking(False) #set non-blocking mode
    
    print("\n--- SOCKET SETTINGS ---") #print current socket settings
    print("Timeout:", sock.gettimeout())
    print("Send buffer size:", sock.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF))
    print("Receive buffer size:", sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF))
    print("Blocking mode:", "Blocking" if sock.getblocking() else "Non-blocking")


def test_connection():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #connect to a test server
    configure_socket_settings(s)

    try:
        print("\nTrying to connect to server...")
        s.connect(('127.0.0.1', 12345))
        print("Connection successful!")

        s.send(b"Hello, server!")
        data = s.recv(1024)
        print("Received:", data.decode())

    #error handling for different socket errors
    except BlockingIOError: 
        print("Non-blocking connect in progress...")
    except ConnectionRefusedError:
        print("Connection refused by the server.")
    except socket.timeout:
        print("Connection attempt timed out.")
    except OSError as e:
        print("General socket error:", e)
    finally:
        s.close()
        print("Socket closed.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Machine Info + Echo Server')
    parser.add_argument('--port', action="store", dest="port", type=int, required=True) #port argument

    given_args = parser.parse_args()
    port = given_args.port

    # Menu for user to select functionality
    print("1 - System Info\n2 - Echo Server\n3 - SNTP Time\n4 - Chat (Server/Client)\n5 - Error Management Test")
    choice = input("Your choice: ")

    if choice == '1':
        print_machine_info()
    elif choice == '2':
        echo_server(port)
    elif choice == '3':
        get_sntp_time()
    elif choice == '4':
        mode = input("Server or Client? (s/c): ").lower()
        if mode == 's':
            chat_server()
        elif mode == 'c':
            chat_client()
        else:
            print("Invalid choice!")
    elif choice == '5':
        configure_socket_settings(socket.socket())
        test_connection()
    else:
        print("Invalid selection!")        