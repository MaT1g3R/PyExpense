FROM python:latest
MAINTAINER MaT1g3R

ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y swig libssl-dev dpkg-dev netcat

RUN mkdir /code
WORKDIR /code
COPY . /code/

RUN pip install -U pip
RUN pip install -Ur requirements.txt

CMD ["/code/run.sh"]
