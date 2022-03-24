FROM python:3.10.1-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apk update \
    && apk add --virtual .build-deps gcc python3-dev musl-dev \
    && apk add --no-cache mariadb-dev

COPY ./requirements.txt .
RUN pip install -r requirements.txt

RUN apk del .build-deps

COPY . .

# run as non-root user
RUN adduser -D django
USER django

CMD [ "/bin/sh" ]
