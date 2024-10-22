import pyautogui
import os
import time
from pynput import mouse, keyboard
from upload import upload_to_ftp

# 初始化状态和事件记录
capslock_pressed = False  # Caps Lock 是否按压状态
screenshot_count = 1  # 截图计数
TIME_WINDOW = 2  # 时间窗口（秒）
wheel_click_times = []  # 存储鼠标滚轮单击事件时间

def take_screenshot_and_upload(i, save_directory, ftp_folder):
    """
    截取屏幕并上传

    参数:
    i (int): 截图的序号
    save_directory (str): 保存截图的目录
    ftp_folder (str): FTP 服务器上的文件夹

    返回:
    None
    """
    screenshot_path = os.path.join(save_directory, f"screenshot_{i}.png")
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_path)
    print(f"截图保存为: {screenshot_path}")

    # 上传截图到 FTP 服务器
    upload_to_ftp(screenshot_path, ftp_folder)

def prune_old_events(event_times):
    """
    移除时间窗口外的事件

    参数:
    event_times (list): 事件发生的时间列表

    返回:
    None
    """
    current_time = time.time()
    event_times[:] = [t for t in event_times if current_time - t <= TIME_WINDOW]

def detect_trigger(event_times, required_events):
    """
    检测时间窗口内是否满足触发条件

    参数:
    event_times (list): 事件发生的时间列表
    required_events (int): 触发所需的事件数量

    返回:
    bool: 是否满足触发条件
    """
    prune_old_events(event_times)
    return len(event_times) >= required_events

def on_mouse_click(x, y, button, pressed, save_directory, ftp_folder):
    """
    鼠标点击事件处理

    参数:
    x (int): 鼠标点击的 x 坐标
    y (int): 鼠标点击的 y 坐标
    button (mouse.Button): 点击的鼠标按钮
    pressed (bool): 是否按下鼠标按钮
    save_directory (str): 保存截图的目录
    ftp_folder (str): FTP 服务器上的文件夹

    返回:
    None
    """
    global screenshot_count

    if pressed:
        current_time = time.time()

        # 检测 Caps Lock 长按 + 鼠标单击
        if capslock_pressed and button == mouse.Button.left:
            take_screenshot_and_upload(screenshot_count, save_directory, ftp_folder)
            screenshot_count += 1

        # 检测 2 秒内单击 4 次滚轮
        elif button == mouse.Button.middle:
            wheel_click_times.append(current_time)
            if detect_trigger(wheel_click_times, 4):
                take_screenshot_and_upload(screenshot_count, save_directory, ftp_folder)
                screenshot_count += 1
                wheel_click_times.clear()  # 清空滚轮单击记录

def on_capslock_press(key):
    """
    Caps Lock 按键按下事件

    参数:
    key (keyboard.Key): 按下的按键

    返回:
    None
    """
    global capslock_pressed
    if key == keyboard.Key.caps_lock:
        capslock_pressed = True

def on_capslock_release(key):
    """
    Caps Lock 按键释放事件

    参数:
    key (keyboard.Key): 释放的按键

    返回:
    None
    """
    global capslock_pressed
    if key == keyboard.Key.caps_lock:
        capslock_pressed = False

def start_listeners(save_directory, ftp_folder):
    """
    启动鼠标和键盘监听器

    参数:
    save_directory (str): 保存截图的目录
    ftp_folder (str): FTP 服务器上的文件夹

    返回:
    None
    """
    print("监听鼠标和键盘中...")

    # 启动鼠标和键盘监听器
    mouse_listener = mouse.Listener(
        on_click=lambda x, y, button, pressed: on_mouse_click(
            x, y, button, pressed, save_directory, ftp_folder
        )
    )
    keyboard_listener = keyboard.Listener(
        on_press=on_capslock_press,
        on_release=on_capslock_release
    )

    mouse_listener.start()
    keyboard_listener.start()

    mouse_listener.join()
    keyboard_listener.join()
