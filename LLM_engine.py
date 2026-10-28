import cv2
from PIL import Image
import pytesseract
import requests

# Đường dẫn Tesseract trên Windows
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


class GenSkipAI:

  def __init__(
      self, server_url: str = "https://genskip-server.vercel.app/summarize"
  ):
    self.server_url = server_url
    self.buffer = []  # Bộ đệm lưu tích lũy các câu thoại

  def extract_text(self, img_bgr) -> str:
    """Đọc chữ từ ảnh ROI bằng Pytesseract"""
    try:
      img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
      pil_img = Image.fromarray(img_rgb)
      text = pytesseract.image_to_string(pil_img, lang="eng")
      clean_text = text.strip()

      # Nếu có chữ mới và chưa bị trùng lặp với câu vừa đọc gần nhất
      if clean_text and len(clean_text) > 8:
        if not self.buffer or clean_text not in self.buffer[-3:]:
          self.buffer.append(clean_text)
          return clean_text
      return ""
    except Exception as e:
      print(f"[OCR Error] {e}")
      return ""

  def summarize_buffered_lore(self) -> str:
    """Gửi toàn bộ bộ đệm thoại lên Server Proxy và làm sạch buffer"""
    if not self.buffer:
      return ""

    # Nối tất cả các câu thoại tích lũy thành 1 đoạn văn hoàn chỉnh
    full_text = "\n".join(self.buffer)

    # Xóa bộ đệm sau khi đã lấy văn bản để chuẩn bị cho đoạn thoại tiếp theo
    self.buffer.clear()

    if len(full_text) < 15:
      return ""

    try:
      response = requests.post(
          self.server_url, json={"text": full_text}, timeout=5
      )
      if response.status_code == 200:
        return response.json().get("summary", "Không có dữ liệu.")
      return f"Server báo lỗi: {response.status_code}"
    except Exception as e:
      return f"Lỗi kết nối Server AI: {e}"