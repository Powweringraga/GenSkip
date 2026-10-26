import pydirectinput
import time
import random

def human_click(x, y):
    # Lệch tọa độ ngẫu nhiên ±3 pixel
    rand_x = x + random.randint(-3, 3)
    rand_y = y + random.randint(-3, 3)
    
    pydirectinput.moveTo(rand_x, rand_y)
    time.sleep(random.uniform(0.05, 0.12))
    pydirectinput.click()

def human_press_f():
    pydirectinput.keyDown('f')
    time.sleep(random.uniform(0.08, 0.15))
    pydirectinput.keyUp('f')