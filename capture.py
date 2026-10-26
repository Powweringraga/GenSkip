import mss
import numpy as np

class ScreenCapturer:
    def __init__(self):
        self.sct = mss.mss()

    def grab_roi(self, monitor_region):
        # monitor_region = {"top": 100, "left": 100, "width": 400, "height": 300}
        screenshot = self.sct.grab(monitor_region)
        img = np.array(screenshot)
        return img[:, :, :3]  # Loại bỏ kênh Alpha, giữ lại BGR cho OpenCV