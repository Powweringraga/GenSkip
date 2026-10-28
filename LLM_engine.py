import requests


class GenSkipAI:

  def __init__(
      self, server_url: str = "https://genskipserver.vercel.app/api"
  ):
    # Chuẩn hóa URL Base
    url = server_url.rstrip("/")
    if not url.endswith("/api"):
      url += "/api"
    self.server_url = url

    # Bộ đệm lưu trữ hội thoại
    self.buffer = [
        "Paimon: Bọn mình đã đến thành phố Mondstadt rồi!",
        "Paimon: Hãy cùng đi gặp Jean ở Đội Kỵ Sĩ Tây Phong để hỏi tin tức nhé.",
    ]

  def extract_text(self, img_roi) -> str:
    """Thu thập thoại từ ảnh ROI (bổ sung OCR local nếu cần)."""
    text = ""  # Nếu có thư viện OCR, gán kết quả vào đây
    if text and text.strip():
      clean_text = text.strip()
      if not self.buffer or self.buffer[-1] != clean_text:
        self.buffer.append(clean_text)
        if len(self.buffer) > 20:
          self.buffer.pop(0)
    return text

  def select_best_choice(self, context: str, options: list[str]) -> int:
    """Gửi request chọn phương án thoại tối ưu."""
    if not options:
      return 1

    # Đảm bảo đường dẫn endpoint là /select_choice
    endpoint = f"{self.server_url}/select_choice"
    payload = {"context": context, "options": options}

    try:
      response = requests.post(endpoint, json=payload, timeout=6)
      if response.status_code == 200:
        return response.json().get("best_index", 1)
      print(
          f"[LLM Error] Status {response.status_code}: {response.text}"
      )
      return 1
    except Exception as e:
      print(f"[LLM Exception] {e}")
      return 1

  def summarize_buffered_lore(self) -> str:
    """Gửi toàn bộ bộ đệm hội thoại lên Server Proxy để tóm tắt."""
    if not self.buffer:
      return ""

    full_text = "\n".join(self.buffer)
    if len(full_text.strip()) < 10:
      return ""

    # Đảm bảo đường dẫn endpoint là /summarize
    endpoint = f"{self.server_url}/summarize"
    payload = {"text": full_text}

    try:
      response = requests.post(endpoint, json=payload, timeout=8)
      if response.status_code == 200:
        return response.json().get("summary", "Không có tóm tắt.")
      print(
          f"[LLM Summary Error] Status {response.status_code}:"
          f" {response.text}"
      )
      return f"Server báo lỗi: {response.status_code}"
    except Exception as e:
      print(f"[LLM Summary Exception] {e}")
      return f"Lỗi kết nối AI: {e}"