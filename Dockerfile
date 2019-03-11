FROM zammad/zammad-docker-compose:zammad

ENV ZAMMAD_DIR /home/zammad

RUN apt-get update -qq && apt-get install -y python3

WORKDIR /smtp
ADD server.py /smtp/

CMD ["python3", "server.py"]
