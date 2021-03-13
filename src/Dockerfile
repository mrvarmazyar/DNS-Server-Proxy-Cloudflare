FROM python:2.7.18-alpine

RUN apk add openssl

WORKDIR /dns

COPY app.py .

EXPOSE 53/udp

CMD ["python","app.py"]
