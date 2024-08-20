import os
import cv2
import time
from tqdm import tqdm
# 初始化字典
detected_ips = {}
def get_ip_key(url):
    """从URL中提取IP地址,并构造一个唯一的键"""
    start = url.find('://') + 3
    end = start
    dot_count = 0
    while dot_count < 3:
        end = url.find('.', end)
        if end == -1:
            break
        dot_count += 1
    return url[start:end] if dot_count == 3 else None
# 设置固定的文件夹路径
folder_path = 'playlist'
# 确保文件夹路径存在
if not os.path.isdir(folder_path):
    print("指定的文件夹不存在。")
    sys.exit()
# 遍历文件夹中的所有.txt文件
for filename in os.listdir(folder_path):
    if filename.endswith('.txt'):
        file_path = os.path.join(folder_path, filename)
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        # 准备写回文件
        with open(file_path, 'w', encoding='utf-8') as output_file:
            # 使用tqdm显示进度条
            for i, line in tqdm(enumerate(lines), total=len(lines), desc=f"Processing {filename}", unit='line'):
                if 'genre' in line:
                    output_file.write(line)
                    continue
                parts = line.split(',', 1)
                if len(parts) == 2:
                    channel_name, url = parts
                    channel_name = channel_name.strip()
                    url = url.strip()
                    ip_key = get_ip_key(url)
                    if ip_key in detected_ips and detected_ips[ip_key]['status'] == 'ok':
                        output_file.write(line)
                    elif ip_key:
                        # 尝试打开视频流
                        cap = cv2.VideoCapture(url)
                        start_time = time.time()
                        frame_count = 0
                        while frame_count < 200 and (time.time() - start_time) < 10:
                            ret, frame = cap.read()
                            if not ret:
                                break
                            frame_count += 1
                        cap.release()
                        if frame_count >= 200:
                            detected_ips[ip_key] = {'status': 'ok'}
                            output_file.write(line)
                        else:
                            detected_ips[ip_key] = {'status': 'fail'}
# 打印检测结果
for ip_key, result in detected_ips.items():
    print(f"IP Key: {ip_key}, Status: {result['status']}")
