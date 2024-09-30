import re
import os


# 原始的print语句和注释
print("程序已经自动过滤了特殊协议和组播以及酒店源，支持http(s)/rts(m)p检测\n\n")
# 保留的分隔线
print("/" * 80)

# 保留原始的文件名输入部分
a = input('FileName(DragHere):')
#with open(a, 'r', encoding="utf-8") as f:#拖入文件操作

def filter_lines(file_path):
    with open(a, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    filtered_lines = []
    for line in lines:
        if ',' in line:
         if 'epg' not in line and 'mitv' not in line and 'udp' not in line and 'rtp' not in line and 'tsfile' not in line \
            and 'P2p' not in line and 'p2p' not in line and 'p3p' not in line and 'P2P' not in line and 'P3p' not in line and 'P3P' not in line:
          filtered_lines.append(line)
    
    return filtered_lines

def write_filtered_lines(output_file_path, filtered_lines):
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.writelines(filtered_lines)

if __name__ == "__main__":
    input_file_path = a
    output_file_path = "有效检测结果.txt"
    
    filtered_lines = filter_lines(input_file_path)
    write_filtered_lines(output_file_path, filtered_lines)

print("/" * 80)

# ###########################################定义替换规则的字典,对整行内的内容进行替换
replacements = {
        " ": "",
}

# 打开原始文件读取内容，并写入新文件
with open('有效检测结果.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 创建新文件并写入替换后的内容
with open('有效检测结果.txt', 'w', encoding='utf-8') as new_file:
    for line in lines:
        for old, new in replacements.items():
            line = line.replace(old, new)
        new_file.write(line)   


import requests
import time
import cv2
from urllib.parse import urlparse
from tqdm import tqdm

# 测试HTTP连接并尝试下载数据
def test_connectivity_and_download(url, initial_timeout=1, retry_timeout=1):
    parsed_url = urlparse(url)
    if parsed_url.scheme not in ['http', 'https']:
        # 非HTTP(s)协议，尝试RTSP检测
        return test_rtsp_connectivity(url, retry_timeout)
    else:
        # HTTP(s)协议，使用原始方法
        try:
            with requests.get(url, stream=True, timeout=initial_timeout) as response:
                if response.status_code == 200:
                    start_time = time.time()
                    while time.time() - start_time < initial_timeout:
                        chunk = response.raw.read(512)  # 尝试下载1KB数据
                        if chunk:
                            return True  # 成功下载数据
        except requests.RequestException as e:
            print(f"请求异常: {e}")
            pass #这行删掉则会在下载不到数据流的时候进行连通性测试

    return False  # 默认返回False

print("/" * 80)

# 测试RTSP连接并尝试读取流
def test_rtsp_connectivity(url, timeout=3):
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        return False
    start_time = time.time()
    while time.time() - start_time < timeout:
        ret, _ = cap.read()
        if ret:
            return True  # 成功读取帧
    cap.release()
    return False

# 主函数
def main(输入, 输出):
    with open(输入, "r", encoding="utf-8") as source_file:
        lines = source_file.readlines()

    results = []
    for line_number, line in enumerate(tqdm(lines, desc="检测中")):
        parts = line.strip().split(",")
        if len(parts) == 2 and parts[1]:  # 确保有URL，并且URL不为空
            channel_name, channel_url = parts
            try:
                is_valid = test_connectivity_and_download(channel_url)
            except Exception as e:
                print(f"检测URL {channel_url} 时发生错误: {e}")
                is_valid = False  # 将异常的URL视为无效

            status = "有效" if is_valid else "无效"

            if "genre" in line.lower() or status == "有效":
                results.append((channel_name.strip(), channel_url.strip(), status))

    # 写入文件
    with open(输出, "w", encoding="utf-8") as output_file:
        for channel_name, channel_url, status in results:
            output_file.write(f"{channel_name},{channel_url}\n")

    print(f"任务完成, 有效源数量: {len([x for x in results if x[2] == '有效'])}, 无效源数量: {len([x for x in results if x[2] == '无效'])}")

if __name__ == "__main__":
    输入 =  "有效检测结果.txt"    #input('请输入utf-8编码的直播源文件路径:')
    输出 = "有效检测结果.txt"
    main(输入, 输出)

print("/" * 80)

# ###########################################定义替换规则的字典,对整行内的内容进行替换
replacements = {
        ",None": "",
        " ": "",
        "\n\n": "",
}

# 打开原始文件读取内容，并写入新文件
with open('有效检测结果.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 创建新文件并写入替换后的内容
with open('有效检测结果.txt', 'w', encoding='utf-8') as new_file:
    for line in lines:
        for old, new in replacements.items():
            line = line.replace(old, new)
        new_file.write(line)    

# 等待用户输入，然后退出
print("/" * 80)

input("按任意键退出...")
