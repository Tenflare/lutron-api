FROM ubuntu
RUN apt-get update && apt-get -y install python python-pip
ADD . /opt/lutron
WORKDIR /opt/lutron
RUN pip install -r requirements.txt
EXPOSE 5000
CMD python main.py