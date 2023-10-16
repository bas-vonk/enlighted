FROM python:3.11.6-bookworm

COPY . /www
WORKDIR /www

# Install the package
RUN pip install -e .

# Set the timezone
RUN apt-get update && apt-get install -y tzdata
ENV TZ=Europe/Amsterdam
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
