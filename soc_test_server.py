import socket
import argparse
import threading
import time
import copy

client_list = {}
client_name = ['Gesture', 'Action', 'Headpose']
union_data_dict = {x:'None' for x in client_name}

t_lock = threading.Lock()

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 0))
    return s.getsockname()[0]

def receive_handler(client_socket, addr, client):
    print(" --- {} container is connected".format(client))
    while True:
        data = client_socket.recv(1024).decode('utf-8')
        t_lock.acquire()
        union_data_dict[client] = data
        t_lock.release()
    client_socket.close()

def accept_func(host, port, num_of_client):
    print("#### server socket start...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))

    print("#### server socket start listening")
    server_socket.listen(num_of_client)

    while len(client_list)<num_of_client:
        try:
            client_socket, addr = server_socket.accept()
        except KeyboardInterrupt :
            cnt_client=0
            for user, con in client_list:
                con.close()
                cnt_client += 1
            server_socket.close()
            print("Keyboard Interrupt")
            print(cnt_client, " clients close")
            break

        client = client_socket.recv(1024).decode('utf-8')
        client_list[client] = client_socket

        receive_thread = threading.Thread(target=receive_handler, args=(client_socket, addr, client))
        receive_thread.daemon = True
        receive_thread.start()

if __name__ == '__main__':
    server_ip = get_ip_address()
    port = 8282
    num_of_client = 3
    Hue_ip = '192.168.0.103'
    device = {}

    # wait connect request from client
    accept_func(server_ip, port, num_of_client)
    print("#### All clients are connected")

    # connect phue
    phue_lamp = Bridge(Hue_ip)
    while True:
        try:
            phue_lamp.connect()
            device['lamp'] = phue_lamp
            break
        except:
            print("retry - press the bridge link button")
            continue
    print("Hue lamp connected -- now state : ", phue_lamp.get_light(1, 'on'))
    bool_lamp_state = phue_lamp.get_light(1, 'on')

    while True:
        t_lock.acquire()
        temp_dict = copy.deepcopy(union_data_dict)
        t_lock.release()
        

