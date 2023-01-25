FROM python:3.9

# Set the working directory
WORKDIR /app/src

COPY ["Pipfile", "Pipfile.lock", "./"]

#RUN apt-get update && apt-get install -y dnsutils && apt-get install -y traceroute && apt-get install -y iputils-ping
RUN pip install --upgrade pip
RUN pip install pipenv && \
    pipenv install --deploy --system --ignore-pipfile

COPY hwr_analyzer ./hwr_analyzer

ENV APP_ENV build

ADD docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

