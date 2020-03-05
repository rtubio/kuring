# Building library and installing it

    a) Install packages at raspbian.packages
    b) Clone repository from GitHub:
        git clone https://github.com/pimoroni/mlx90640-library
    c) Compile and install BCM library:
        make bcm2835
    d) @Makefile : uncomment I2C_LIBS line that includes the native BCM2835 library
        I2C_LIBS = -lbcm2835
    e) 
        make clean && make I2C_MODE=RPI all && sudo make install

# Streaming video from Raspberry PI

    sudo examples/rawrgb | gst-launch-1.0 fdsrc blocksize=2304 ! udpsink host=192.168.10.117 port=5000

# Receiving the video on the other end

    gst-launch-1.0 udpsrc blocksize=2304 port=5000 ! rawvideoparse use-sink-caps=false width=32 height=24 format=rgb framerate=16/1 ! videoconvert ! videoscale ! video/x-raw,width=640,height=480 ! autovideosink