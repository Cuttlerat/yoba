FROM python:3.6
RUN apt-get update 
RUN apt-get install -y vim inotify-tools tmux tzdata
RUN cp /usr/share/zoneinfo/Europe/Moscow /etc/localtime
COPY ./requirements /pybot/requirements
WORKDIR /pybot
RUN pip3.6 install -r requirements
ENTRYPOINT ["tmux"]
