from python:3.10

WORKDIR /usr/src/app

COPY .env .env
COPY requirements.txt requirements.txt

COPY oopo.py oopo.py

COPY email_cog.py email_cog.py
COPY reaction_cog.py reaction_cog.py
COPY message_cog.py message_cog.py

RUN pip3 install -r requirements.txt

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.9.0/wait /wait
RUN chmod +x /wait

CMD /wait && python oopo.py
