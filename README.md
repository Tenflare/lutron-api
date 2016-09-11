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
    sudo docker run -d --restart=always -e LUTRON_HOST=<IP OF BRIDGE> --name shades-api --net=host shades-api

## Usage

### Macros


Open the shades

    curl -X POST 127.0.0.1:5000/shades/open

Close the shades

    curl -X POST 127.0.0.1:5000/shades/close

Set the shades at 50%

    curl -X POST 127.0.0.1:5000/shades/50


### Device Command Examples

```
Start Lowering a Device Group


/api/device/6/6/3 - Equivalent to #DEVICE,6,6,3

Stop Lowering a Device Group

/api/device/6/6/4 - Equivalent to #DEVICE,6,6,4

Start Raising a Device Group

#DEVICE,6,5,3
/api/device/6/5/3

Stop Lowering a Device Group

#DEVICE,6,5,4
/api/device/6/5/4

```


## Smarthings Integration

Once you have your API up and running, integrating with other hubs is super simple.  

Checkout [https://github.com/kecorbin/smartthings](https://github.com/kecorbin/smartthings) for a sample using Samsung Smartthings

## Home Assistant Integration

This can also be used to integrate Lutron into Home Assistant, using the shades example from above, the following can be
specified in your configuration.yaml file for HASS.


    - platform: command_line
      rollershutters:
        Living Room Rollershutter:
          upcmd: curl -X POST http://192.168.10.25:5000/shades/open
          downcmd: curl -X POST http://192.168.10.25:5000/shades/close
          stopcmd: curl -X POST http://192.168.10.25:5000/shades/50

