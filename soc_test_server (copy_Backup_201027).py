import socket
import argparse
import threading
import time
import copy
import requests

# control
import phue_lamp
import control_web

client_list = {}
client_name = ['Gesture', 'Action', 'Headpose']
# Gesture list [ Swiping Up / Sliding Two Fingers Up / Swiping Left / Thumb Up / Sliding Two Fingers Right / Stop Sign
#                Sliding Two Fingers Left / Sliding Two Fingers Down / Rolling Hand Backward / Doing other things
#                Swiping Right / Swiping Down / Thumb Down ]
# Action list [ sitting / standing / drinking / brushing / playing instrument / speaking
#               waving a hand / working / coming / leaving / talking on the phone
#               stretching / nodding off / reading / blow nose ]
# Head pose list { ~left : lamp , center : pc , right~ : ai speaker }
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
    device_lamp = phue_lamp.Phue(Hue_ip)

    #
    #device_pc = control_web.Web_control()

    mills = lambda: int(round(time.time() * 1000))
    prev_time = mills()

    while True:
        t_lock.acquire()
        temp_dict = copy.deepcopy(union_data_dict)
        t_lock.release()

        now_time = mills()

        if (now_time - prev_time) > 500:
            requests.get('http://192.168.0.21:3001/api/v1/actions/action/{}/{}_{}_{}_{}_{}' \
                .format('home', 'Mode: None', temp_dict['Gesture'], temp_dict['Action'], temp_dict['Headpose'] + 'Device_name', 'controlA'))

        


        
        

