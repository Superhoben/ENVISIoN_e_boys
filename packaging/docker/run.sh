# How to run the envision docker container.
xhost +local:docker
sudo docker run -it --rm \
    --name envision \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
    envision envision-inviwo