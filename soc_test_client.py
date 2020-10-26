import socket
import argparse
import threading

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 0))
    return s.getsockname()[0]

def send_handler(client_socket):
    while True:
        data = input()
        client_socket.send(data.encode('utf-8'))
    client_socket.close()

if __name__ == '__main__':
    server_ip = get_ip_address()
    port = 8282

    client = "Gesture"
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, port))
    client_socket.send(client.encode('utf-8'))

    send_thread = threading.Thread(target=send_handler, args=(client_socket,))
    send_thread.daemon = True
    send_thread.start()
    send_thread.join()
