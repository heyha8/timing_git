import cv2
import numpy as np

def undistort_image(raw_image, camera_params):
    """
    Undistort an image using fisheye camera parameters.
    
    Args:
        raw_image: Input image (numpy array)
        camera_params: Dictionary containing camera parameters (fx, fy, cx, cy, disto_param)
    
    Returns:
        rectified: Undistorted image
    """
    if raw_image is None or raw_image.size == 0:
        print("Error: Input image is empty!")
        return None

    # Extract camera parameters
    fx = camera_params['focal_length'][0]
    fy = camera_params['focal_length'][1]
    cx = camera_params['principal_point'][0]
    cy = camera_params['principal_point'][1]
    dist_coeffs = camera_params['disto_param']

    # Check if distortion coefficients are all zero
    if all(coeff == 0 for coeff in dist_coeffs):
        return raw_image.copy()

    # Construct camera matrix K
    K = np.array([[fx, 0, cx],
                  [0, fy, cy],
                  [0, 0, 1]], dtype=np.float64)

    # Construct distortion coefficients D
    D = np.array(dist_coeffs, dtype=np.float64)

    # Get image size
    h, w = raw_image.shape[:2]
    
    # Identity rotation matrix
    R = np.eye(3, dtype=np.float64)
    
    # Initialize mapping matrices
    map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, R, K, (w, h), cv2.CV_32FC1)
    
    # Perform remapping to undistort the image
    rectified = cv2.remap(raw_image, map1, map2, interpolation=cv2.INTER_LINEAR, 
                         borderMode=cv2.BORDER_CONSTANT)
    
    return rectified

# Example usage
if __name__ == "__main__":
    # Camera parameters
    camera_params = {
    'img_width': 3840,
    'img_height': 2160,
    'focal_length': [1124.887919056582, 1125.130274483685],
    'principal_point': [1910.872885036033, 1093.236507361603],
    'disto_param': [0.007625004377035269, -0.0206010373536668, 0.0334550082241107, -0.02411760701246449]
    }
    
    # Load image (replace 'input.jpg' with your image path)
    input_image = cv2.imread('/media/fhr/PSSD/shouchi_calib_bag/ikalibr-bag/lidar-camera/cam4/cam4-hesai.jpg')
    if input_image is not None:
        # Undistort image
        undistorted_image = undistort_image(input_image, camera_params)
        
        # Save output
        if undistorted_image is not None:
            cv2.imwrite('/media/fhr/PSSD/shouchi_calib_bag/ikalibr-bag/lidar-camera/cam4/undistorted_output.jpg', undistorted_image)
            print("Undistorted image saved as 'undistorted_output.jpg'")
    else:
        print("Error: Could not load input image")