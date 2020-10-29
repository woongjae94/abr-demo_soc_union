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
# Head pose list [ FarLeft / Left / Center / Right / FarRight ]
# Head pose list { ~left : lamp , center : pc , right~ : ppt }
union_data_dict = {x:'None$None$None$' for x in client_name}
print(union_data_dict)

t_lock = threading.Lock()

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 0))
    return s.getsockname()[0]

def receive_handler(client_socket, addr, client):
    print(" --- {} container is connected".format(client))
    while True:
        data = client_socket.recv(512).decode('utf-8')
        t_lock.acquire()
        union_data_dict[client] = data
        t_lock.release()
        time.sleep(0.2)
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
    device = 'None'
    #device = [None lamp pc ppt]
    control_mode = 'Action'
    #control_mode = [ Action Gesture ]
    control_param = 'None'

    # wait connect request from client
    accept_func(server_ip, port, num_of_client)
    print("#### All clients are connected")

    # connect phue
    wait_for_phue_connect=input("press phue link button and then press enter : ")
    device_lamp = phue_lamp.Phue(Hue_ip)
    print(device_lamp.get_light_state())

    #
    device_pc = control_web.Web()

    #
    device_ppt = control_web.Ppt()


    reset_time = 0

    mills = lambda: int(round(time.time() * 1000))
    prev_time = mills()

    pre_gesture = 'None'

    while True:
        t_lock.acquire()
        temp_dict = copy.deepcopy(union_data_dict)
        t_lock.release()

        now_time = mills()

        if (now_time - prev_time) > 500:
            #print(temp_dict)
            gesture_msg = temp_dict['Gesture'].split("$")[-2]
            action_msg = temp_dict['Action'].split("$")[-2]
            head_msg = temp_dict['Headpose'].split("$")[-2]
            try:
                requests.get('http://192.168.0.22:3001/api/v1/actions/action/{}/Mode:{}_Gesture:{}_Action:{}_Head:{}_Control:{}'.format('home', control_mode, gesture_msg, action_msg, head_msg + device, 'controlA'))
                print('Gesture: ',gesture_msg,' |Action: ', action_msg,' |Head: ', head_msg)
            except:
                print("http connect unstable... ")
                print(gesture_msg, action_msg, head_msg)
            prev_time = now_time

# Gesture list [ Swiping Up / Sliding Two Fingers Up / Swiping Left / Thumb Up / Sliding Two Fingers Right / Stop Sign
#                Sliding Two Fingers Left / Sliding Two Fingers Down / Rolling Hand Backward / Doing other things
#                Swiping Right / Swiping Down / Thumb Down ]
# device = [None lamp pc ppt]          
            if control_mode == 'Action':
                if gesture_msg == 'Thumb Up':
                    control_mode = 'Gesture'
                    if head_msg =='FarLeft' or head_msg == 'Left':
                        device = 'lamp'
                    elif head_msg == 'Center':
                        device = 'pc'
                    elif head_msg == 'FarRight' or head_msg == 'Right':
                        device = 'ppt'
                    else:
                        device = 'None'

            elif control_mode == 'Gesture':
                if gesture_msg == 'Thumb Down':
                    control_mode = 'Action'
                    device = 'None'
                    continue

                if device == 'lamp':
                    device_lamp = phue_lamp.Phue(Hue_ip)
                    device_lamp.control_lamp(pre_gesture, gesture_msg)

                elif device == 'pc':
                    device_pc = control_web.Web()
                    device_pc.control_pc(pre_gesture, gesture_msg, head_msg)
                    print("pc")

                elif device == 'ppt':
                    device_ppt = control_web.Ppt()
                    device_ppt.control_ppt(pre_gesture, gesture_msg)
                    print("ppt")

                else:
                    print("there is no selected device")
                    control_mode = 'Action'
            
            else:
                control_mode = 'Action'
                device = 'None'
            
            pre_gesture = gesture_msg

            reset_time += 1
            if reset_time > 5:
                t_lock.acquire()
                union_data_dict['Gesture'] = 'None$None$None$'
                union_data_dict['Action'] = 'None$None$None$'
                t_lock.release()
                reset_time = 0
            







        


        
        

