import numpy as np

def quaternion_and_translation_to_transform(qx, qy, qz, qw, t):
    """Convert quaternion and translation to 4x4 transformation matrix"""
    q = np.array([qw, qx, qy, qz])
    q = q / np.linalg.norm(q)  # Normalize quaternion
    qw, qx, qy, qz = q
    R = np.array([
        [1 - 2*qy**2 - 2*qz**2, 2*qx*qy - 2*qz*qw, 2*qx*qz + 2*qy*qw],
        [2*qx*qy + 2*qz*qw, 1 - 2*qx**2 - 2*qz**2, 2*qy*qz - 2*qx*qw],
        [2*qx*qz - 2*qy*qw, 2*qy*qz + 2*qx*qw, 1 - 2*qx**2 - 2*qy**2]
    ])
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = t
    return T

def compute_lidar_to_camera_transform(T_il, T_ci):
    """Compute transformation from LiDAR to camera using transformation matrices"""
    T_cl = T_ci @ T_il
    R_cl = T_cl[:3, :3]
    P_cl = T_cl[:3, 3]
    return R_cl, P_cl

# Camera configurations (IMU to Camera)
camera_configs = {
    '/camera1/image_raw': {
        'qx': -0.5014919942359141,
        'qy': 0.4940119643945745,
        'qz': -0.4996808167412811,
        'qw': -0.5047544354763671,
        'P': np.array([0.0002384815967839808, -0.07021666474267334, -0.06198398020359156])
    },
    '/camera2/image_raw': {
        'qx': 0.7041876709956439,
        'qy': 0.003554908799898653,
        'qz': -0.7099931820693703,
        'qw': 0.004094881703420828,
        'P': np.array([-0.04274680538157673, 0.002678105323233039,-0.02867295405798999])
    },
    '/camera3/image_raw': {
        'qx': -0.5128203538420552,
        'qy': -0.4992145044149796,
        'qz': -0.4903551147217995,
        'qw': 0.4973449755785091,
        'P': np.array([0.002587633567970967, 0.05174615613791331, -0.05749103369172464])
    },
    '/camera4/image_raw': {
        'qx': 0.01854158489488407,
        'qy': -0.7139846285542719,
        'qz': -0.001252055056512248,
        'qw': -0.6999147035003197,
        'P': np.array([0.06337303105444164, 0.001106592139457578, -0.05873348582844092])
    }
}

# LiDAR configurations (IMU to LiDAR)
lidar_configs = {
    '/hesai/pandar': {
        'qx': -0.03157945960890955,
        'qy': -0.8466653625576385,
        'qz': 0.5310451474602664,
        'qw': -0.01231068376878419,
        'P': np.array([0.01055170343154121,-0.113562897147613, -0.1350520956045414])
    },
    '/livox/lidar': {
        'qx': -0.00352177157019005,
        'qy': -0.006292580862168814,
        'qz': -0.9999732913577816,
        'qw': -0.001190429412274317,
        'P': np.array([0.01109517862721343,0.01298655847841911,0.09377467713554094])
    }
}

# Compute and output transformations
for lidar_key, lidar_config in lidar_configs.items():
    T_il = quaternion_and_translation_to_transform(
        lidar_config['qx'], lidar_config['qy'], lidar_config['qz'], lidar_config['qw'], lidar_config['P']
    )
    
    R_il = T_il[:3, :3]
    P_il = T_il[:3, 3]
    
    print(f"\n{lidar_key} to IMU:")
    print("extrinsic_R:", R_il.flatten().tolist())
    print("extrinsic_T:", P_il.tolist())
    
    for camera_key, camera_config in camera_configs.items():
        T_ic = quaternion_and_translation_to_transform(
            camera_config['qx'], camera_config['qy'], camera_config['qz'], camera_config['qw'], camera_config['P']
        )

        T_ci = np.linalg.inv(T_ic)
        
        R_cl, P_cl = compute_lidar_to_camera_transform(T_il, T_ci)
        
        print(f"\n{lidar_key} to {camera_key}:")
        print("Rcl:", R_cl.flatten().tolist())
        print("Tcl:", P_cl.tolist())