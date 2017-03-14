FROM python:3.6-alpine
RUN apk add --update bash && rm -rf /var/cache/apk/*
RUN mkdir -p /tester/scripts
WORKDIR /tester
COPY client.py scripts/client.py
COPY requirements.txt scripts/requirements.txt
RUN pip install -r scripts/requirements.txt
COPY run_task.sh run_task
RUN chmod +x run_task
RUN ln -s /tester/run_task /usr/local/bin/
CMD ["/bin/bash"]