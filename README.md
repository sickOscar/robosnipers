# Robolaser (name TBD)

## Development

To start developing this app you need python3 and docker installed. I suggest to use a Linux machine, many of the things here have never been tested on Windows (and maybe never will).

First of all, you need an MQTT broker running to run the application.

To start the MQTT broker, from project root directory launch
```
docker-compose up
```

### Brain

To start developing what we called brain (server + simulation):
```
cd brain
then create and setup the virtual env with:
```
virtualenv venv
pip3 install -r requirements.txt
```

> NOTE: if you don't have virtualenv installed, you can install it with
```
pip3 install virtualenv
```

to start the application, run
```
python3 main.py
```
This script supports the following command line arguments:
- -h, --help prints the help
- --debug shows a window with pygame running to check if the world is rendering correctly 

### Web view

To run both the web view and the map editor, you need to run a web server on the ```assets``` folder. There are many ways to do that, maybe the easiest one is the following python one-liner.
```
cd assets
python -m SimpleHTTPServer
```
or (for python3)
```
python3 -m http.server
```

At ```http://localhost:8000``` you'll find the simulator front end running


#### Map editor
Assuming you used the previous command to launch the web server, you can find the map editor at
```http://localhost:8000/map_editor/editor.html```