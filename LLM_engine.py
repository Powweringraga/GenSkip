import requests
from vision import VisionEngine


class GenSkipAI:

  def __init__(
      self, server_url: str = "https://genskipserver.vercel.app"
  ):
    # Chuẩn hóa URL Base
    url = server_url.strip().rstrip("/")
    if url.endswith("/api"):
      url = url[:-4]
    self.server_url = url

    self.buffer = []
    self._last_dialogue = ""
    self._candidate_dialogue = ""
    self._candidate_frames = 0
    self._last_summary_input = ""

  def extract_text(self, img_roi) -> str:
    """OCR visible dialogue and buffer it after the text stabilizes."""
    text = VisionEngine.extract_dialogue_text(img_roi).strip()
    normalized_text = " ".join(text.casefold().split())
    if not normalized_text:
      self._candidate_dialogue = ""
      self._candidate_frames = 0
      return ""

    if normalized_text == self._last_dialogue:
      return text

    if normalized_text == self._candidate_dialogue:
      self._candidate_frames += 1
    else:
      self._candidate_dialogue = normalized_text
      self._candidate_frames = 1

    if self._candidate_frames >= 2:
      self.buffer.append(text)
      self.buffer = self.buffer[-40:]
      self._last_dialogue = normalized_text
      self._candidate_dialogue = ""
      self._candidate_frames = 0
    return text

  def select_best_choice(self, context: str, options: list[str]) -> int:
    """Ask the proxy to choose a quest- and character-consistent response."""
    if not options:
      return 1

    endpoint = f"{self.server_url}/select_choice"
    prompt_context = (
        "Use the recent Genshin Impact quest dialogue to choose the option "
        "that best fits the Traveler's character and the current quest. "
        "Prefer a meaningful, helpful response over a joke or an unrelated "
        "reply. Return a 1-based option index.\n\n"
        f"Recent dialogue:\n{context}"
    )
    response = requests.post(
        endpoint,
        json={"context": prompt_context, "options": options},
        timeout=6,
    )
    response.raise_for_status()
    result = response.json()
    if not isinstance(result, dict):
      raise ValueError("Choice service returned an invalid response.")
    best_index = result.get("best_index")
    if (
        not isinstance(best_index, int)
        or isinstance(best_index, bool)
        or not 1 <= best_index <= len(options)
    ):
      raise ValueError("Choice service returned an out-of-range option index.")
    return best_index

  def summarize_buffered_lore(self) -> str:
    """Summarize newly captured dialogue in the context of the active quest."""
    if not self.buffer:
      return ""

    dialogue = "\n".join(self.buffer)
    if len(dialogue.strip()) < 10 or dialogue == self._last_summary_input:
      return ""

    endpoint = f"{self.server_url}/summarize"
    try:
      response = requests.post(
          endpoint,
          json={
              "text": (
                  "Summarize this current Genshin Impact quest scene for the "
                  "player. Identify the characters, what has happened, the "
                  "current objective or decision, and any important lore. "
                  "Use only the dialogue below and do not invent details.\n\n"
                  f"{dialogue}"
              )
          },
          timeout=8,
      )
      response.raise_for_status()
      result = response.json()
      if not isinstance(result, dict) or not isinstance(
          result.get("summary"), str
      ):
        raise ValueError("Summary service returned an invalid response.")
      self._last_summary_input = dialogue
      return result["summary"]
    except (requests.RequestException, ValueError) as error:
      if isinstance(error, requests.HTTPError) and error.response is not None:
        detail = error.response.text.strip()
        if detail:
          return (
              f"AI summary unavailable ({error.response.status_code}): "
              f"{detail[:500]}"
          )
      return f"AI summary unavailable: {error}"