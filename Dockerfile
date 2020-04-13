FROM python:3.6-alpine

WORKDIR /app
COPY . /app
CMD ["/app/shrinkeventfile"]
