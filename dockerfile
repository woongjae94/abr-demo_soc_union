FROM woongjae94/abr-demo:socket
MAINTAINER <WoongJae> <skydnd0304@gmail.com>

ENV DEBIAN_FRONTEND=noninteractive

RUN pip install pytz

WORKDIR /home
