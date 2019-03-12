FROM zammad/zammad-docker-compose:zammad-2.9.0-13

ENV ZAMMAD_DIR /opt/zammad

RUN apt-get update -qq && apt-get install -y python3

WORKDIR /opt/get-mail
ADD server.py /opt/get-mail/

ENTRYPOINT ["python3", "-u", "server.py"]
