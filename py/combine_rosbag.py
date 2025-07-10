import rosbag
import rospy

def extract_topics_from_bag(input_bag_file, output_bag_file, topics):
    # 创建一个新的 bag 文件用于存储提取的数据
    with rosbag.Bag(output_bag_file, 'w') as out_bag:
        # 打开输入的 rosbag 文件
        with rosbag.Bag(input_bag_file, 'r') as in_bag:
            # 遍历输入 bag 文件中的每个 topic 和对应的消息
            for topic, msg, t in in_bag.read_messages():
                # 如果消息的 topic 在我们指定的 topic 列表中
                if topic in topics:
                    # 将该消息写入到新的 bag 文件中
                    out_bag.write(topic, msg, t)

def merge_rosbags(input_bag_files, output_bag_file, topics_to_extract):
    # 创建一个新的 bag 文件用于合成输出
    with rosbag.Bag(output_bag_file, 'w') as out_bag:
        # 遍历所有输入的 bag 文件
        for bag_file in input_bag_files:
            # 提取每个 bag 文件中的指定 topics
            with rosbag.Bag(bag_file, 'r') as in_bag:
                for topic, msg, t in in_bag.read_messages():
                    if topic in topics_to_extract:
                        # 将符合条件的消息写入到新的 bag 文件中
                        out_bag.write(topic, msg, t)

if __name__ == "__main__":
    # 输入的 rosbag 文件路径列表
    input_bag_files = ['/media/fhr/Elements/dataset/handle_mapping/25-07-09-9舍地下车库/2025-07-10-01-19-01.bag', '/media/fhr/Elements/dataset/handle_mapping/25-07-09-9舍地下车库/cam2.bag']
    
    # 指定要提取的 topic 列表
    topics_to_extract = ['/camera1/image/compressed','/imu','/hesai/pandar']

    # 输出的合成后的 rosbag 文件路径
    output_bag_file = '/media/fhr/Elements/dataset/handle_mapping/25-07-09-9舍地下车库/hesai-cam2.bag'

    # 合并多个 rosbag 文件
    merge_rosbags(input_bag_files, output_bag_file, topics_to_extract)

    rospy.loginfo(f"合并完成，输出文件：{output_bag_file}")
