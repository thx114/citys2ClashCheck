import tkinter as tk
from tkinter import scrolledtext
import os
import yaml
import requests

def get_remote_file_size(url):
    """
    获取远程文件的大小
    """
    response = requests.head(url)
    size = response.headers.get('content-length', 0)
    return int(size)

def download_file(url, local_file_path):
    """
    下载文件
    """
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_file_path, 'wb') as file:
            file.write(response.content)
        print(f"文件已下载到 {local_file_path}")
    else:
        print("下载文件失败。")

def update_file_if_necessary(url, local_file_path):
    """
    如果需要，更新本地文件
    """
    remote_size = get_remote_file_size(url)
    
    if os.path.exists(local_file_path):
        local_size = os.path.getsize(local_file_path)
    else:
        local_size = 0
    
    if local_size != remote_size:
        print("本地文件不存在或大小不一致，正在下载更新...")
        download_file(url, local_file_path)
    else:
        print("本地文件存在且大小一致，无需下载。")

# 读取YAML文件以获取比对对象
def load_yaml_rules(yaml_url):
    local_file_path = 'local_file.yaml'

    update_file_if_necessary(yaml_url, local_file_path)
    with open(local_file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

# 读取并显示日志文件内容
def display_log_file(log_file_path, text_widget):
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r', encoding='utf-8') as file:
            text_widget.insert(tk.END, file.read())
    else:
        text_widget.insert(tk.END, "日志文件不存在。")

# 比对日志内容
def compare_log(rules, log_content):
    results = []
    for key, value in rules.items():
        if key in log_content:
            results.append(value)
    return results

# GUI设计
def create_gui():
    LOG_PATH = os.path.expandvars(r'%LocalAppData%Low\Colossal Order\Cities Skylines II\Player.log')
    YAML_URL = 'https://hub.gitmirror.com/https://raw.githubusercontent.com/thx114/citys2ClashCheck/main/test.yaml' # YAML文件路径
    
    rules = load_yaml_rules(YAML_URL)
    
    root = tk.Tk()
    root.title("日志文件阅读器")
    
    # 创建滚动文本区域显示日志文件
    log_display = scrolledtext.ScrolledText(root,  wrap=tk.WORD)
    log_display.pack(fill=tk.BOTH, expand=True)

    # 显示日志文件内容
    display_log_file(LOG_PATH, log_display)
    
    # 比对结果并显示
    log_content = log_display.get("1.0", tk.END)
    results = compare_log(rules, log_content)
    result_text = "\n".join(results)
    result_label = tk.Label(root, text=f"匹配结果:\n{result_text}")
    result_label.pack()
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()
