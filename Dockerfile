FROM ubuntu
RUN apt-get update && apt-get install python
ADD . /opt/shades
WORKDIR /opt/shades
RUN pip install -r requirements.txt
EXPOSE 5000
CMD python main.py