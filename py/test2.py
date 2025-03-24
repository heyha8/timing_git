import numpy as np
import matplotlib.pyplot as plt
import os

# 读取 txt 文件并处理数据
def read_data(file_name):
    data = []
    with open(file_name, 'r') as file:
        for line in file:
            # 提取每行中的数值，假设每行是以冒号分隔的数值
            numbers = [float(x.split(': ')[1]) for x in line.strip().split(',') if ':' in x]  # 提取以冒号为分隔的数值
            data.append(numbers)
    return np.array(data)

# 绘制数据
def plot_data(data):
    plt.figure(figsize=(10, 6))
    for i in range(data.shape[1]):  # 对每列数据绘制曲线
        plt.plot(data[:, i], label=f'Column {i}')
    
    plt.title('IMU Data')
    plt.xlabel('Row Index')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True)
    plt.show()

# 主函数
if __name__ == "__main__":
    file_name = '/home/fhr/.ros/imu_data.txt'  # 替换为你的文件路径
    data = read_data(file_name)
    
    if data.shape[0] > 0:  # 确保有行数据
        plot_data(data)
    else:
        print("数据行数不足，无法绘图。")