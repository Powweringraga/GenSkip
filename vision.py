import os
import shutil
import cv2
import numpy as np
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = (
    os.environ.get("TESSERACT_CMD")
    or shutil.which("tesseract")
    or r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


class VisionEngine:

  @staticmethod
  def extract_dialogue_text(img_roi):
    """Read visible dialogue text from a BGR screenshot region."""
    gray = cv2.cvtColor(img_roi, cv2.COLOR_BGR2GRAY)
    enlarged = cv2.resize(
        gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC
    )
    try:
      text = pytesseract.image_to_string(
          enlarged, lang="eng", config="--psm 6"
      )
    except pytesseract.TesseractNotFoundError as error:
      raise RuntimeError(
          "Tesseract OCR was not found. Install Tesseract or set TESSERACT_CMD."
      ) from error
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)

  @staticmethod
  def find_template(haystack_img, needle_img_path, threshold=0.8):
    """Tìm kiếm vị trí nút mẫu trong ảnh ROI."""
    needle = cv2.imread(needle_img_path)
    if needle is None:
      return False, None

    result = cv2.matchTemplate(haystack_img, needle, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
      h, w = needle.shape[:2]
      center_x = max_loc[0] + w // 2
      center_y = max_loc[1] + h // 2
      return True, (center_x, center_y)

    return False, None

  @staticmethod
  def extract_all_choices(img_roi, template_path, threshold=0.70):
    """Phát hiện TẤT CẢ các nút lựa chọn thoại trên màn hình, đọc chữ từng nút

    bằng OCR và trả về danh sách văn bản + tọa độ tâm của từng nút.
    """
    options_text = []
    options_coords = []

    needle = cv2.imread(template_path)
    if needle is None:
      return options_text, options_coords

    h, w = needle.shape[:2]
    result = cv2.matchTemplate(img_roi, needle, cv2.TM_CCOEFF_NORMED)

    # Lấy tất cả các vị trí có độ khớp >= threshold
    locs = np.where(result >= threshold)
    matches = list(zip(*locs[::-1]))

    if not matches:
      return options_text, options_coords

    # Nén các điểm tìm kiếm bị trùng lặp gần nhau (Non-Maximum Suppression đơn giản)
    filtered_matches = []
    for pt in sorted(matches, key=lambda x: x[1]):  # Sắp xếp theo chiều dọc Y
      if not any(abs(pt[1] - existing[1]) < 20 for existing in filtered_matches):
        filtered_matches.append(pt)

    # Đọc chữ và lấy tọa độ cho từng nút thoại
    for pt in filtered_matches:
      center_x = pt[0] + w // 2
      center_y = pt[1] + h // 2

      # Cắt vùng chứa chữ bên phải biểu tượng nút thoại
      text_crop = img_roi[
          max(0, pt[1] - 5) : min(img_roi.shape[0], pt[1] + h + 5),
          pt[0] + w : min(img_roi.shape[1], pt[0] + w + 350),
      ]

      # Dùng OCR đọc nội dung của nút
      try:
        rgb_crop = cv2.cvtColor(text_crop, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_crop)
        text = pytesseract.image_to_string(pil_img, lang="eng").strip()
      except Exception:
        text = ""

      options_text.append(text if text else f"Option at Y={center_y}")
      options_coords.append((center_x, center_y))

    return options_text, options_coords