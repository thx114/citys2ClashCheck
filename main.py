import tkinter as tk
from tkinter import scrolledtext
from tkinter import filedialog
import os
import yaml
import requests
import re
DEV_MODE = False

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
    更新本地对照表
    """
    
    if os.path.exists(local_file_path):
        local_size = os.path.getsize(local_file_path)
    else:
        local_size = 0
    
    print("正在下载对照表...")
    download_file(url, local_file_path)

# 读取YAML文件以获取比对对象
def load_yaml_rules(yaml_url):
    local_file_path = 'local_file.yaml'

    if not DEV_MODE:
        update_file_if_necessary(yaml_url, local_file_path)
    with open(local_file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def display_log_file(log_file_path, text_widget):
    # 设置日志显示背景为黑色
    text_widget.config(bg="black")
    
    # 配置不同类型的日志消息的颜色
    text_widget.tag_configure("INFO", foreground="white")
    text_widget.tag_configure("MESSAGE", foreground="light blue")
    text_widget.tag_configure("WARN", foreground="orange")
    text_widget.tag_configure("DEBUG", foreground="gray")
    text_widget.tag_configure("DEFAULT", foreground="gray")
    text_widget.tag_configure("ERROR", foreground="red")

    if os.path.exists(log_file_path):
        with open(log_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                # 根据行内容决定使用何种颜色
                if "[Info" in line:
                    text_widget.insert(tk.END, line, "INFO")
                elif "[Message" in line:
                    text_widget.insert(tk.END, line, "MESSAGE")
                elif "WARN" in line:
                    text_widget.insert(tk.END, line, "WARN")
                elif "[Debug" in line:
                    text_widget.insert(tk.END, line, "DEBUG")
                elif "[CRITICAL]" in line:
                    text_widget.insert(tk.END, line, "ERROR")
                elif "[FATAL]" in line:
                    text_widget.insert(tk.END, line, "ERROR")
                elif "[Error" in line:
                    text_widget.insert(tk.END, line, "ERROR")
                else:
                    text_widget.insert(tk.END, line, "DEFAULT")
    else:
        text_widget.insert(tk.END, "日志文件不存在。", "DEFAULT")


# 比对日志内容
def process_colored_text(text, result_widget):
    pattern = r"\$(\w+)(.*?)\$"
    matches = re.finditer(pattern, text, re.DOTALL)
    start = 0
    for match in matches:
        color, content = match.groups()
        end = match.start()
        # 先插入颜色标记之前的文本（如果有的话）
        if start < end:
            result_widget.insert(tk.END, text[start:end])
        # 配置颜色并插入颜色标记的文本
        result_widget.tag_configure(color, foreground=color)
        result_widget.insert(tk.END, content, color)
        start = match.end()
    # 插入最后一个颜色标记之后的文本（如果有的话）
    if start < len(text):
        result_widget.insert(tk.END, text[start:].replace('\\n','\n'))


def compare_log(rules, log_content, result_widget):
    
    for pattern, response in rules.items():
        # 将YAML中的【num】等占位符转换为正则表达式的捕获组
        matches = re.finditer(pattern, log_content)
        pathed = False
        for match in matches:
            if pathed:
                continue  
            # 从匹配对象中提取捕获组的值
            captured_values = match.groups()
            # 根据捕获的值替换响应字符串中的占位符
            formatted_response = response
            for i, value in enumerate(captured_values, start=1):
                formatted_response = formatted_response.replace(f"【value】", value)
            # 将替换后的响应字符串插入结果文本框
            result_widget.insert(tk.END, "· ")
            process_colored_text(formatted_response, result_widget)
            result_widget.insert(tk.END, "\n")
            pathed = True

# GUI设计
def create_gui():
    LOG_PATH = os.path.expandvars(r'%LocalAppData%Low\Colossal Order\Cities Skylines II\Player.log')
    YAML_URL = 'https://hub.gitmirror.com/https://raw.githubusercontent.com/thx114/citys2ClashCheck/main/test.yaml' # YAML文件路径
    
    rules = load_yaml_rules(YAML_URL)
    
    root = tk.Tk()
    root.title("citys2LogCheck")
    
    # 创建滚动文本区域显示日志文件
    log_display = scrolledtext.ScrolledText(root,  wrap=tk.WORD)
    log_display.pack(fill=tk.BOTH, expand=True)

    # 显示日志文件内容
    display_log_file(LOG_PATH, log_display)
    
    # 比对结果并显示
    result_display = scrolledtext.ScrolledText(root, width=100, height=10)
    result_display.pack()
    
    log_content = log_display.get("1.0", tk.END)
    compare_log(rules, log_content, result_display)

    def save_log():
        log_content = log_display.get("1.0", tk.END)
        result_content = result_display.get("1.0", tk.END)
        combined_content = log_content + "\n结果文本:\n" + result_content
        
        # 使用filedialog弹出保存文件对话框
        save_path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("All files", "*.*")],
            title="保存日志文件"
        )
        
        # 检查用户是否选择了文件名
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as file:
                file.write(combined_content)
            print("日志已保存到:", save_path)

    save_button = tk.Button(root, text="保存日志", command=save_log)
    save_button.pack()
    
    root.mainloop()

if __name__ == "__main__":
    create_gui()
