Lutron REST API
=============

This is simple Flask based API for interacting with Lutron Caseta

This was originally written specifically for controlling Lutron Shades, but can easily
be modified to work with any Lutron Device.


## Installing

After downloading, install using setuptools.

    pip install -r requirements.txt
    python main.py

## Docker


The latest build of this project is also available as a Docker image from Docker Hub

    docker pull kecorbin/lutron-shades-api
    sudo docker run -d --restart=always --name shades-api --net=host shades-api

