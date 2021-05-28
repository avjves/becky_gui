FROM python:3.8

#
ENV TZ=Europe/Helsinki
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Installing dependencies
RUN apt update
RUN apt install python3-pip npm -y

#
EXPOSE 6700
EXPOSE 6701

COPY . /becky
RUN cd /becky/backend
RUN python3 -m venv /becky/venv
RUN . /becky/venv/bin/activate && pip3 install --upgrade pip
RUN . /becky/venv/bin/activate && pip3 install -r /becky/backend/requirements.txt
RUN . /becky/venv/bin/activate && python3 /becky/backend/manage.py migrate
RUN cd /becky/frontend/becky-react && npm install
CMD . /becky/venv/bin/activate && exec bash /becky/run_docker.sh
