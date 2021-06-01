FROM python:3.8

#
ENV TZ=Europe/Helsinki
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Installing dependencies
RUN apt update
RUN apt install python3-pip npm -y
RUN apt install nginx -y
RUN apt install s3cmd -y

#
EXPOSE 80

COPY ./nginx/default /etc/nginx/sites-enabled/default
COPY . /becky
RUN cd /becky/backend
RUN python3 -m venv /becky/venv
RUN . /becky/venv/bin/activate && pip3 install --upgrade pip
RUN . /becky/venv/bin/activate && pip3 install -r /becky/backend/requirements.txt
RUN . /becky/venv/bin/activate && python3 /becky/backend/manage.py migrate
RUN cd /becky/frontend/becky-react/src && bash paths_to_prod.sh
RUN cd /becky/frontend/becky-react && npm install npm@latest -g
RUN cd /becky/frontend/becky-react && npm install && npm run build
RUN cp -r /becky/frontend/becky-react/build/* /usr/share/nginx/html
CMD . /becky/venv/bin/activate && exec bash /becky/run_docker.sh
