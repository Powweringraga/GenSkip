import ctypes
import os
from ctypes import wintypes

import pyautogui

# Keep the existing foreground input behavior.
pyautogui.PAUSE = 0.01
pyautogui.FAILSAFE = False


WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_MOUSEMOVE = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
VK_SPACE = 0x20
MK_LBUTTON = 0x0001


def _user32():
  if os.name != "nt":
    raise OSError("Background game input is only supported on Windows.")
  return ctypes.WinDLL("user32", use_last_error=True)


def _post_message(hwnd: int, message: int, wparam: int, lparam: int) -> None:
  user32 = _user32()
  post_message = user32.PostMessageW
  post_message.argtypes = [
      wintypes.HWND,
      wintypes.UINT,
      ctypes.c_size_t,
      ctypes.c_ssize_t,
  ]
  post_message.restype = wintypes.BOOL
  if not post_message(hwnd, message, wparam, lparam):
    raise ctypes.WinError(ctypes.get_last_error())


def _is_foreground(hwnd: int) -> bool:
  user32 = _user32()
  user32.GetForegroundWindow.restype = wintypes.HWND
  return user32.GetForegroundWindow() == hwnd


def human_press_f(hwnd: int | None = None) -> None:
  """Advance dialogue with Space, sending it to the game when it is in the background."""
  if hwnd is None or _is_foreground(hwnd):
    pyautogui.press("space")
    return

  user32 = _user32()
  user32.MapVirtualKeyW.argtypes = [wintypes.UINT, wintypes.UINT]
  user32.MapVirtualKeyW.restype = wintypes.UINT
  scan_code = user32.MapVirtualKeyW(VK_SPACE, 0)
  keydown_lparam = 1 | (scan_code << 16)
  keyup_lparam = keydown_lparam | (1 << 30) | (1 << 31)
  _post_message(hwnd, WM_KEYDOWN, VK_SPACE, keydown_lparam)
  _post_message(hwnd, WM_KEYUP, VK_SPACE, keyup_lparam)


def human_click(abs_x: int, abs_y: int, hwnd: int | None = None) -> None:
  """Click a game-client coordinate, using the foreground mouse only when focused."""
  x = int(abs_x)
  y = int(abs_y)
  if hwnd is None:
    pyautogui.click(x, y)
    return

  if _is_foreground(hwnd):
    user32 = _user32()
    user32.ClientToScreen.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.POINT)]
    user32.ClientToScreen.restype = wintypes.BOOL
    point = wintypes.POINT(x, y)
    if not user32.ClientToScreen(hwnd, ctypes.byref(point)):
      raise ctypes.WinError(ctypes.get_last_error())
    pyautogui.click(point.x, point.y)
    return

  if not 0 <= x <= 0xFFFF or not 0 <= y <= 0xFFFF:
    raise ValueError("Background click coordinates must be within the game client.")
  lparam = (y << 16) | x
  _post_message(hwnd, WM_MOUSEMOVE, 0, lparam)
  _post_message(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, lparam)
  _post_message(hwnd, WM_LBUTTONUP, 0, lparam)