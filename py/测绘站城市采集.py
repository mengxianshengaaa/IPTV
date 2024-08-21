import requests
import re
import cv2  # 导入OpenCV库


#本段代码更新文件方式-----追加写入
#同省份多城市查询IP

# 更新四川电信组播定义fofa链接列表   #///////////////////////////////////////
fofa_urls = [
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJjaGVuZ2R1Ig%3D%3D',   # 成都   #///////////////////////////////////////
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJYaWNoYW5nIg%3D%3D',   # 西昌
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJtaWFueWFuZyI%3D',  # 绵阳
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJsdXpob3Ui',  # 泸州
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJkYXpob3Ui',  # 达州
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJuYW5jaG9uZyI%3D'  # 南充
]

# 尝试从fofa链接提取IP地址和端口号，并去除重复项
def extract_unique_ip_ports(fofa_urls):
    all_unique_ips_ports = set()
    for fofa_url in fofa_urls:
        try:
            response = requests.get(fofa_url, timeout=10)
            html_content = response.text
            # 使用正则表达式匹配IP地址和端口号
            ips_ports = re.findall(r'(\d+\.\d+\.\d+\.\d+:\d+)', html_content)
            all_unique_ips_ports.update(ips_ports)  # 将IP和端口号添加到集合中
        except requests.RequestException as e:
            print(f"请求 {fofa_url} 时发生错误: {e}")
    return list(all_unique_ips_ports)
# 检查视频流的可达性
def check_video_stream_connectivity(ip_port, urls_udp):
    video_url = f"http://{ip_port}{urls_udp}"
    cap = cv2.VideoCapture(video_url)
    if cap.isOpened():
        cap.release()
        return ip_port  # 如果打开成功，返回IP和端口号
    else:
        cap.release()
        return None
# 从本地文件读取内容
def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
    return None
# 更新文件中的IP地址并将每个IP追加写入
def update_and_write_ips(file_path, valid_ips_ports):
    try:
        original_content = read_file_content(file_path)
        if original_content:
            # 假设原文件中的IP地址格式为 http://IP:PORT
            ip_port_pattern = r'http://(\d+\.\d+\.\d+:\d+)'
            new_lines = []
            for line in original_content.splitlines():
                match = re.search(ip_port_pattern, line)
                if match:
                    # 找到一个IP地址，替换为有效的IP地址列表
                    for valid_ip_port in valid_ips_ports:
                        new_line = re.sub(ip_port_pattern, f'http://{valid_ip_port}', line)
                        new_lines.append(new_line)
            # 将更新后的内容追加到文件末尾
            with open(file_path, 'a', encoding='utf-8') as file:
                file.write("\n".join(new_lines) + "\n")
            print(f"文件 {file_path} 已更新并追加保存。")
    except Exception as e:
        print(f"更新文件 {file_path} 时发生错误: {e}")
# 定义组播地址和端口
urls_udp = "/rtp/239.93.0.58:5140"   #///////////////////////////////////////
# 提取唯一的IP地址和端口号
unique_ips_ports = extract_unique_ip_ports(fofa_urls)
# 存储所有有效的IP地址和端口号
valid_ips_ports = [ip_port for ip_port in unique_ips_ports if check_video_stream_connectivity(ip_port, urls_udp)]
if valid_ips_ports:
    print("找到的可访问视频流服务的IP地址和端口号：")
    for valid_ip_port in valid_ips_ports:
        print(valid_ip_port)
    # 指定需要更新的本地文件路径
    local_file_path = 'playlist/四川电信.txt'   #///////////////////////////////////////
    # 更新文件中的IP地址并将每个IP写入新行
    update_and_write_ips(local_file_path, valid_ips_ports)
else:
    print("没有找到可访问的视频流服务或者没有提取到IP地址和端口号。")




# 更新湖北电信组播定义fofa链接列表   #///////////////////////////////////////
fofa_urls = [
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJ3dWhhbiI%3D',   # 武汉   #///////////////////////////////////////
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJodWFuZ3NoaSI%3D',   # 黄石
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJ4aWFuZ3lhbmci',  # 襄阳
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJqaW5nemhvdSI%3D',  # 荆州
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJodWFuZ2dhbmci',  # 黄冈
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJ4aWFvZ2FuIg%3D%3D',  # 孝感
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJKaW5nbWVuIg%3D%3D',  # 荆门
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJ4aWFubmluZyI%3D'  # 咸宁
]

# 尝试从fofa链接提取IP地址和端口号，并去除重复项
def extract_unique_ip_ports(fofa_urls):
    all_unique_ips_ports = set()
    for fofa_url in fofa_urls:
        try:
            response = requests.get(fofa_url, timeout=10)
            html_content = response.text
            # 使用正则表达式匹配IP地址和端口号
            ips_ports = re.findall(r'(\d+\.\d+\.\d+\.\d+:\d+)', html_content)
            all_unique_ips_ports.update(ips_ports)  # 将IP和端口号添加到集合中
        except requests.RequestException as e:
            print(f"请求 {fofa_url} 时发生错误: {e}")
    return list(all_unique_ips_ports)
# 检查视频流的可达性
def check_video_stream_connectivity(ip_port, urls_udp):
    video_url = f"http://{ip_port}{urls_udp}"
    cap = cv2.VideoCapture(video_url)
    if cap.isOpened():
        cap.release()
        return ip_port  # 如果打开成功，返回IP和端口号
    else:
        cap.release()
        return None
# 从本地文件读取内容
def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
    return None
# 更新文件中的IP地址并将每个IP追加写入
def update_and_write_ips(file_path, valid_ips_ports):
    try:
        original_content = read_file_content(file_path)
        if original_content:
            # 假设原文件中的IP地址格式为 http://IP:PORT
            ip_port_pattern = r'http://(\d+\.\d+\.\d+:\d+)'
            new_lines = []
            for line in original_content.splitlines():
                match = re.search(ip_port_pattern, line)
                if match:
                    # 找到一个IP地址，替换为有效的IP地址列表
                    for valid_ip_port in valid_ips_ports:
                        new_line = re.sub(ip_port_pattern, f'http://{valid_ip_port}', line)
                        new_lines.append(new_line)
            # 将更新后的内容追加到文件末尾
            with open(file_path, 'a', encoding='utf-8') as file:
                file.write("\n".join(new_lines) + "\n")
            print(f"文件 {file_path} 已更新并追加保存。")
    except Exception as e:
        print(f"更新文件 {file_path} 时发生错误: {e}")
# 定义组播地址和端口
urls_udp = "/rtp/239.254.96.96:8550"   #///////////////////////////////////////
# 提取唯一的IP地址和端口号
unique_ips_ports = extract_unique_ip_ports(fofa_urls)
# 存储所有有效的IP地址和端口号
valid_ips_ports = [ip_port for ip_port in unique_ips_ports if check_video_stream_connectivity(ip_port, urls_udp)]
if valid_ips_ports:
    print("找到的可访问视频流服务的IP地址和端口号：")
    for valid_ip_port in valid_ips_ports:
        print(valid_ip_port)
    # 指定需要更新的本地文件路径
    local_file_path = 'playlist/湖北电信.txt'   #///////////////////////////////////////
    # 更新文件中的IP地址并将每个IP写入新行
    update_and_write_ips(local_file_path, valid_ips_ports)
else:
    print("没有找到可访问的视频流服务或者没有提取到IP地址和端口号。")



# 更新北京联通组播定义fofa链接列表//////////////////////////////////////////////////////////////
fofa_urls = [
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiByZWdpb249ImJlaWppbmci'   # 北京
]

# 尝试从fofa链接提取IP地址和端口号，并去除重复项
def extract_unique_ip_ports(fofa_urls):
    all_unique_ips_ports = set()
    for fofa_url in fofa_urls:
        try:
            response = requests.get(fofa_url, timeout=10)
            html_content = response.text
            # 使用正则表达式匹配IP地址和端口号
            ips_ports = re.findall(r'(\d+\.\d+\.\d+\.\d+:\d+)', html_content)
            all_unique_ips_ports.update(ips_ports)  # 将IP和端口号添加到集合中
        except requests.RequestException as e:
            print(f"请求 {fofa_url} 时发生错误: {e}")
    return list(all_unique_ips_ports)
# 检查视频流的可达性
def check_video_stream_connectivity(ip_port, urls_udp):
    video_url = f"http://{ip_port}{urls_udp}"
    cap = cv2.VideoCapture(video_url)
    if cap.isOpened():
        cap.release()
        return ip_port  # 如果打开成功，返回IP和端口号
    else:
        cap.release()
        return None
# 从本地文件读取内容
def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
    return None
# 更新文件中的IP地址并将每个IP追加写入
def update_and_write_ips(file_path, valid_ips_ports):
    try:
        original_content = read_file_content(file_path)
        if original_content:
            # 假设原文件中的IP地址格式为 http://IP:PORT
            ip_port_pattern = r'http://(\d+\.\d+\.\d+:\d+)'
            new_lines = []
            for line in original_content.splitlines():
                match = re.search(ip_port_pattern, line)
                if match:
                    # 找到一个IP地址，替换为有效的IP地址列表
                    for valid_ip_port in valid_ips_ports:
                        new_line = re.sub(ip_port_pattern, f'http://{valid_ip_port}', line)
                        new_lines.append(new_line)
            # 将更新后的内容追加到文件末尾
            with open(file_path, 'a', encoding='utf-8') as file:
                file.write("\n".join(new_lines) + "\n")
            print(f"文件 {file_path} 已更新并追加保存。")
    except Exception as e:
        print(f"更新文件 {file_path} 时发生错误: {e}")
# 定义组播地址和端口
urls_udp = "/rtp/239.3.1.129:8008"   #/////////////////////////////////////////////////////////
# 提取唯一的IP地址和端口号
unique_ips_ports = extract_unique_ip_ports(fofa_urls)
# 存储所有有效的IP地址和端口号
valid_ips_ports = [ip_port for ip_port in unique_ips_ports if check_video_stream_connectivity(ip_port, urls_udp)]
if valid_ips_ports:
    print("找到的可访问视频流服务的IP地址和端口号：")
    for valid_ip_port in valid_ips_ports:
        print(valid_ip_port)
    # 指定需要更新的本地文件路径
    local_file_path = 'playlist/北京联通.txt'   #///////////////////////////////////////
    # 更新文件中的IP地址并将每个IP写入新行
    update_and_write_ips(local_file_path, valid_ips_ports)
else:
    print("没有找到可访问的视频流服务或者没有提取到IP地址和端口号。")





# 更新江苏电信组播定义fofa链接列表   #///////////////////////////////////////
fofa_urls = [
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiByZWdpb249IkppYW5nc3UiICYmIGNpdHk9InN1emhvdSI%3D',   # 苏州   #///////////////////////////////////////
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiByZWdpb249IkppYW5nc3UiICYmIGNpdHk9Im5hbmppbmci',   # nanjing
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiByZWdpb249IkppYW5nc3UiICYmIGNpdHk9Im5hbnRvbmci',  # 南通
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiByZWdpb249IkppYW5nc3UiICYmIGNpdHk9Inlhbmd6aG91Ig%3D%3D',  # 扬州
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiByZWdpb249IkppYW5nc3UiICYmIGNpdHk9ImNoYW5nemhvdSI=',  # 常州
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiByZWdpb249IkppYW5nc3UiICYmIGNpdHk9Ind1eGki',  # 无锡
    'InVkcHh5IiAmJiByZWdpb249IkppYW5nc3UiICYmIGNpdHk9Inh1emhvdSI='  # 徐州
]

# 尝试从fofa链接提取IP地址和端口号，并去除重复项
def extract_unique_ip_ports(fofa_urls):
    all_unique_ips_ports = set()
    for fofa_url in fofa_urls:
        try:
            response = requests.get(fofa_url, timeout=10)
            html_content = response.text
            # 使用正则表达式匹配IP地址和端口号
            ips_ports = re.findall(r'(\d+\.\d+\.\d+\.\d+:\d+)', html_content)
            all_unique_ips_ports.update(ips_ports)  # 将IP和端口号添加到集合中
        except requests.RequestException as e:
            print(f"请求 {fofa_url} 时发生错误: {e}")
    return list(all_unique_ips_ports)
# 检查视频流的可达性
def check_video_stream_connectivity(ip_port, urls_udp):
    video_url = f"http://{ip_port}{urls_udp}"
    cap = cv2.VideoCapture(video_url)
    if cap.isOpened():
        cap.release()
        return ip_port  # 如果打开成功，返回IP和端口号
    else:
        cap.release()
        return None
# 从本地文件读取内容
def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
    return None
# 更新文件中的IP地址并将每个IP追加写入
def update_and_write_ips(file_path, valid_ips_ports):
    try:
        original_content = read_file_content(file_path)
        if original_content:
            # 假设原文件中的IP地址格式为 http://IP:PORT
            ip_port_pattern = r'http://(\d+\.\d+\.\d+:\d+)'
            new_lines = []
            for line in original_content.splitlines():
                match = re.search(ip_port_pattern, line)
                if match:
                    # 找到一个IP地址，替换为有效的IP地址列表
                    for valid_ip_port in valid_ips_ports:
                        new_line = re.sub(ip_port_pattern, f'http://{valid_ip_port}', line)
                        new_lines.append(new_line)
            # 将更新后的内容追加到文件末尾
            with open(file_path, 'a', encoding='utf-8') as file:
                file.write("\n".join(new_lines) + "\n")
            print(f"文件 {file_path} 已更新并追加保存。")
    except Exception as e:
        print(f"更新文件 {file_path} 时发生错误: {e}")
# 定义组播地址和端口
urls_udp = "/rtp/239.49.8.19:9614"   #///////////////////////////////////////
# 提取唯一的IP地址和端口号
unique_ips_ports = extract_unique_ip_ports(fofa_urls)
# 存储所有有效的IP地址和端口号
valid_ips_ports = [ip_port for ip_port in unique_ips_ports if check_video_stream_connectivity(ip_port, urls_udp)]
if valid_ips_ports:
    print("找到的可访问视频流服务的IP地址和端口号：")
    for valid_ip_port in valid_ips_ports:
        print(valid_ip_port)
    # 指定需要更新的本地文件路径
    local_file_path = 'playlist/江苏电信.txt'   #///////////////////////////////////////
    # 更新文件中的IP地址并将每个IP写入新行
    update_and_write_ips(local_file_path, valid_ips_ports)
else:
    print("没有找到可访问的视频流服务或者没有提取到IP地址和端口号。")


###############检测playlist文件夹内所有txt文件内的组播
###############检测playlist文件夹内所有txt文件内的组播
###############检测playlist文件夹内所有txt文件内的组播

import os
import cv2
import time
from tqdm import tqdm
import sys

# 初始化字典以存储IP检测结果
detected_ips = {}

def get_ip_key(url):
    """从URL中提取IP地址，并构造一个唯一的键"""
    start = url.find('://') + 3
    end = url.find('/', start)
    if end == -1:
        end = len(url)
    return url[start:end].strip()

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
            # 使用 tqdm 显示进度条
            for line in tqdm(lines, total=len(lines), desc=f"Processing {filename}"):
                parts = line.split(',', 1)
                if len(parts) >= 2:
                    channel_name, url = parts
                    channel_name = channel_name.strip()
                    url = url.strip()
                    ip_key = get_ip_key(url)
                    
                    # 检查IP是否已经被检测过
                    if ip_key in detected_ips:
                        # 如果之前检测成功，则写入该行
                        if detected_ips[ip_key]['status'] == 'ok':
                            output_file.write(line)
                        continue  # 无论之前检测结果如何，都不重新检测
                    
                    # 初始化帧计数器和成功标志
                    frame_count = 0
                    success = False
                    # 尝试打开视频流
                    cap = cv2.VideoCapture(url)
                    start_time = time.time()
                    while (time.time() - start_time) < 5:
                        ret, frame = cap.read()
                        if not ret:
                            break
                        frame_count += 1
                        # 如果在3秒内读取到60帧以上，设置成功标志
                        if frame_count >= 5:
                            success = True
                            break
                    cap.release()
                    
                    # 根据检测结果更新字典
                    if success:
                        detected_ips[ip_key] = {'status': 'ok'}
                        output_file.write(line)
                    else:
                        detected_ips[ip_key] = {'status': 'fail'}

# 打印检测结果
for ip_key, result in detected_ips.items():
    print(f"IP Key: {ip_key}, Status: {result['status']}")
