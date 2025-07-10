import rosbag
import rospy

# 设置rosbag文件路径
bag_path = '/media/fhr/Elements/dataset/handle_mapping/25-5-19-static/indoor2/2025-05-19-17-46-55.bag'
output_txt = 'timestamps_comparison_519indoor2_mid360.txt'

# 打开rosbag文件
bag = rosbag.Bag(bag_path)

# 用来存储时间戳
imu_timestamps = []
lidar_timestamps = []

# 读取/imu和/livox/lidar话题的消息
for topic, msg, t in bag.read_messages(topics=['/imu', '/livox/lidar']):
    if topic == '/imu':
        imu_timestamps.append(t.to_sec())
    elif topic == '/livox/lidar':
        lidar_timestamps.append(t.to_sec())

# 关闭rosbag文件
bag.close()

# 将时间戳写入txt文件并对比
with open(output_txt, 'w') as f:
    f.write("IMU Timestamps and LIDAR Timestamps Comparison\n")
    f.write("=" * 50 + "\n")
    f.write(f"IMU Rate: {len(imu_timestamps)} messages (100Hz)\n")
    f.write(f"LIDAR Rate: {len(lidar_timestamps)} messages (10Hz)\n")
    f.write("\nTimestamp Comparison:\n")
    f.write("=" * 50 + "\n")

    # 遍历并对比两个时间戳列表
    imu_idx = 0
    lidar_idx = 0
    while imu_idx < len(imu_timestamps) and lidar_idx < len(lidar_timestamps):
        imu_time = imu_timestamps[imu_idx]
        lidar_time = lidar_timestamps[lidar_idx]

        # 写入时间戳对比
        f.write(f"IMU Timestamp: {imu_time:.6f}, LIDAR Timestamp: {lidar_time:.6f}\n")

        # 检查时间戳对齐情况（考虑到IMU为100Hz，LIDAR为10Hz）
        if abs(imu_time - lidar_time) < 0.12:
            f.write("Aligned\n")
        else:
            f.write("Not Aligned\n")
        
        # # 根据时间戳的大小，更新索引
        # if imu_time < lidar_time:
        #     imu_idx += 1
        # else:
        #     lidar_idx += 1
        # 每增加10个IMU数据点，增加1个LIDAR数据点
        imu_idx += 1
        if imu_idx % 20 == 0:
            lidar_idx += 1

print(f"Time-stamp comparison has been saved to {output_txt}")
