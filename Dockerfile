FROM zammad/zammad-docker-compose:zammad

ENV ZAMMAD_DIR /home/zammad

RUN apt-get update -qq && apt-get install -y python3

WORKDIR /get-mai
ADD server.py /get-mail

CMD ["python3", "server.py"]
