# syntax=docker/dockerfile:1.4
FROM python:3.10-alpine AS builder
EXPOSE 8000
WORKDIR /app 
COPY Pipfile /app
COPY Pipfile.lock /app
RUN pip3 install pipenv
RUN pipenv install
COPY . /app 
ENTRYPOINT ["pipenv"] 
CMD ["run", "python3", "manage.py", "runserver", "0.0.0.0:8000"]
