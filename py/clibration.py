import numpy as np
from scipy.spatial.transform import Rotation as R

# 将四元数转换为旋转矩阵
def quaternion_to_rotation_matrix(q):
    r = R.from_quat(q)
    return r.as_matrix()


rotation_matrix = quaternion_to_rotation_matrix([-0.0115494377572271,-0.8612894823738078,0.50785859686529,-0.01125538225770515])

# 打印结果
print("Rotation Matrix:")
print(rotation_matrix)