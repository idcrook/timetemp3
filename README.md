# timetemp3

Monitor and display time/temp with RasPi and log to cloud


## Install

```shell
sudo apt install -y git build-essential python3-setuptools python3-dev python3-pip python3-venv python3-wheel

# additional system dependencies for Adafruit-LED-Backpack
sudo apt install python3-smbus python3-pil

# work-around for missing geojson dependency
pip3 install --user geojson

# now for the fun part
pip3 install -e .
```
