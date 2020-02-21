#!/bin/bash
# This script creates a symlink to '/dev/arduino' so that there is always a fixed way to find the Arduino devices
# connected to this computer.
#
# $1 : [OPTIONAL] path of the link to be created to the device set up by kernel/udev
#
# This script logs into syslog.
#
# ricardo@karbontek.co.jp

logger -t "[info, $0]" "Starting execution"

dev="$DEVNAME"
link='/dev/arduino'

[[ $# -eq 1 ]] && {
  logger -t "[info, $0]" "Using <$1> instead of <$link>"
  link="$1"
}

[[ -L "$link" ]] && {
  [[ -a "$link" ]] && {
    logger -t "[warning, $0]" "<$link> exists and it is NOT broken, skipping."
    exit 0
  } || {
    logger -t "[warning, $0]" "<$link> exists but it is broken, removing and creating a new one."
    rm -f "$link"
  }
}

ln -sf "$dev" "$link"
logger -t "[info, $0]" "Link created from <$dev> to <$link>"
