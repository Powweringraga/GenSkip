import cv2
import numpy as np

def get_quest_marker_angle(minimap_crop):
    # Chuyển sang hệ màu HSV
    hsv = cv2.cvtColor(minimap_crop, cv2.COLOR_BGR2HSV)
    
    # Dải màu vàng của chấm nhiệm vụ Genshin (Cần tinh chỉnh bằng HSV Tool)
    lower_yellow = np.array([15, 150, 150])
    upper_yellow = np.array([35, 255, 255])
    
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    M = cv2.moments(mask)
    
    if M["m00"] != 0:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        # Tính góc quay so với tâm Minimap
        center_x, center_y = minimap_crop.shape[1] // 2, minimap_crop.shape[0] // 2
        angle = np.arctan2(cY - center_y, cX - center_x)
        return True, angle
    return False, None