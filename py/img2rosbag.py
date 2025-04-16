import os
import cv2
import rosbag
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import rospy
from std_msgs.msg import Header

def get_image_timestamp(image_path):
    """从图像文件名中提取时间戳，格式为1710256033.944435656.jpg"""
    filename = os.path.basename(image_path)
    try:
        # 提取时间戳（文件名去掉扩展名）
        timestamp_str = filename.split('.')[0] + '.' + filename.split('.')[1]
        return float(timestamp_str)
    except Exception as e:
        print(f"无法解析时间戳，使用文件修改时间: {e}")
        return os.path.getmtime(image_path)

def images_to_rosbag(image_folder, output_bag_path, topic_name="/camera/image_raw"):
    """将文件夹中的图像转换为rosbag文件"""
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
            
            # 读取图像
            img = cv2.imread(image_path)
            if img is None:
                print(f"无法读取图像: {image_path}")
                continue
                
            # 转换为ROS Image消息
            img_msg = bridge.cv2_to_imgmsg(img, encoding="bgr8")
            
            # 设置消息头
            img_msg.header = Header()
            img_msg.header.stamp = rospy.Time.from_sec(timestamp)
            img_msg.header.frame_id = "camera_frame"
            
            # 写入rosbag
            bag.write(topic_name, img_msg, img_msg.header.stamp)
            
            print(f"已处理: {image_file}, 时间戳: {timestamp}")
            
        print(f"完成！rosbag已保存至: {output_bag_path}")

if __name__ == "__main__":
    # 示例用法
    image_folder = "/home/fhr/data/handle_mapping/oxford/keble-collage-3/images_raw/cam1"  # 替换为实际图像文件夹路径
    output_bag = "keble-collage-3-cam1.bag"                    # 输出rosbag文件名
    topic_name = "/camera1/image"            # ROS话题名称
    
    # 初始化ROS节点（仅用于获取rospy.Time）
    rospy.init_node('image_to_rosbag', anonymous=True)
    
    images_to_rosbag(image_folder, output_bag, topic_name)