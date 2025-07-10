import rosbag
import rospy
from sensor_msgs.msg import CompressedImage

# 输入和输出文件路径
bag_path = '/media/fhr/Elements/dataset/handle_mapping/oxford/keble-collage-3/keble-collage-3-cam1_compressed.bag'
corrected_cam_timestamps_txt = 'corrected_cam_timestamps.txt'
output_bag_path = '/media/fhr/Elements/dataset/handle_mapping/oxford/keble-collage-3/keble_updated_timestamps.bag'

# 读取修正后的相机时间戳
corrected_timestamps = []
with open(corrected_cam_timestamps_txt, 'r') as f:
    lines = f.readlines()
    for line in lines:
        if line.strip() and not line.startswith("Corrected") and not line.startswith("="):
            corrected_timestamps.append(float(line.strip()))

# 更新 rosbag 中相机 topic 的时间戳
bag = rosbag.Bag(bag_path)
out_bag = rosbag.Bag(output_bag_path, 'w')

cam_topic = '/camera1/image/compressed'
cam_idx = 0

print("Updating timestamps in rosbag...")
for topic, msg, t in bag.read_messages():
    if topic == cam_topic and cam_idx < len(corrected_timestamps):
        # 更新消息的时间戳
        new_timestamp = rospy.Time.from_sec(corrected_timestamps[cam_idx])
        msg.header.stamp = new_timestamp
        out_bag.write(topic, msg, new_timestamp)
        cam_idx += 1
    else:
        # 非相机 topic 直接写入
        out_bag.write(topic, msg, t)

bag.close()
out_bag.close()

print(f"New rosbag with updated timestamps saved to {output_bag_path}")