import cv2


class VisionEngine:

  @staticmethod
  def find_template(haystack_img, needle_img_path, threshold=0.8):
    # Đọc ảnh mẫu (Dùng chữ thường needle)
    needle = cv2.imread(needle_img_path)

    # Kiểm tra xem ảnh mẫu có tồn tại/đọc thành công không
    if needle is None:
      return False, None

    # Tìm kiếm template
    result = cv2.matchTemplate(haystack_img, needle, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
      # Tính toán tọa độ tâm
      h, w = needle.shape[:2]
      center_x = max_loc[0] + w // 2
      center_y = max_loc[1] + h // 2
      return True, (center_x, center_y)

    return False, None