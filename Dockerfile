FROM python:3.9.16-slim-buster
#
RUN apt-get update
#
WORKDIR /Synopsis/bin
COPY . /Synopsis/bin
#
RUN pip install -r requirements.txt
#
ENTRYPOINT ["python3", "-Bu", "-m", "synopsis"]
