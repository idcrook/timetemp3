#!/bin/bash
#!/bin/bash -x

# wrapper script to install systemd user unit(s)

SCRIPT_DIR=$( cd  $(dirname "${BASH_SOURCE:=$0}") && pwd)

clone_dir=$(dirname $SCRIPT_DIR)

if [[ -d "${clone_dir}" ]] ; then
    echo Using clone "${clone_dir}"
else
    echo Missing directory "${clone_dir}"
    exit 1
fi

cd "${clone_dir}"/

# refer to https://www.freedesktop.org/software/systemd/man/systemd.unit.html#User%20Unit%20Search%20Path
# - Canonical directory requires root access: pkg-config systemd --variable=systemduserunitdir
# - the following variable only requires user access
MY_SYSTEMD_USER_UNIT_DIR=/home/pi/.config/systemd/user/
mkdir -p "${MY_SYSTEMD_USER_UNIT_DIR}"
cp -av "${clone_dir}"/etc/timetemp_7segment_clock.service  "${MY_SYSTEMD_USER_UNIT_DIR}"
cp -av "${clone_dir}"/etc/timetemp_weather_logging.service "${MY_SYSTEMD_USER_UNIT_DIR}"

systemctl  --user list-unit-files | grep timetemp
# next command needed even though listed in previous output
systemctl  --user daemon-reload

systemctl  --user start  timetemp_7segment_clock
systemctl  --user status timetemp_7segment_clock | cat
echo " journalctl --user-unit   timetemp_7segment_clock.service"

systemctl  --user start  timetemp_weather_logging
systemctl  --user status timetemp_weather_logging | cat
echo " journalctl --user-unit   timetemp_weather_logging.service"

# Automatically start
systemctl --user enable  timetemp_7segment_clock
systemctl --user enable  timetemp_weather_logging

echo ""
echo "Run to allow user services to run when not logged on"
echo ""
echo " sudo loginctl enable-linger pi"
echo " sudo loginctl user-status pi"
echo ""
