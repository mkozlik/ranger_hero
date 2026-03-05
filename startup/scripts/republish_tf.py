#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy
from tf2_msgs.msg import TFMessage

class TFStaticRepublisher(Node):
    def __init__(self):
        super().__init__('tf_static_republisher')
        qos = QoSProfile(depth=10, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.pub = self.create_publisher(TFMessage, '/tf_static', qos)
        self.collected = []
        self.sub = self.create_subscription(TFMessage, '/tf_static', self.on_msg, qos)
        self.timer = self.create_timer(5.0, self.republish)

    def on_msg(self, msg):
        for t in msg.transforms:
            # Avoid duplicates by child_frame_id
            existing = [i for i, x in enumerate(self.collected) if x.child_frame_id == t.child_frame_id]
            if existing:
                self.collected[existing[0]] = t
            else:
                self.collected.append(t)

    def republish(self):
        if self.collected:
            out = TFMessage()
            out.transforms = list(self.collected)
            self.pub.publish(out)
            self.get_logger().info(f'Republished {len(self.collected)} static transforms')

def main():
    rclpy.init()
    rclpy.spin(TFStaticRepublisher())

if __name__ == '__main__':
    main()
