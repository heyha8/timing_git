import os
import cv2
import rosbag
from sensor_msgs.msg import Image, CompressedImage
from cv_bridge import CvBridge
import rospy
from std_msgs.msg import Header
import numpy as np

def get_image_timestamp(image_path):
    """从图像文件名中提取时间戳，格式为1744844702394718.jpg，后六位为小数"""
    filename = os.path.basename(image_path)
    try:
        # 提取时间戳（文件名去掉扩展名）
        timestamp_str = filename.split('.')[0]
        # 将时间戳转换为浮点数，假设后6位是小数
        timestamp = float(timestamp_str[:-6] + '.' + timestamp_str[-6:])
        return timestamp
    except Exception as e:
        print(f"无法解析时间戳，使用文件修改时间: {e}")
        return os.path.getmtime(image_path)

def images_to_rosbag(image_folder, output_bag_path, topic_name="/camera/image_raw",
                     resize_factor=1.0, add_8hours=False, discard_after_timestamp=None,
                     discard_before_timestamp=None, use_compressed=False):
    """
    将文件夹中的图像转换为 rosbag 文件

    参数:
        image_folder: 图像文件夹路径
        output_bag_path: 输出 rosbag 文件路径
        topic_name: ROS 话题名（基础名）
        resize_factor: 图像缩放比例
        add_8hours: 是否给时间戳加8小时
        discard_after_timestamp: 舍弃此时间戳之后的图像
        discard_before_timestamp: 舍弃此时间戳之前的图像
        use_compressed: 是否使用 CompressedImage 消息类型
    """
    # 初始化CvBridge
    bridge = CvBridge()
    
    # 创建rosbag文件
    with rosbag.Bag(output_bag_path, 'w') as bag:
        # 获取图像文件列表并排序
        image_files = sorted(
            [f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))],
            key=lambda x: get_image_timestamp(os.path.join(image_folder, x))
        )
        
        if not image_files:
            print("文件夹中没有找到图像文件")
            return

        for image_file in image_files:
            image_path = os.path.join(image_folder, image_file)
            timestamp = get_image_timestamp(image_path)
            
            # 可选：将时间戳加上8小时
            if add_8hours:
                timestamp += 8 * 3600  # 8小时转换为秒
            
            # 检查是否需要舍弃晚于指定时间戳的数据
            if discard_after_timestamp is not None and timestamp > discard_after_timestamp:
                print(f"跳过图像 {image_file}，时间戳 {timestamp} 晚于 {discard_after_timestamp}")
                continue

            # 检查是否需要舍弃早于指定时间戳的数据
            if discard_before_timestamp is not None and timestamp < discard_before_timestamp:
                print(f"跳过图像 {image_file}，时间戳 {timestamp} 早于 {discard_before_timestamp}")
                continue
            
            # 读取图像
            img = cv2.imread(image_path)
            if img is None:
                print(f"无法读取图像: {image_path}")
                continue
                
            # 调整图像大小
            if resize_factor != 1.0:
                height, width = img.shape[:2]
                new_height = int(height * resize_factor)
                new_width = int(width * resize_factor)
                img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # 根据 use_compressed 决定消息类型
            if use_compressed:
                # 编码为 JPEG
                success, encoded_image = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
                if not success:
                    print(f"图像编码失败: {image_file}")
                    continue
                compressed_data = np.array(encoded_image).tobytes()

                # 创建 CompressedImage 消息
                img_msg = CompressedImage()
                img_msg.header = Header()
                img_msg.header.stamp = rospy.Time.from_sec(timestamp)
                img_msg.header.frame_id = "camera_frame"
                img_msg.format = "jpeg"
                img_msg.data = compressed_data

                # 写入 rosbag（话题名自动加 /compressed）
                final_topic = topic_name.rstrip('/') + '/compressed'
                bag.write(final_topic, img_msg, img_msg.header.stamp)
                print(f"已处理 (compressed): {image_file}, 时间戳: {timestamp}, 话题: {final_topic}")

            else:
                # 使用 sensor_msgs/Image
                try:
                    img_msg = bridge.cv2_to_imgmsg(img, encoding="bgr8")
                    img_msg.header.stamp = rospy.Time.from_sec(timestamp)
                    img_msg.header.frame_id = "camera_frame"
                except Exception as e:
                    print(f"cv_bridge 转换失败: {e}")
                    continue

                # 写入 rosbag
                final_topic = topic_name
                bag.write(final_topic, img_msg, img_msg.header.stamp)
                print(f"已处理 (raw): {image_file}, 时间戳: {timestamp}, 话题: {final_topic}")
            
        print(f"完成！rosbag 已保存至: {output_bag_path}")


if __name__ == "__main__":
    # ================== 用户配置区 ==================
    image_folder = "/media/fhr/Elements/dataset/handle_mapping/25-07-10-calibration_dvlc/cam/cam1-4/camera_2"  # 图像文件夹
    output_bag = "/media/fhr/Elements/dataset/handle_mapping/25-07-10-calibration_dvlc/dvlc_cam2.bag"          # 输出 bag 路径
    topic_name = "/camera1/image"  # 基础话题名（如果是 compressed，会自动变为 /camera1/image/compressed）

    # 其他参数
    resize_factor = 1.0                   # 缩放比例 (1.0 = 原图)
    add_8hours = True                     # 是否加8小时
    discard_after_timestamp = 1752145934.92   # 舍弃之后的时间戳（None 表示不禁用）
    discard_before_timestamp = 1752145888.41  # 舍弃之前的时间戳

    # 🔥 关键选项：是否使用 compressed 图像
    use_compressed = False  # True -> CompressedImage, False -> Image
    # =================================================

    # 初始化ROS节点（用于时间戳）
    rospy.init_node('image_to_rosbag', anonymous=True)
    
    # 调用函数
    images_to_rosbag(
        image_folder=image_folder,
        output_bag_path=output_bag,
        topic_name=topic_name,
        resize_factor=resize_factor,
        add_8hours=add_8hours,
        discard_after_timestamp=discard_after_timestamp,
        discard_before_timestamp=discard_before_timestamp,
        use_compressed=use_compressed
    )