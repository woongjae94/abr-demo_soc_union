FROM woongjae94/py36gpu:base
MAINTAINER <WoongJae> <skydnd0304@gmail.com>

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get install nano && \
	pip install scipy \
        phue \
        pyautogui \
        pySerial

WORKDIR /home
