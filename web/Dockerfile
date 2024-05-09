FROM python:3.8.13-buster
RUN echo \
   && apt-get update \
   && apt-get --yes install apt-file \
   && apt-file update
RUN echo \
   && apt-get --yes install build-essential
ARG USER=nobody
RUN usermod -aG sudo $USER
RUN pip3 install --upgrade pip
# 安装
COPY requirements.txt  /app/requirements.txt 
WORKDIR /app
RUN pip3 --no-cache-dir install -r requirements.txt
USER $USER

EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["main_server.py"]