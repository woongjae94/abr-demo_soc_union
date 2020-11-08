FROM woongjae94/abr-demo:socket
MAINTAINER <WoongJae> <skydnd0304@gmail.com>

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get install sshpass

WORKDIR /home
