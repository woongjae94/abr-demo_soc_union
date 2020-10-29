sudo docker run -v ~/Desktop/abr-demo_soc_union:/home -it --rm --name Socket_container -p 3019:8282 woongjae94/abr-demo:socket python3 main_soc_server_and_control.py
