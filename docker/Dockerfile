FROM ros:humble

ARG ROS2_DISTRO=humble
ARG HOME=/root

RUN apt-get update && apt-get install -y \
    ros-humble-ros-base \
    python3-colcon-common-extensions \
    python3-vcstool \
    python3-pip \
    build-essential \
    git \
    x11-apps \
    ros-humble-rmw-cyclonedds-cpp \
    ros-humble-navigation2 \
    ros-humble-nav2-bringup \
    ros-humble-slam-toolbox \
    ros-humble-tf2-ros \
    ros-humble-rviz2 \
    ros-humble-moveit \
    ros-humble-usb-cam \
    ros-humble-tf2-geometry-msgs \
    ros-humble-tf-transformations \
    ros-humble-robot-localization \
    ros-humble-teleop-twist-* \
    ros-humble-mavros \
    ros-humble-plotjuggler-ros \
    ros-humble-rosbag2-storage-mcap \
    ros-humble-rqt* \
    ros-humble-nmea-msgs \
    ros-humble-mavros-msgs \
    ros-humble-rmw-cyclonedds-cpp \
    ros-humble-kortex-bringup \
    ros-humble-kinova-gen3-6dof-robotiq-2f-85-moveit-config \
    ros-humble-pcl-conversions \
    apt-transport-https \
    cmake \
    libasio-dev \
    libtinyxml2-dev \
    libboost-all-dev \
    libpcl-dev \
    lsb-release \
    ignition-fortress \
    gnupg \
    nano \
    vim \
    can-utils \
    usbutils \
    iproute2 \
    net-tools \
    tmux \
    kmod \
    tmuxinator \
    inetutils-ping \
    && rm -rf /var/lib/apt/lists/*


# Setup timezone (fix interactive package installation)
RUN ln -snf /usr/share/zoneinfo/${TZ} /etc/localtime && echo ${TZ} > /etc/timezone
#RUN ip link set can0 up type can bitrate 500000

# Agent forwarding during docker build https://stackoverflow.com/questions/43418188/ssh-agent-forwarding-during-docker-build
# install ssh client and git
RUN sudo apt-get install openssh-client git

ENV DOCKER_BUILDKIT=1
RUN apt-get install -y openssh-client
ENV GIT_SSH_COMMAND="ssh -v" 
USER root

RUN --mount=type=ssh id=default \
    mkdir -p -m 0600 ~/.ssh/ && \
    ssh-keyscan github.com >> ~/.ssh/known_hosts


RUN apt-get update

# Livox SDK
WORKDIR /root
RUN git clone https://github.com/Livox-SDK/Livox-SDK2.git
WORKDIR /root/Livox-SDK2
RUN mkdir build
WORKDIR /root/Livox-SDK2/build
RUN cmake .. && make -j
RUN sudo make install


WORKDIR /root
RUN git clone https://github.com/Livox-SDK/livox_ros_driver2.git ws_livox/src/livox_ros_driver2
COPY to_copy/MID360_config.json $HOME/ws_livox/src/livox_ros_driver2/config/MID360_config.json
WORKDIR /root/ws_livox
RUN /bin/bash -c "source /opt/ros/humble/setup.bash; ./src/livox_ros_driver2/build.sh humble"


# Set up a workspace
WORKDIR /root/ranger_ws/src
RUN git clone https://github.com/westonrobot/ugv_sdk.git
RUN git clone https://github.com/agilexrobotics/ranger_ros2.git
RUN git clone --branch humble https://github.com/ros-perception/pointcloud_to_laserscan.git

RUN git clone --branch humble --single-branch https://github.com/Kinovarobotics/ros2_kortex.git
WORKDIR /root/ranger_ws/src/ros2_kortex
RUN git sparse-checkout init --cone && git sparse-checkout set kortex_moveit_config/kinova_gen3_lite_moveit_config


#RUN rosdep install --ignore-src --from-paths src -y -r

# Go to workspace and build it
WORKDIR /root/ranger_ws/
RUN /bin/bash -c "source /opt/ros/humble/setup.bash; colcon build --symlink-install"

RUN echo 'export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp' >> /root/.bashrc
RUN echo 'source /root/ranger_ws/install/setup.bash' >> /root/.bashrc
RUN echo 'source /opt/ros/humble/setup.bash' >> /root/.bashrc
RUN echo 'source /root/ws_livox/install/setup.bash' >> /root/.bashrc

COPY to_copy/tmux $HOME/.tmux.conf


#RUN bash /root/ranger_ws/src/ranger_ros2/ranger_bringup/scripts/setup_can2usb.bash

WORKDIR /root/ranger_hero/startup

CMD ["bash"]
