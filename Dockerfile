FROM python:3.9.16-slim-buster
#
RUN apt-get update
#
WORKDIR /Synopsis/bin
#
COPY ./requirements.txt /Synopsis/bin/requirements.txt
RUN pip install -r requirements.txt
#
COPY . /Synopsis/bin
#
ENTRYPOINT ["python3", "-Bu", "-m", "synopsis"]
