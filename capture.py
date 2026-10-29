import ctypes
import os
from ctypes import wintypes

import mss
import numpy as np
from PIL import ImageGrab


class ScreenCapturer:
    def __init__(self):
        self.sct = mss.mss()

    @staticmethod
    def find_game_window():
        if os.name != "nt":
            raise OSError("Background game capture is only supported on Windows.")

        user32 = ctypes.WinDLL("user32", use_last_error=True)
        user32.IsWindowVisible.argtypes = [wintypes.HWND]
        user32.IsWindowVisible.restype = wintypes.BOOL
        user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
        user32.GetWindowTextLengthW.restype = ctypes.c_int
        user32.GetWindowTextW.argtypes = [
            wintypes.HWND,
            wintypes.LPWSTR,
            ctypes.c_int,
        ]
        user32.GetWindowTextW.restype = ctypes.c_int

        matches = []
        enum_windows_proc = ctypes.WINFUNCTYPE(
            wintypes.BOOL, wintypes.HWND, wintypes.LPARAM
        )

        def find_genshin_window(hwnd, _lparam):
            if not user32.IsWindowVisible(hwnd):
                return True

            title_length = user32.GetWindowTextLengthW(hwnd)
            if not title_length:
                return True

            title = ctypes.create_unicode_buffer(title_length + 1)
            user32.GetWindowTextW(hwnd, title, len(title))
            normalized_title = title.value.casefold().strip()
            if normalized_title in {"genshin impact", "原神"}:
                matches.append(hwnd)
            return True

        user32.EnumWindows.argtypes = [enum_windows_proc, wintypes.LPARAM]
        user32.EnumWindows.restype = wintypes.BOOL
        user32.EnumWindows(enum_windows_proc(find_genshin_window), 0)
        return int(matches[0]) if matches else None

    def grab_roi(self, monitor_region, hwnd=None):
        # monitor_region = {"top": 100, "left": 100, "width": 400, "height": 300}
        if hwnd is None:
            screenshot = self.sct.grab(monitor_region)
            img = np.array(screenshot)
            return img[:, :, :3]  # Keep BGR for OpenCV.

        screenshot = ImageGrab.grab(window=hwnd)
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        user32.GetWindowRect.argtypes = [
            wintypes.HWND,
            ctypes.POINTER(wintypes.RECT),
        ]
        user32.GetWindowRect.restype = wintypes.BOOL
        user32.GetClientRect.argtypes = [
            wintypes.HWND,
            ctypes.POINTER(wintypes.RECT),
        ]
        user32.GetClientRect.restype = wintypes.BOOL
        user32.ClientToScreen.argtypes = [
            wintypes.HWND,
            ctypes.POINTER(wintypes.POINT),
        ]
        user32.ClientToScreen.restype = wintypes.BOOL

        window_rect = wintypes.RECT()
        client_rect = wintypes.RECT()
        client_origin = wintypes.POINT()
        if (
            not user32.GetWindowRect(hwnd, ctypes.byref(window_rect))
            or not user32.GetClientRect(hwnd, ctypes.byref(client_rect))
            or not user32.ClientToScreen(hwnd, ctypes.byref(client_origin))
        ):
            raise ctypes.WinError(ctypes.get_last_error())

        client_width = client_rect.right - client_rect.left
        client_height = client_rect.bottom - client_rect.top
        window_width = window_rect.right - window_rect.left
        window_height = window_rect.bottom - window_rect.top
        if screenshot.size == (client_width, client_height):
            client_offset_x = 0
            client_offset_y = 0
        elif screenshot.size == (window_width, window_height):
            client_offset_x = client_origin.x - window_rect.left
            client_offset_y = client_origin.y - window_rect.top
        else:
            raise ValueError(
                "Captured Genshin window dimensions do not match its client area."
            )

        left = client_offset_x + int(monitor_region["left"])
        top = client_offset_y + int(monitor_region["top"])
        right = left + int(monitor_region["width"])
        bottom = top + int(monitor_region["height"])
        if (
            left < 0
            or top < 0
            or right > screenshot.width
            or bottom > screenshot.height
        ):
            raise ValueError(
                "Dialogue capture region is outside the Genshin window. "
                "Use the expected 1920x1080 game resolution."
            )

        cropped = screenshot.crop((left, top, right, bottom)).convert("RGB")
        return np.asarray(cropped)[:, :, ::-1].copy()