FROM python:3

WORKDIR /ship_discovery_agent

COPY requirements.txt /ship_discovery_agent
COPY config/config.ini /ship_discovery_agent
COPY . .

RUN pip3 install -r requirements.txt
RUN mkdir -p /root/.ssh
RUN chmod 0700 /root/.ssh
RUN ssh-keyscan example.com > /root/.ssh/known_hosts

ENV REPEAT_TIMER 10
ENV CONF_FILE '/ship_discovery_agent/config/config.ini'
ENV CONTROLLER_URL 'http://127.0.0.1:5000/upload'

CMD [ "sh", "init.sh" ]
