from ftplib import FTP
import os

# FTP 服务器配置
FTP_SERVER = "192.168.1.1"       # FTP 服务器地址
FTP_USER = "anonymous"           # 匿名用户模式
FTP_PASSWORD = ""                # 匿名无需密码

def upload_to_ftp(local_file, folder):
    """
    将截图上传到指定 FTP 文件夹

    参数:
        local_file (str): 本地文件路径，用来保存屏幕截图
        folder (str): FTP 服务器上的目标文件夹路径，用于指定截图在FTP服务器上的位置
    返回:
        None
    """
    try:
        # 连接 FTP 服务器
        ftp = FTP(FTP_SERVER)
        ftp.login(user=FTP_USER, passwd=FTP_PASSWORD)

        # 切换或创建目标文件夹
        try:
            ftp.cwd(folder)
        except:
            print(f"文件夹 {folder} 不存在，正在创建...")
            ftp.mkd(folder)
            ftp.cwd(folder)

        # 上传文件
        with open(local_file, "rb") as file:
            ftp.storbinary(f"STOR {os.path.basename(local_file)}", file)
        print(f"成功上传 {local_file} 到 {FTP_SERVER}/{folder}/")

        # 关闭 FTP 连接
        ftp.quit()

    except Exception as e:
        print(f"FTP 上传失败：{e}")



def check_ftp_connection(folder):
    """
    检测是否能连接到 FTP 服务器并切换到指定文件夹

    参数:
        folder (str): FTP 服务器上的目标文件夹路径

    返回:
        bool: 是否成功连接并切换到指定文件夹
    """
    try:
        ftp = FTP(FTP_SERVER)
        ftp.login(user=FTP_USER, passwd=FTP_PASSWORD)

        # 尝试切换到目标文件夹
        ftp.cwd(folder)
        ftp.quit()
        return True
    except Exception as e:
        print(f"FTP 连接失败：{e}")
        return False
