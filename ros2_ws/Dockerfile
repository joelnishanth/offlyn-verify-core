FROM ros:jazzy-ros-base

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-pytest \
    ros-jazzy-gazebo-ros-pkgs \
    ros-jazzy-robot-state-publisher \
    ros-jazzy-joint-state-publisher \
    ros-jazzy-rviz2 \
    ros-jazzy-tf2-ros \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages pydantic>=2.0 pyyaml

WORKDIR /ros2_ws

COPY src/ src/
COPY ../prototype/ /prototype/

RUN . /opt/ros/jazzy/setup.sh && \
    colcon build --symlink-install

COPY ros_entrypoint.sh /ros_entrypoint.sh
RUN chmod +x /ros_entrypoint.sh

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
