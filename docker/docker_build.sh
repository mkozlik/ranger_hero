#!/bin/bash

DOCKERFILE=Dockerfile
IMAGE_NAME=ranger_hero

distro="humble"
build_args=""
for (( i=1; i<=$#; i++));
do
  param="${!i}"
  echo $param

  if [ "$param" == "--distro" ]; then
    j=$((i+1))
    distro="${!j}"
  fi

  if [ "$param" == "--dockerfile" ]; then
    j=$((i+1))
    DOCKERFILE="${!j}"
  fi

  if [ "$param" == "--image-name" ]; then
    j=$((i+1))
    IMAGE_NAME="${!j}"
  fi

  if [ "$param" == "--build-args" ]; then
    j=$((i+1))
    build_args="${!j}"
  fi

done

echo "Building $IMAGE_NAME image for $distro with additional docker arguments $build_args."
echo "Dockerfile: $DOCKERFILE"

# export BUILDKIT_PROGRESS=plain
export DOCKER_BUILDKIT=1
docker build \
    $build_args \
    --build-arg ROS_HOSTNAME=$ROS_HOSTNAME \
    --build-arg ROS_MASTER_URI=$ROS_MASTER_URI \
    --build-arg ROS_IP=$ROS_IP \
    -f $DOCKERFILE \
    --ssh default \
    -t $IMAGE_NAME:$distro .
