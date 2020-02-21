#!/bin/bash
# This script removes a symlink to '/dev/arduino' so that there is always a fixed way to find the Arduino devices
# connected to this computer.
#
# $1 : [OPTIONAL] path of the link to be removed to the device set up by kernel/udev
#
# This script logs into syslog.
#
# ricardo@karbontek.co.jp

logger -t "[info, $0]" "Starting execution"

link='/dev/arduino'

[[ $# -eq 1 ]] && {
  logger -t "[info, $0]" "Using <$1> instead of <$link>"
  link="$1"
}

[[ -L "$link" ]] && {
  rm -f "$link"
  logger -t "[info, $0]" "<$link> removed"
}

exit 0
