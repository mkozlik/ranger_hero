FROM ros:jazzy

ARG ROS2_DISTRO=jazzy
ARG HOME=/root

RUN apt-get update && apt-get install -y \
    ros-jazzy-ros-base \
    python3-colcon-common-extensions \
    python3-vcstool \
    python3-pip \
    build-essential \
    git \
    x11-apps \
    ros-jazzy-rmw-cyclonedds-cpp \
    ros-jazzy-navigation2 \
    ros-jazzy-nav2-bringup \
    ros-jazzy-slam-toolbox \
    ros-jazzy-tf2-ros \
    ros-jazzy-rviz2 \
    ros-jazzy-moveit \
    ros-jazzy-usb-cam \
    ros-jazzy-tf2-geometry-msgs \
    ros-jazzy-tf-transformations \
    ros-jazzy-robot-localization \
    ros-jazzy-teleop-twist-* \
    ros-jazzy-mavros \
    ros-jazzy-plotjuggler-ros \
    ros-jazzy-rosbag2-storage-mcap \
    ros-jazzy-rqt* \
    ros-jazzy-nmea-msgs \
    ros-jazzy-mavros-msgs \
    ros-jazzy-rmw-cyclonedds-cpp \
    ros-jazzy-pcl-conversions \
    ros-jazzy-pcl-ros \
    apt-transport-https \
    cmake \
    libasio-dev \
    libtinyxml2-dev \
    libboost-all-dev \
    libpcl-dev \
    lsb-release \
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
    build-essential \
    cmake \
    libssl-dev \
    libasio-dev \
    libapr1-dev \
    libaprutil1-dev \
    libjsoncpp-dev \
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
#RUN cmake .. && make -j
#RUN sudo make install


WORKDIR /root
RUN git clone https://github.com/Livox-SDK/livox_ros_driver2.git ws_livox/src/livox_ros_driver2
COPY to_copy/MID360_config.json $HOME/ws_livox/src/livox_ros_driver2/config/MID360_config.json
WORKDIR /root/ws_livox
RUN /bin/bash -c "source /opt/ros/jazzy/setup.bash; ./src/livox_ros_driver2/build.sh humble"


# Set up a workspace
WORKDIR /root/ranger_ws/src
RUN git clone https://github.com/westonrobot/ugv_sdk.git
RUN git clone https://github.com/agilexrobotics/ranger_ros2.git
RUN git clone --branch jazzy https://github.com/ros-perception/pointcloud_to_laserscan.git


RUN apt-get update && apt-get install -y \
    ros-jazzy-librealsense2* \
    ros-jazzy-realsense2-* \
    ros-jazzy-example-interfaces \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /root/kinova_ws/src
RUN git clone --branch jazzy https://github.com/Kinovarobotics/ros2_kortex.git
WORKDIR /root/kinova_ws/
RUN vcs import src --skip-existing --input src/ros2_kortex/ros2_kortex.$ROS_DISTRO.repos
RUN vcs import src --skip-existing --input src/ros2_kortex/ros2_kortex-not-released.$ROS_DISTRO.repos



#RUN rosdep install --ignore-src --from-paths src -y -r

# Go to workspace and build it
WORKDIR /root/ranger_ws/
RUN /bin/bash -c "source /opt/ros/jazzy/setup.bash; colcon build --symlink-install"
WORKDIR /root/kinova_ws/
#RUN /bin/bash -c "source /opt/ros/jazzy/setup.bash; source install/setup.bash; colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release --packages-select kortex_bringup kortex_description kortex_driver"

RUN echo 'export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp' >> /root/.bashrc
RUN echo 'source /root/ranger_ws/install/setup.bash' >> /root/.bashrc
RUN echo 'source /opt/ros/jazzy/setup.bash' >> /root/.bashrc
RUN echo 'source /root/ws_livox/install/setup.bash' >> /root/.bashrc
#RUN echo 'source /root/kinova_ws/install/setup.bash' >> /root/.bashrc

COPY to_copy/tmux $HOME/.tmux.conf


#RUN bash /root/ranger_ws/src/ranger_ros2/ranger_bringup/scripts/setup_can2usb.bash

WORKDIR /root/ranger_hero/startup

CMD ["bash"]
