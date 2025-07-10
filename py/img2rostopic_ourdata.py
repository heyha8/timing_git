import os
import cv2
import rosbag
from sensor_msgs.msg import CompressedImage
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

def images_to_rosbag(image_folder, output_bag_path, topic_name="/camera/image_raw/compressed", 
                    resize_factor=0.25, add_8hours=False, discard_after_timestamp=None,discard_before_timestamp=None):
    """将文件夹中的图像转换为压缩格式的rosbag文件"""
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
                
            # 调整图像大小为0.25倍
            if resize_factor != 1.0:
                height, width = img.shape[:2]
                new_height = int(height * resize_factor)
                new_width = int(width * resize_factor)
                img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # 将图像转换为CompressedImage消息
            # 首先将图像编码为JPEG格式
            _, compressed_img = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
            compressed_img_data = np.array(compressed_img).tobytes()
            
            # 创建CompressedImage消息
            img_msg = CompressedImage()
            img_msg.header = Header()
            img_msg.header.stamp = rospy.Time.from_sec(timestamp)
            img_msg.header.frame_id = "camera_frame"
            img_msg.format = "jpeg"
            img_msg.data = compressed_img_data
            
            # 写入rosbag
            bag.write(topic_name, img_msg, img_msg.header.stamp)
            
            print(f"已处理: {image_file}, 时间戳: {timestamp}")
            
        print(f"完成！rosbag已保存至: {output_bag_path}")

if __name__ == "__main__":
    # 示例用法
    image_folder = "/media/fhr/Elements/dataset/handle_mapping/25-07-09-9舍地下车库/cam/image/camera_2"  # 替换为实际图像文件夹路径
    output_bag = "/media/fhr/Elements/dataset/handle_mapping/25-07-09-9舍地下车库/cam2.bag"  # 输出rosbag文件名
    topic_name = "/camera1/image/compressed"  # ROS压缩话题名称
    
    # 初始化ROS节点（仅用于获取rospy.Time）
    rospy.init_node('image_to_rosbag', anonymous=True)
    
    # 配置参数
    resize_factor = 1  # 图像缩放比例
    add_8hours = True    # 是否加上8小时
    discard_after_timestamp = 1752081820.37  # 舍弃此时间戳之后的数据，None表示不启用
    discard_before_timestamp = 1752081541.96  # 舍弃此时间戳之前的数据，None表示不启用
    
    images_to_rosbag(image_folder, output_bag, topic_name, 
                    resize_factor=resize_factor, 
                    add_8hours=add_8hours, 
                    discard_after_timestamp=discard_after_timestamp,
                    discard_before_timestamp=discard_before_timestamp)