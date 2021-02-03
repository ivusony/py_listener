FROM python:3

RUN mkdir /usr/src/listener

RUN mkdir /usr/src/listener/src

RUN mkdir /usr/src/listener/logs

WORKDIR /usr/src/listener

RUN python -m pip install pika && python -m pip install requests && python -m pip install pymongo

WORKDIR /usr/src/listener/src

EXPOSE 5050

COPY entrypoint.sh /usr/local/bin/

RUN chmod +x /usr/local/bin/entrypoint.sh

CMD ["entrypoint.sh"]
