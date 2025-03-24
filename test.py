import numpy as np
import matplotlib.pyplot as plt

# 读取 txt 文件并处理数据
def read_data(file_name):
    data = []
    with open(file_name, 'r') as file:
        for line in file:
            # 提取每行中的数值，假设每行是以逗号或空格分隔的数值
            numbers = [float(x) for x in line.strip().split(',')]
            data.append(numbers)
    return np.array(data)

# 计算每行与前一行的差值
def calculate_differences(data):
    # return data[1900:2000,:]
     return np.diff(data, axis=0)

# 绘制数据
def plot_data(differences):
    plt.figure(figsize=(10, 6))
    for i in range(differences.shape[1]):  # 对每列数据绘制曲线
        plt.plot(differences[:, i], label=f'Column {i}')
    
    plt.title('Differences between consecutive lines')
    plt.xlabel('Row Index')
    plt.ylabel('Difference')
    plt.legend()
    plt.grid(True)
    plt.show()

# 主函数
if __name__ == "__main__":
    file_name = '/home/fhr/.ros/imu_data.txt'  # 替换为你的文件路径
    data = read_data(file_name)
    
    if data.shape[0] > 1:  # 确保有多行数据
        differences = calculate_differences(data)
        plot_data(differences)
    else:
        print("数据行数不足，无法计算差异。")
