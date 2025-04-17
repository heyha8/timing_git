import numpy as np

def quaternion_to_rotation_matrix(qx, qy, qz, qw):
    """将四元数转换为3x3旋转矩阵"""
    q = np.array([qw, qx, qy, qz])
    q = q / np.linalg.norm(q)  # 归一化四元数
    qw, qx, qy, qz = q
    return np.array([
        [1 - 2*qy**2 - 2*qz**2, 2*qx*qy - 2*qz*qw, 2*qx*qz + 2*qy*qw],
        [2*qx*qy + 2*qz*qw, 1 - 2*qx**2 - 2*qz**2, 2*qy*qz - 2*qx*qw],
        [2*qx*qz - 2*qy*qw, 2*qy*qz + 2*qx*qw, 1 - 2*qx**2 - 2*qy**2]
    ])

def compute_lidar_to_camera_transform(R_ci, P_ci, R_il, P_il):
    """计算从LiDAR到相机的变换"""
    R_il_inv = R_il.T  # 旋转矩阵的逆为其转置
    R_cl = R_ci @ R_il_inv
    P_cl = P_ci - R_cl @ P_il
    return R_cl, P_cl

# IMU到相机2的变换
qx_ci = 0.7033672728261847
qy_ci = 0.001888893385981243
qz_ci = -0.7108198186191107
qw_ci = 0.002469221968063933
R_ci = quaternion_to_rotation_matrix(qx_ci, qy_ci, qz_ci, qw_ci)
P_ci = np.array([-0.06342325359291739,-0.005768949616455654,-0.05836565133347886])

# IMU到LiDAR的变换
lidar_configs = {
    '/hesai/pandar': {
        'qx': -0.0115494377572271,
        'qy': -0.8612894823738078,
        'qz': 0.50785859686529,
        'qw': -0.01125538225770515,
        'P': np.array([-0.05342769407014442, -0.003737439090847478, -0.04069358660072635])
    },
    '/livox/lidar': {
        'qx': -0.001959916542997731,
        'qy': -0.0183504131532268,
        'qz': -0.9998014967133597,
        'qw': 0.00750920994357774,
        'P': np.array([-0.0539114707266129, -0.002573553335441055, 0.1260177940561691])
    }
}

# 计算并输出变换
for lidar_key, config in lidar_configs.items():
    R_il = quaternion_to_rotation_matrix(config['qx'], config['qy'], config['qz'], config['qw'])
    P_il = config['P']
    R_cl, P_cl = compute_lidar_to_camera_transform(R_ci, P_ci, R_il, P_il)
    
    print(f"\n{lidar_key}的变换结果：")
    print("Rcl:", R_cl.flatten().tolist())
    print("Pcl:", P_cl.tolist())