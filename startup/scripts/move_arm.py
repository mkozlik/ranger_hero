import rclpy
from rclpy.node import Node
from moveit2 import MoveIt2
from geometry_msgs.msg import PoseStamped

class RelativeMove(Node):

    def __init__(self):
        super().__init__("relative_move")

        self.moveit2 = MoveIt2(
            node=self,
            joint_names=[
                "joint_1","joint_2","joint_3",
                "joint_4","joint_5","joint_6"
            ],
            base_link_name="base_link",
            end_effector_name="gripper_base_link",
            group_name="arm"
        )

        # Get current pose
        current_pose = self.moveit2.get_current_pose()

        target = PoseStamped()
        target.header.frame_id = "base_link"

        target.pose = current_pose.pose
        target.pose.position.x += 0.05  # move 5 cm in +X of base

        self.moveit2.move_to_pose(target)
        self.moveit2.wait_until_executed()


def main():
    rclpy.init()
    node = RelativeMove()
    rclpy.spin_once(node)
    rclpy.shutdown()