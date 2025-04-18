import numpy as np
from scipy.spatial.transform import Rotation as R

# 将四元数转换为旋转矩阵
def quaternion_to_rotation_matrix(q):
    r = R.from_quat(q)
    return r.as_matrix()

def quaternion_to_rotation_matrix0(qx, qy, qz, qw):
    """Convert quaternion to 3x3 rotation matrix"""
    q = np.array([qw, qx, qy, qz])
    q = q / np.linalg.norm(q)  # Normalize quaternion
    qw, qx, qy, qz = q
    return np.array([
        [1 - 2*qy**2 - 2*qz**2, 2*qx*qy - 2*qz*qw, 2*qx*qz + 2*qy*qw],
        [2*qx*qy + 2*qz*qw, 1 - 2*qx**2 - 2*qz**2, 2*qy*qz - 2*qx*qw],
        [2*qx*qz - 2*qy*qw, 2*qy*qz + 2*qx*qw, 1 - 2*qx**2 - 2*qy**2]
    ])


rotation_matrix = quaternion_to_rotation_matrix([-0.0115494377572271,-0.8612894823738078,0.50785859686529,-0.01125538225770515])
rotation_matrix0 = quaternion_to_rotation_matrix0(-0.0115494377572271,-0.8612894823738078,0.50785859686529,-0.01125538225770515)

# 打印结果
print("Rotation Matrix:")
print(rotation_matrix)
print("Rotation Matrix0:")
print(rotation_matrix0)