FROM --platform=linux/amd64 python:3.12-alpine

ENV PYTHONUNBUFFERED True

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . ./

EXPOSE 5000