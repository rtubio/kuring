#!/bin/bash

source /etc/streamer.conf

/usr/local/bin/mlx90640 $FPS | gst-launch-1.0 fdsrc blocksize=2304 ! udpsink host=$HOST port=$PORT
