import os
import threading
from tkinter import Tk, Label, Entry, Button, filedialog, StringVar, messagebox
from upload import check_ftp_connection  # 导入 FTP 检测函数
from screenshot import start_listeners  # 从 screenshot.py 导入逻辑
import pystray
from PIL import Image, ImageDraw

# 初始化窗口
window = Tk()
window.title("Assistant")

# 创建变量来存储用户输入的信息
save_directory = StringVar()
ftp_folder = StringVar()

# 选择文件夹函数
def select_folder():
    """
    选择截图本地保存路径

    调用文件对话框让用户选择截图保存的目录，并将选择的目录设置到 save_directory 变量中。

    参数:
        无

    返回:
        无
    """
    folder = filedialog.askdirectory()
    if folder:
        save_directory.set(folder)

# 启动按钮点击事件
def on_submit():
    """
    启动按钮点击事件处理函数

    当用户点击启动按钮时，检查用户是否输入了所有必要的信息，然后检测 FTP 连接是否成功。
    如果连接成功，禁用启动按钮并更改其文本，然后启动一个新线程来运行监听器。

    参数:
        无

    返回:
        无
    """
    if not save_directory.get() or not ftp_folder.get():
        messagebox.showerror("error", "请填写所有信息！")
        return

    # 检测 FTP 连接
    folder_name = ftp_folder.get()
    if not check_ftp_connection(folder_name):
        messagebox.showerror("FTP Error", "无法连接到 FTP 服务器，请检查服务器信息。")
        return

    # 成功连接后禁用按钮并更改文本
    submit_button.config(text="程序运行中", state="disabled")

    # 启动监听器线程（保持 GUI 可见）
    local_save_path = save_directory.get()
    threading.Thread(
        target=start_listeners, args=(local_save_path, folder_name), daemon=True
    ).start()

# 显示窗口
def show_window(icon, item):
    """
    显示窗口

    当用户从托盘图标菜单中选择“显示窗口”时，调用此函数以显示主窗口。

    参数:
        icon (pystray.Icon): 托盘图标对象
        item (pystray.MenuItem): 被点击的菜单项

    返回:
        无
    """
    window.deiconify()

# 用户关闭窗口时隐藏到托盘
def on_close():
    """
    用户关闭窗口时隐藏到托盘

    当用户点击窗口的关闭按钮时，调用此函数以隐藏主窗口到托盘。

    参数:
        无

    返回:
        无
    """
    window.withdraw()

# 退出程序
def on_exit(icon, item):
    """
    退出程序

    当用户从托盘图标菜单中选择“退出”时，调用此函数以退出程序。

    参数:
        icon (pystray.Icon): 托盘图标对象
        item (pystray.MenuItem): 被点击的菜单项

    返回:
        无
    """
    icon.stop()
    window.quit()

# 创建托盘图标
def create_tray_icon():
    """
    创建托盘图标

    创建一个托盘图标，并设置其菜单选项为“显示窗口”和“退出”。

    参数:
        无

    返回:
        无
    """
    image = Image.new('RGB', (64, 64), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.text((10, 20), "Assistant", fill="black")

    icon = pystray.Icon("Screenshot App", image, "Assistant", menu=pystray.Menu(
        pystray.MenuItem("显示窗口", show_window),
        pystray.MenuItem("退出", on_exit)
    ))
    icon.run()

# 启动托盘图标线程
def start_tray_icon():
    """
    启动托盘图标线程

    启动一个新线程来运行托盘图标，以避免阻塞主 GUI 线程。

    参数:
        无

    返回:
        无
    """
    threading.Thread(target=create_tray_icon, daemon=True).start()

# 界面布局
Label(window, text="截图本地保存路径:").grid(row=0, column=0, padx=10, pady=5)
Entry(window, textvariable=save_directory).grid(row=0, column=1, padx=10, pady=5)
Button(window, text="选择", command=select_folder).grid(row=0, column=2, padx=10, pady=5)

Label(window, text="FTP服务器文件夹名称:").grid(row=1, column=0, padx=15, pady=5)
Entry(window, textvariable=ftp_folder).grid(row=1, column=1, padx=10, pady=5)

submit_button = Button(window, text="启动", command=on_submit)
submit_button.grid(row=2, column=1, pady=10)

# 用户点击 X 按钮时最小化到托盘
window.protocol("WM_DELETE_WINDOW", on_close)

if __name__ == "__main__":
    start_tray_icon()  # 启动托盘图标线程
    window.mainloop()
