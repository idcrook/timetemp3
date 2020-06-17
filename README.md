timetemp3
=========

Monitor and display time/temp with RasPi and log to cloud

Install
-------

Install pre-reqs and dependencies

```shell
# python and build system dependencies
sudo apt install -y git build-essential python3-setuptools python3-dev \
    python3-pip python3-venv python3-wheel

# for extra systemd functionality (not yet implemented)
sudo apt install python3-systemd

# additional system dependencies for Adafruit-LED-Backpack
sudo apt install python3-smbus python3-pil

# work-around for missing geojson dependency in current pyowm development
pip3 install --user geojson
```

now for the fun part

```shell
mkdir ~/projects
cd ~/projects
git clone https://github.com/idcrook/timetemp3.git
cd timetemp3

# perform the python setup, which also includes dependencies
pip3 install .
# for development, use instead # pip3 install -e .
```

Run
---

The i2c addresses in the scripts and config files may need to be updated for your hardware.

```shell
cd ~/projects/timetemp3
cp conf/weather_logging_config.example.json conf/weather_logging_config.json
# edit conf/weather_logging_config.json
touch conf/phant-config.json
# replace conf/phant-config.json with a phant data source config file
```

Assuming your system is setup to include `~/.local/bin` in `$PATH`, can run the `timetemp_*` wrapper scripts the Python `setup.py` installed

```shell
cd ~/projects/timetemp3

timetemp_7segment_clock
# <Ctrl-C> to exit

timetemp_weather_logging conf/weather_logging_config.json conf/phant-config.json
# <Ctrl-C> to exit
```

Run as systemd service
----------------------

On my Raspberry Pi OS system, `groups` includes "`gpio i2c`" so these services do not need to run as root user.

Install user unit file. Assumes git clone at `/home/pi/projects/timetemp3/` and has been installed

```shell
# refer to https://www.freedesktop.org/software/systemd/man/systemd.unit.html#User%20Unit%20Search%20Path
MY_SYSTEMD_USER_UNIT_DIR=/home/pi/.config/systemd/user/
mkdir -p "${MY_SYSTEMD_USER_UNIT_DIR}"
cd /home/pi/projects/timetemp3/
cp -av etc/timetemp_7segment_clock.service "${MY_SYSTEMD_USER_UNIT_DIR}"
cp -av etc/timetemp_weather_logging.service "${MY_SYSTEMD_USER_UNIT_DIR}"

# activate
systemctl --user list-unit-files | grep timetemp
# next command needed even though it is listed in previous output
systemctl --user daemon-reload

systemctl --user start timetemp_7segment_clock
systemctl --user status timetemp_7segment_clock
journalctl --user-unit timetemp_7segment_clock.service

systemctl --user start timetemp_weather_logging
systemctl --user status timetemp_weather_logging
journalctl --user-unit timetemp_weather_logging.service

# Automatically start
systemctl --user enable timetemp_7segment_clock
systemctl --user enable timetemp_weather_logging

# Run on system startup
sudo loginctl enable-linger pi
sudo loginctl user-status pi
```

TODO
====

See [TODO.org](TODO.org)
