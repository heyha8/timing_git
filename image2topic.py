import rospy
import cv2
import os
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from std_msgs.msg import Header

# ROS 初始化
rospy.init_node('image_publisher', anonymous=True)

# 创建 CvBridge 对象，用于转换 OpenCV 图像与 ROS 图像消息
bridge = CvBridge()

# 创建发布者对象
image_pub = rospy.Publisher('/left_camera/image', Image, queue_size=10)

# 设置要读取的图像文件夹路径
image_folder = os.path.expanduser('~/data/data/image')   # 修改为你自己的文件夹路径

# 获取文件夹中的所有子文件夹
def get_subfolders():
    subfolders = []
    for folder_name in os.listdir(image_folder):
        folder_path = os.path.join(image_folder, folder_name)
        if os.path.isdir(folder_path):  # 只获取文件夹
            subfolders.append(folder_path)
    return subfolders

# 获取每个子文件夹内的第一张图像（假设按字母顺序选择）
def get_image_from_folder(folder_path):
    image_files = [f for f in os.listdir(folder_path) if f.endswith('.jpg') or f.endswith('.png')]
    image_files.sort()  # 可以按名称排序，选择第一张图像
    if image_files:
        return os.path.join(folder_path, image_files[0])  # 返回文件路径
    return None

# 读取图像并发布
def publish_images():
    # 获取所有子文件夹
    subfolders = get_subfolders()

    for subfolder in subfolders:
        # 获取子文件夹内的第一张图像
        image_file = get_image_from_folder(subfolder)

        if image_file:
            # 读取图像
            cv_image = cv2.imread(image_file)

            # 检查图像是否成功读取
            if cv_image is None:
                rospy.logwarn(f"Failed to read image {image_file}")
                continue

            # 将 OpenCV 图像转换为 ROS 图像消息
            try:
                ros_image = bridge.cv2_to_imgmsg(cv_image, encoding="bgr8")
            except CvBridgeError as e:
                rospy.logerr(f"Error converting image: {e}")
                continue

            # 创建消息头
            header = Header()
            header.stamp = rospy.Time.now()
            header.frame_id = "left_camera"  # 设置为相机的 frame_id

            # 设置图像的时间戳和其他信息
            ros_image.header = header

            # 发布图像
            image_pub.publish(ros_image)

            rospy.loginfo(f"Published image: {image_file}")

            # 可选择延时来控制发布频率（比如每 0.5 秒发布一次）
            rospy.sleep(0.5)

# 主循环
if __name__ == "__main__":
    try:
        while not rospy.is_shutdown():
            publish_images()
    except rospy.ROSInterruptException:
        pass
