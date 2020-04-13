FROM python:3.6-alpine

RUN pip install flake8
WORKDIR /app
COPY . /app
CMD ["/app/shrinkeventfile"]
