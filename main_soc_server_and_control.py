import socket
import argparse
import threading
#import multiprocessing
import time
import copy
import requests
from pytz import timezone
from datetime import datetime

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
#print(union_data_dict)

t_lock = threading.Lock()
#t_lock = multiprocessing.Lock()

today = datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d')
time_now = lambda: datetime.now(timezone('Asia/Seoul')).strftime('%H:%M:%S')
mills = lambda: int(round(time.time() * 1000))
tester_name = ""

# def auto_save(today, tester_name):
#     command = "sshpass -p \"dpdlqldkf\" scp -o StrictHostKeyChecking=no -P 8222 /home/" \
#         + today + "_" + tester_name + ".txt" + " abr@155.230.14.96:~/Desktop/log_test/"
#     with open("./save_log.sh", 'w') as f:
#         f.write(command)
#     run_save = subprocess.Popen(["sh", ".save_log.sh"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)


def add_log(msg):
    cur_time = time_now()
    with open('./log_test/' + today + "_" + tester_name + ".txt", "a") as f:
        f.write(today + ' | '+ cur_time + ' | (mode:{}) | (gesture:{}) | (action:{}) | (headpose:{}) | (device:{})\n'.format( \
            msg[0], msg[1], msg[2], msg[3], msg[4]))

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 0))
    return s.getsockname()[0]

def receive_handler(client_socket, addr, client):
    print(" --- {} container is connected".format(client))
    try:
        while True:
            data = client_socket.recv(512).decode('utf-8')
            t_lock.acquire()
            union_data_dict[client] = data
            t_lock.release()
    except:
        print("client socket [" + client + "] is forcibly terminated")
        t_lock.acquire()
        union_data_dict[client] = "Close$Close$Close$"
        t_lock.release()
    finally:
        client_socket.close()
        t_lock.acquire()
        global client_list
        del client_list[client]
        t_lock.release()
        print(client + "socket closed")

def accept_func(server_socket, host, port, num_of_client):
    print("Waiting for client socket")
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

        #receive_thread = multiprocessing.Process(target=receive_handler, args=(client_socket, addr, client))
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
    

    # wait connect request from client
    print("#### server socket start...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((server_ip, port))

    print("#### server socket start listening")
    server_socket.listen(num_of_client)

    accept_func(server_socket, server_ip, port, num_of_client)
    print("#### All clients are connected")

    # connect phue
    wait_for_phue_connect=input("press phue link button and then press enter : ")
    device_lamp = phue_lamp.Phue(Hue_ip)
    print(device_lamp.get_light_state())
    if device_lamp.get_light_state():
        device_lamp.power_switch(False)

    #
    device_pc = control_web.Web()
    #
    device_ppt = control_web.Ppt()

    while True:
        pre_gesture = "None"
        pre_action = "None"
        pre_head = "None"
        reset_time = 0
        prev_time = mills()
        pre_gesture = 'None'
        if_pre_reading = False
        try:
            #tester_name = input("please enter tester's name(ENG) : ")
            while True:
                t_lock.acquire()
                temp_dict = copy.deepcopy(union_data_dict)
                t_lock.release()

                now_time = mills()

                if (now_time - prev_time) > 500:
                    #print(temp_dict)
                    try:
                        gesture_msg = temp_dict['Gesture'].split("$")[-2]
                        # if gesture_msg == "Close":
                        #     accept_func(server_socket, server_ip, port, num_of_client)
                    except:
                        gesture_msg = "None"

                    try:
                        action_msg = temp_dict['Action'].split("$")[-2]
                        # if action_msg == "Close":
                        #     accept_func(server_socket, server_ip, port, num_of_client)
                    except:
                        action_msg = "None"

                    try:
                        head_msg = temp_dict['Headpose'].split("$")[-2]
                        # if head_msg == "Close":
                        #     accept_func(server_socket, server_ip, port, num_of_client)
                    except:
                        head_msg = "None"

                    try:
                        requests.get('http://192.168.0.22:3001/api/v1/actions/action/{}/Mode:{}_Gesture:{}_Action:{}_Head:{}_Device:{}'.format( \
                            'home', control_mode, gesture_msg, action_msg, head_msg, device))
                        print('Mode: ', control_mode, ' |Gesture: ',gesture_msg,' |Action: ', action_msg,' |Head: ', head_msg, ' |Device: ', device)

                        if (pre_gesture != gesture_msg) or (pre_action != action_msg) or (pre_head != head_msg):
                            if gesture_msg == action_msg == head_msg == "None":
                                pass
                            else:
                                add_log([control_mode, gesture_msg, action_msg, head_msg, device])

                    except:
                        print("http connect unstable... ")
                        print(gesture_msg, action_msg, head_msg)
                    prev_time = now_time

                    if gesture_msg == "Close" or action_msg == "Close" or head_msg == "Close":
                        accept_func(server_socket, server_ip, port, num_of_client)


        # Gesture list [ Swiping Up / Sliding Two Fingers Up / Swiping Left / Thumb Up / Sliding Two Fingers Right / Stop Sign
        #                Sliding Two Fingers Left / Sliding Two Fingers Down / Rolling Hand Backward / Doing other things
        #                Swiping Right / Swiping Down / Thumb Down ]
        # Action list [ sitting / standing / drinking / brushing / playing instrument / speaking
        #               waving a hand / working / coming / leaving / talking on the phone
        #               stretching / nodding off / reading / blow nose ]
        # device = [None lamp pc ppt]          
                    if control_mode == 'Action':

                        if action_msg == 'reading':
                            # light on
                            if not device_lamp.get_light_state():
                                device_lamp.power_switch(True)
                            device_lamp.bri_value = 254
                            device_lamp.change_bri()
                            device_lamp.change_color_rgb([0.9, 0.7, 0.2])
                            control_mode = 'Gesture'
                            device = 'lamp'
                            if_pre_reading = True

                        elif action_msg == 'stretching':
                            if if_pre_reading:
                                if device_lamp.get_light_state():
                                    device_lamp.power_switch(False)
                                control_mode = 'Action'
                                device = 'None'
                                if_pre_reading = False
                        
                        else:
                            #
                            pass    


                        if gesture_msg == 'Thumb Up':
                            control_mode = 'Gesture'
                            if head_msg =='FarLeft' or head_msg == 'Left':
                                device = 'lamp'
                            elif head_msg == 'Center':
                                device = 'pc'
                            elif head_msg == 'FarRight' or head_msg == 'Right':
                                device = 'pc'
                            else:
                                device = 'None'
                                control_mode = 'Action'

                    elif control_mode == 'Gesture':
                        
                        if action_msg == 'stretching':
                            if if_pre_reading:
                                if device_lamp.get_light_state():
                                    device_lamp.power_switch(False)
                                control_mode = 'Action'
                                device = 'None'
                                if_pre_reading = False


                        if gesture_msg == 'Thumb Down':

                            control_mode = 'Action'
                            device = 'None'
                            continue

                        if device == 'lamp':
                            device_lamp.control_lamp(pre_gesture, gesture_msg)
                            print("lamp")

                        elif device == 'pc':
                            device_pc.control_pc(pre_gesture, gesture_msg, head_msg)
                            print("pc")

                        elif device == 'ppt':
                            device_ppt.control_ppt(pre_gesture, gesture_msg)
                            print("ppt")

                        else:
                            print("there is no selected device")
                            control_mode = 'Action'
                    
                    else:
                        control_mode = 'Action'
                        device = 'None'
                    
                    pre_gesture = gesture_msg
                    pre_action = action_msg
                    pre_head = head_msg

                    reset_time += 1
                    if reset_time > 5:
                        t_lock.acquire()
                        union_data_dict['Gesture'] = 'None$None$None$'
                        union_data_dict['Action'] = 'None$None$None$'
                        union_data_dict['Headpose'] = 'None$None$None$'
                        t_lock.release()
                        reset_time = 0
        
        except KeyboardInterrupt:
            print("saving log file...")
            # auto_save(today, tester_name)
            print("save complete")
            while True:
                choice = input("q : quit\nr : restart\nq or r :")
                if choice == 'q':
                    break
                elif choice == 'r':
                    break
                else:
                    continue
            if choice == 'q':
                break
            else:
                continue
                




