FROM python:3.9-alpine as base
COPY ./Docker/requirements.txt /requirements.txt
RUN pip install --user -r /requirements.txt

FROM base
COPY ./Docker/main.py /run/main.py
ENV qb_host="http://192.168.100.1" \
    qb_port=8080 \
    qb_account=admin \
    qb_password=adminadmin \
    aria2_url="https://192.168.100.1" \
    aria2_rpc_port=6800
RUN echo "python /run/main.py" >> /run/run.sh
RUN "Asia/Shanghai" > /etc/timezone
CMD ["/bin/sh","/run/run.sh"]