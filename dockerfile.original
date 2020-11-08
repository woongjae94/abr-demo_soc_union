FROM woongjae94/py36gpu:base
MAINTAINER <WoongJae> <skydnd0304@gmail.com>

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get install nano && \
	pip install scipy \
        phue \
        pyautogui \
        pySerial \
        selenium \
        python-xlib

RUN apt-get install -y wget unzip zip python3-tk python3-dev

ADD https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb .
RUN apt install -y ./google-chrome-stable_current_amd64.deb

#ADD http://chromedriver.storage.googleapis.com/86.0.4240.22/chromedriver_linux64.zip .
#RUN unzip chromedriver_linux64.zip

COPY chromedriver /chromedriver/

ADD http://cdn.naver.com/naver/NanumFont/fontfiles/NanumFont_TTF_ALL.zip /usr/share/fonts/nanumfont/
WORKDIR /usr/share/fonts/nanumfont/
RUN unzip NanumFont_TTF_ALL.zip
RUN fc-cache -f -v

WORKDIR /home
