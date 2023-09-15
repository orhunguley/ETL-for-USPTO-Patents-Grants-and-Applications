# FROM python:3.11.3
FROM continuumio/miniconda3

RUN apt update
RUN apt install python3 -y
RUN apt-get install nano

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

COPY ./src /code/src

WORKDIR /code/src

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# CMD [ "python", "./data_ingestion.py"]