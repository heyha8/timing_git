import rosbag
import rospy
import numpy as np
import os
import pickle

# 设置文件路径
bag_path = '/media/fhr/Elements/dataset/handle_mapping/25-4-17-indoor/6_sorted/all-camera2.bag'
output_txt = 'timestamps_comparison_6.txt'
timestamp_cache = 'timestamps_cache_6.pkl'
#corrected_cam_timestamps_txt = 'corrected_cam_timestamps.txt'

# 检查是否已有缓存的时间戳文件
def load_cached_timestamps():
    if os.path.exists(timestamp_cache):
        with open(timestamp_cache, 'rb') as f:
            data = pickle.load(f)
            return data['imu'], data['lidar'], data['cam']
    return None, None, None

# 保存时间戳到缓存
def save_timestamps_to_cache(imu_ts, lidar_ts, cam_ts):
    with open(timestamp_cache, 'wb') as f:
        pickle.dump({'imu': imu_ts, 'lidar': lidar_ts, 'cam': cam_ts}, f)

# 从rosbag中提取时间戳
def extract_timestamps_from_bag():
    bag = rosbag.Bag(bag_path)
    imu_timestamps = []
    lidar_timestamps = []
    cam_timestamps = []
    print("Reading rosbag...")
    for topic, msg, t in bag.read_messages(topics=[
        '/imu',
        '/livox/lidar',
        '/camera1/image/compressed'
    ]):
        if topic == '/imu':
            imu_timestamps.append(t.to_sec())
        elif topic == '/livox/lidar':
            lidar_timestamps.append(t.to_sec())
        elif topic == '/camera1/image/compressed':
            cam_timestamps.append(t.to_sec())
    bag.close()
    return imu_timestamps, lidar_timestamps, cam_timestamps

# 加载或提取时间戳
imu_timestamps, lidar_timestamps, cam_timestamps = load_cached_timestamps()
if imu_timestamps is None:
    print("No cached timestamps found, extracting from rosbag...")
    imu_timestamps, lidar_timestamps, cam_timestamps = extract_timestamps_from_bag()
    save_timestamps_to_cache(imu_timestamps, lidar_timestamps, cam_timestamps)
else:
    print("Loaded timestamps from cache.")

# 自适应计算IMU相对于LiDAR和Camera的更新比率
def calculate_update_ratios(imu_count, lidar_count, cam_count):
    lidar_ratio = 1
    cam_ratio = 1
    if imu_count > 0 and lidar_count > 0:
        lidar_ratio = max(1, round(imu_count / lidar_count))
    if imu_count > 0 and cam_count > 0:
        cam_ratio = max(1, round(imu_count / cam_count))
    return lidar_ratio, cam_ratio

lidar_update_ratio, cam_update_ratio = calculate_update_ratios(len(imu_timestamps), len(lidar_timestamps), len(cam_timestamps))
print(f"LiDAR update ratio: {lidar_update_ratio} IMU frames per LiDAR frame")
print(f"Camera update ratio: {cam_update_ratio} IMU frames per Camera frame")

# 计算LiDAR和Camera的初始偏置
def calculate_cam_lidar_bias(lidar_ts, cam_ts, lidar_ratio, cam_ratio, num_pairs=50):
    if len(lidar_ts) < num_pairs or len(cam_ts) < num_pairs:
        return 0.0, 0
    first_lidar_time = lidar_ts[0]
    cam_diffs = [abs(cam_ts[j] - first_lidar_time) for j in range(len(cam_ts))]
    closest_cam_idx = np.argmin(cam_diffs)
    cam_step = max(1, round(lidar_ratio / cam_ratio)) if lidar_ratio > 0 else 1
    biases = []
    cam_idx = closest_cam_idx
    lidar_idx = 0
    for i in range(num_pairs):
        if cam_idx < len(cam_ts) and lidar_idx < len(lidar_ts):
            bias = lidar_ts[lidar_idx] - cam_ts[cam_idx]
            biases.append(bias)
            cam_idx += cam_step
            lidar_idx += 1
    return np.mean(biases) if biases else 0.0, closest_cam_idx

average_cam_bias, closest_cam_idx = calculate_cam_lidar_bias(lidar_timestamps, cam_timestamps, lidar_update_ratio, cam_update_ratio)
print(f"Average Initial Bias (LIDAR - CAM): {average_cam_bias:.6f} seconds")

# 计算IMU和LiDAR的初始偏置
def calculate_imu_lidar_bias(imu_ts, lidar_ts, update_ratio, num_pairs=5):
    if len(imu_ts) < 15 or len(lidar_ts) < num_pairs:
        return 0.0, 0
    first_lidar_time = lidar_ts[0]
    imu_diffs = [abs(imu_ts[i] - first_lidar_time) for i in range(min(15, len(imu_ts)))]
    closest_imu_idx = np.argmin(imu_diffs)
    biases = []
    imu_idx = closest_imu_idx
    lidar_idx = 0
    for i in range(num_pairs):
        if imu_idx < len(imu_ts) and lidar_idx < len(lidar_ts):
            bias = imu_ts[imu_idx] - lidar_ts[lidar_idx]
            biases.append(bias)
            imu_idx += update_ratio
            lidar_idx += 1
    return np.mean(biases) if biases else 0.0, closest_imu_idx

average_imu_bias, closest_imu_idx = calculate_imu_lidar_bias(imu_timestamps, lidar_timestamps, lidar_update_ratio)
print(f"Average Initial Bias (IMU - LIDAR): {average_imu_bias:.6f} seconds")

# 写入时间戳对比并收集cam_lidar_errors
imu_lidar_errors = []
cam_lidar_errors = []
aligned_cam_timestamps = []  # 存储与cam_lidar_errors对应的相机时间戳
with open(output_txt, 'w') as f:
    f.write("IMU, LIDAR, and CAMERA Timestamps Comparison\n")
    f.write("=" * 50 + "\n")
    f.write(f"IMU Rate: {len(imu_timestamps)} messages\n")
    f.write(f"LIDAR Rate: {len(lidar_timestamps)} messages\n")
    f.write(f"CAMERA Rate: {len(cam_timestamps)} messages\n")
    f.write(f"LiDAR Update Ratio: {lidar_update_ratio} IMU frames per LiDAR frame\n")
    f.write(f"Camera Update Ratio: {cam_update_ratio} IMU frames per Camera frame\n")
    f.write(f"Average Initial Bias (LIDAR - CAM): {average_cam_bias:.6f} seconds\n")
    f.write(f"Average Initial Bias (IMU - LIDAR): {average_imu_bias:.6f} seconds\n")
    f.write("\nTimestamp Comparison:\n")
    f.write("=" * 50 + "\n")

    imu_idx = closest_imu_idx
    lidar_idx = 0
    cam_idx = closest_cam_idx
    imu_lidar_counter = 0
    imu_cam_counter = 0
    while imu_idx < len(imu_timestamps) and lidar_idx < len(lidar_timestamps) and cam_idx < len(cam_timestamps):
        imu_time = imu_timestamps[imu_idx]
        lidar_time = lidar_timestamps[lidar_idx] if lidar_idx < len(lidar_timestamps) else None
        cam_time = cam_timestamps[cam_idx] if cam_idx < len(cam_timestamps) else None

        imu_lidar_error = None
        cam_lidar_error = None
        write_to_file = False

        if lidar_time is not None and imu_lidar_counter % lidar_update_ratio == 0:
            imu_lidar_error = imu_time - lidar_time - average_imu_bias
            imu_lidar_errors.append(imu_lidar_error)

        if cam_time is not None and imu_cam_counter % cam_update_ratio == 0:
            if lidar_time is not None:
                cam_lidar_error = lidar_time - cam_time - average_cam_bias
                cam_lidar_errors.append(cam_lidar_error)
                aligned_cam_timestamps.append(cam_time)

        if (imu_lidar_counter % lidar_update_ratio == 0 and 
            imu_cam_counter % cam_update_ratio == 0 and 
            lidar_time is not None and 
            cam_time is not None):
            write_to_file = True

        if write_to_file:
            f.write("IMU Timestamp: {:.6f}, LIDAR Timestamp: {:.6f}, CAM Timestamp: {:.6f}\n".format(
                imu_time, lidar_time, cam_time
            ))
            if imu_lidar_error is not None:
                f.write("IMU-LIDAR Error (IMU - LIDAR - Bias): {:.6f}, ".format(imu_lidar_error))
            if cam_lidar_error is not None:
                f.write("CAM-LIDAR Error (LIDAR - CAM - Bias): {:.6f}\n".format(cam_lidar_error))

            aligned = True
            if imu_lidar_error is not None and abs(imu_lidar_error) >= 0.06:
                f.write("IMU and LIDAR Not Aligned, Error: {:.6f}\n".format(abs(imu_lidar_error)))
                aligned = False
            if cam_lidar_error is not None and abs(cam_lidar_error) >= 0.06:
                f.write("LIDAR and CAM Not Aligned, Error: {:.6f}\n".format(abs(cam_lidar_error)))
                aligned = False
            if aligned:
                f.write("Aligned\n")

        imu_idx += 1
        imu_lidar_counter += 1
        imu_cam_counter += 1
        if imu_lidar_counter >= lidar_update_ratio:
            lidar_idx += 1
            imu_lidar_counter = 0
        if imu_cam_counter >= cam_update_ratio:
            cam_idx += 1
            imu_cam_counter = 0

# 输出平均时间误差
if imu_lidar_errors:
    average_imu_lidar_error = np.mean(imu_lidar_errors)
    print(f"Average Time Error (IMU - LIDAR - Bias): {average_imu_lidar_error:.6f} seconds")
else:
    print("No IMU-LIDAR time errors calculated")

if cam_lidar_errors:
    average_cam_lidar_error = np.mean(cam_lidar_errors)
    print(f"Average Time Error (LIDAR - CAM - Bias): {average_cam_lidar_error:.6f} seconds")
else:
    print("No CAM-LIDAR time errors calculated")

print(f"Timestamp comparison has been saved to {output_txt}")

# # 修正相机时间戳
# corrected_cam_timestamps = []
# cam_idx = 0
# error_idx = 0

# for cam_time in cam_timestamps:
#     if cam_idx < len(cam_timestamps):
#         # 检查是否有对应的误差
#         if error_idx < len(cam_lidar_errors) and abs(cam_time - aligned_cam_timestamps[error_idx]) < 0.01:
#             # 使用误差修正时间戳
#             corrected_time = cam_time + cam_lidar_errors[error_idx]
#             corrected_cam_timestamps.append(corrected_time)
#             error_idx += 1
#         else:
#             # 没有对应误差，使用前后帧插值
#             if error_idx == 0:
#                 # 在第一个误差之前，使用第一个误差
#                 corrected_time = cam_time + cam_lidar_errors[0]
#             elif error_idx >= len(cam_lidar_errors):
#                 # 在最后一个误差之后，使用最后一个误差
#                 corrected_time = cam_time + cam_lidar_errors[-1]
#             else:
#                 # 在两个误差之间，线性插值
#                 t1 = aligned_cam_timestamps[error_idx - 1]
#                 t2 = aligned_cam_timestamps[error_idx]
#                 e1 = cam_lidar_errors[error_idx - 1]
#                 e2 = cam_lidar_errors[error_idx]
#                 weight = (cam_time - t1) / (t2 - t1)
#                 interpolated_error = e1 + weight * (e2 - e1)
#                 corrected_time = cam_time + interpolated_error
#             corrected_cam_timestamps.append(corrected_time)
#         cam_idx += 1

# # 将修正后的相机时间戳保存到 TXT 文件
# with open(corrected_cam_timestamps_txt, 'w') as f:
#     f.write("Corrected Camera Timestamps\n")
#     f.write("=" * 50 + "\n")
#     for t in corrected_cam_timestamps:
#         f.write("{:.6f}\n".format(t))

#print(f"Corrected camera timestamps saved to {corrected_cam_timestamps_txt}")