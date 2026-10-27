import cv2
from PIL import Image
import pytesseract
import requests


class GenSkipAI:

  def __init__(
      self, server_url: str = "https://genskip-server.onrender.com/summarize"
  ):
    # Đường dẫn Server Proxy chính xác tới endpoint FastAPI
    self.server_url = server_url

  def extract_text(self, img_bgr) -> str:
    """Đọc chữ từ ảnh ROI bằng Pytesseract"""
    try:
      img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
      pil_img = Image.fromarray(img_rgb)
      text = pytesseract.image_to_string(pil_img, lang="eng")
      return text.strip()
    except Exception as e:
      print(f"[OCR Error] {e}")
      return ""

  def summarize_lore(self, text: str) -> str:
    """Gửi văn bản đến Server Proxy để tóm tắt mà không cần API Key ở Client"""
    if not text or len(text) < 10:
      return "Không tìm thấy đoạn thoại đủ dài để tóm tắt."

    try:
      response = requests.post(
          self.server_url, json={"text": text}, timeout=5
      )
      if response.status_code == 200:
        return response.json().get("summary", "Không có dữ liệu.")
      return f"Server báo lỗi: {response.status_code}"
    except Exception as e:
      return f"Lỗi kết nối Server AI: {e}"