# Copyright (c) 2024 PickNik, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import (
    DeclareLaunchArgument,
    OpaqueFunction,
    RegisterEventHandler,
)
from launch.event_handlers import OnProcessExit
from launch.conditions import IfCondition, UnlessCondition
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from moveit_configs_utils import MoveItConfigsBuilder
import yaml



def load_yaml(package_name, file_path):
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)
 
    try:
        with open(absolute_file_path, "r") as file:
            return yaml.safe_load(file)
    except EnvironmentError:  # parent of IOError, OSError *and* WindowsError where available
        return None

def launch_setup(context, *args, **kwargs):
    # Initialize Arguments
    robot_ip = LaunchConfiguration("robot_ip")
    use_fake_hardware = LaunchConfiguration("use_fake_hardware")
    gripper_max_velocity = LaunchConfiguration("gripper_max_velocity")
    gripper_max_force = LaunchConfiguration("gripper_max_force")
    launch_rviz = LaunchConfiguration("launch_rviz")
    use_sim_time = LaunchConfiguration("use_sim_time")

    launch_arguments = {
        "robot_ip": robot_ip,
        "use_fake_hardware": use_fake_hardware,
        "gripper": "gen3_lite_2f",
        "gripper_joint_name": "right_finger_bottom_joint",
        "dof": "6",
        "gripper_max_velocity": gripper_max_velocity,
        "gripper_max_force": gripper_max_force,
    }

    moveit_config = (
        MoveItConfigsBuilder(
            "gen3_lite_gen3_lite_2f", package_name="kinova_gen3_lite_moveit_config"
        )
        .robot_description(mappings=launch_arguments)
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .planning_scene_monitor(
            publish_robot_description=True, publish_robot_description_semantic=True
        )
        .planning_pipelines(pipelines=["ompl"])
        .to_moveit_configs()
    )

    moveit_config.moveit_cpp.update({"use_sim_time": use_sim_time.perform(context) == "true"})

    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
        ],
    )

    # Static TF
    static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="static_transform_publisher",
        output="log",
        arguments=["--frame-id", "world", "--child-frame-id", "base_link"],
    )

    # Publish TF
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="both",
        parameters=[
            moveit_config.robot_description,
        ],
    )

    # ros2_control using FakeSystem as hardware
    ros2_controllers_path = os.path.join(
        get_package_share_directory("kinova_gen3_lite_moveit_config"),
        "config",
        "ros2_controllers.yaml",
    )
    ros2_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[ros2_controllers_path],
        remappings=[
            ("/controller_manager/robot_description", "/robot_description"),
        ],
        output="both",
    )

    robot_traj_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_trajectory_controller", "-c", "/controller_manager"],
    )

    robot_pos_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["twist_controller", "--inactive", "-c", "/controller_manager"],
    )

    robot_hand_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["gen3_lite_2f_gripper_controller", "-c", "/controller_manager"],
    )

    fault_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["fault_controller", "-c", "/controller_manager"],
        condition=UnlessCondition(use_fake_hardware),
    )
    # rviz with moveit configuration
    rviz_config_file = (
        get_package_share_directory("kinova_gen3_lite_moveit_config") + "/config/moveit.rviz"
    )
    rviz_node = Node(
        package="rviz2",
        condition=IfCondition(launch_rviz),
        executable="rviz2",
        name="rviz2_moveit",
        output="log",
        arguments=["-d", rviz_config_file],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.planning_pipelines,
            moveit_config.joint_limits,
        ],
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager",
        ],
    )

    # Delay rviz start after `joint_state_broadcaster`
    delay_rviz_after_joint_state_broadcaster_spawner = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[rviz_node],
        ),
        condition=IfCondition(launch_rviz),
    )

    #servo_yaml = os.path.join(
    #    get_package_share_directory("kinova_gen3_lite_moveit_config") + "/config/servo_params.yaml"
    #)
    servo_yaml = load_yaml("kinova_gen3_lite_moveit_config", "config/servo_params.yaml")


    servo_params = {"moveit_servo": servo_yaml}

    servo_node = Node(
        package="moveit_servo",
        executable="servo_node",
        parameters=[
            #servo_yaml,
            #acceleration_filter_update_period,
            #planning_group_name,
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.joint_limits,
            {"moveit_servo.use_gazebo": False},
            {"moveit_servo.command_in_type": "unitless"},
            {"moveit_servo.scale.linear": 0.4},
            {"moveit_servo.scale.rotational": 0.8},
            {"moveit_servo.scale.joint": 0.5},
            {"moveit_servo.publish_period": 0.033},
            {"moveit_servo.low_latency_mode": False},
            {"moveit_servo.command_out_type": "trajectory_msgs/JointTrajectory"},
            {"moveit_servo.publish_joint_positions": True},
            {"moveit_servo.publish_joint_velocities": True},
            {"moveit_servo.publish_joint_accelerations": False},
            {"moveit_servo.smoothing_filter_plugin_name": "online_signal_smoothing::ButterworthFilterPlugin"},
            {"moveit_servo.is_primary_planning_scene_monitor": True},
            {"moveit_servo.move_group_name": "arm"},
            {"moveit_servo.planning_frame": "base_link"},
            {"moveit_servo.ee_frame_name": "end_effector_link"},
            {"moveit_servo.robot_link_command_frame": "base_link"},
            {"moveit_servo.incoming_command_timeout": 0.1},
            {"moveit_servo.num_outgoing_halt_msgs_to_publish": 4},
            {"moveit_servo.lower_singularity_threshold": 300000.0},
            {"moveit_servo.hard_stop_singularity_threshold": 400000.0},
            {"moveit_servo.joint_limit_margin": 0.1},
            {"moveit_servo.leaving_singularity_threshold_multiplier": 2.0},
            {"moveit_servo.cartesian_command_in_topic": "~/delta_twist_cmds"},
            {"moveit_servo.joint_command_in_topic": "~/delta_joint_cmds"},
            {"moveit_servo.joint_topic": "/joint_states"},
            {"moveit_servo.status_topic": "~/status"},
            {"moveit_servo.command_out_topic": "/arm_controller/joint_trajectory"},
            {"moveit_servo.check_collisions": True},
            {"moveit_servo.collision_check_rate": 10.0},
            {"moveit_servo.self_collision_proximity_threshold": 0.01},
            {"moveit_servo.scene_collision_proximity_threshold": 0.02},
            {"moveit_servo.use_sim_time": True},
        ],
        output="screen",
    )

    nodes_to_start = [
        ros2_control_node,
        robot_state_publisher,
        joint_state_broadcaster_spawner,
        delay_rviz_after_joint_state_broadcaster_spawner,
        robot_traj_controller_spawner,
        robot_pos_controller_spawner,
        robot_hand_controller_spawner,
        fault_controller_spawner,
        move_group_node,
        static_tf,
        servo_node,
    ]

    return nodes_to_start


def generate_launch_description():
    # Declare arguments
    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            "robot_ip",
            description="IP address by which the robot can be reached.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "use_fake_hardware",
            default_value="false",
            description="Start robot with fake hardware mirroring command to its states.",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "gripper_max_velocity",
            default_value="100.0",
            description="Max velocity for gripper commands",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "gripper_max_force",
            default_value="100.0",
            description="Max force for gripper commands",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "use_internal_bus_gripper_comm",
            default_value="true",
            description="Use arm's internal gripper connection",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "use_external_cable",
            default_value="false",
            description="Max force for gripper commands",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="false",
            description="Use simulated clock",
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument("launch_rviz", default_value="true", description="Launch RViz?")
    )

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])