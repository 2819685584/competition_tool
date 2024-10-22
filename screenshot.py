import pyautogui
import os
import time
from pynput import mouse, keyboard
from upload import upload_to_ftp

# 初始化计时和事件记录
mouse_click_times = []  # 鼠标点击时间记录
triple_click_time = None  # 记录三连击的开始时间
capslock_pressed = False  # Caps Lock 是否处于按压状态
screenshot_count = 1  # 截图计数
TIME_WINDOW = 2  # 时间窗口（秒）

def take_screenshot_and_upload(i, save_directory, ftp_folder):
    """截取屏幕并上传"""
    screenshot_path = os.path.join(save_directory, f"screenshot_{i}.png")
    screenshot = pyautogui.screenshot()
    screenshot.save(screenshot_path)
    print(f"截图保存为: {screenshot_path}")

    # 上传截图到 FTP 服务器
    upload_to_ftp(screenshot_path, ftp_folder)

def prune_old_events(event_times):
    """移除时间窗口外的事件"""
    current_time = time.time()
    event_times[:] = [t for t in event_times if current_time - t <= TIME_WINDOW]

def detect_trigger(event_times, min_events, max_events):
    """检测时间窗口内是否满足触发条件"""
    prune_old_events(event_times)
    return min_events <= len(event_times) <= max_events

def on_mouse_click(x, y, button, pressed, save_directory, ftp_folder):
    """鼠标点击事件"""
    global screenshot_count, triple_click_time, capslock_pressed

    current_time = time.time()

    if pressed:
        # 检测500ms内的三连击
        mouse_click_times.append(current_time)
        if len(mouse_click_times) >= 3 and current_time - mouse_click_times[-3] <= 0.5:
            triple_click_time = current_time  # 标记三连击的时间

        # 判断是否触发截图（Caps Lock 长按 + 鼠标单击）
        if capslock_pressed:
            take_screenshot_and_upload(screenshot_count, save_directory, ftp_folder)
            screenshot_count += 1
        elif triple_click_time and current_time - triple_click_time <= 2:
            # 三连击后2秒内单击满足6~9次的条件进行截图
            if detect_trigger(mouse_click_times, 6, 9):
                take_screenshot_and_upload(screenshot_count, save_directory, ftp_folder)
                screenshot_count += 1
                mouse_click_times.clear()  # 清空记录

def on_capslock_press(key):
    """Caps Lock 按键事件"""
    global capslock_pressed

    if key == keyboard.Key.caps_lock:
        capslock_pressed = True  # 标记 Caps Lock 被长按

def on_capslock_release(key):
    """Caps Lock 释放事件"""
    global capslock_pressed

    if key == keyboard.Key.caps_lock:
        capslock_pressed = False  # 取消长按标记

def start_listeners(save_directory, ftp_folder):
    """启动鼠标和键盘监听器"""
    print("监听鼠标和键盘中...")

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



