import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime
import os
from urllib.parse import urlparse
import socket
import subprocess

# 当前日期
timestart = datetime.now()

################################################ 读取文件内容
def read_txt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return lines

################################################# 检测 URL 是否可访问并记录响应时间
def check_url(url, timeout=6):
    start_time = time.time()
    elapsed_time = None
    success = False
    try:
        if url.startswith("http"):
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    success = True
        elif url.startswith("p3p"):
            success = check_p3p_url(url, timeout)
        elif url.startswith("p2p"):
            success = check_p2p_url(url, timeout)
        elif url.startswith("rtmp") or url.startswith("rtsp"):
            success = check_rtmp_url(url, timeout)
        elif url.startswith("rtp"):
            success = check_rtp_url(url, timeout)
        elapsed_time = (time.time() - start_time) * 1000
    except Exception as e:
        print(f"Error checking {url}: {e}")
        elapsed_time = None
    return elapsed_time, success

################################################
def check_rtmp_url(url, timeout):
    try:
        result = subprocess.run(['ffprobe', url], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        if result.returncode == 0:
            return True
    except subprocess.TimeoutExpired:
        print(f"Timeout checking {url}")
    except Exception as e:
        print(f"Error checking {url}: {e}")
    return False

################################################
def check_rtp_url(url, timeout):
    try:
        parsed_url = urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port
        with socket.socket(socket.AF_INET, socket.SOCK_DUDP) as s:
            s.settimeout(timeout)
            s.connect((host, port))
            s.sendto(b'', (host, port))
            s.recv(1)
        return True
    except (socket.timeout, socket.error):
        return False

################################################
def check_p3p_url(url, timeout):
    try:
        parsed_url = urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port
        path = parsed_url.path
        if not host or not port or not path:
            raise ValueError("Invalid p3p URL")
        with socket.create_connection((host, port), timeout=timeout) as s:
            request = f"GET {path} P3P/1.0\r\nHost: {host}\r\n\r\n"
            s.sendall(request.encode())
            response = s.recv(1024)
            if b"P3P" in response:
                return True
    except Exception as e:
        print(f"Error checking {url}: {e}")
    return False

################################################
def check_p2p_url(url, timeout):
    try:
        parsed_url = urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port
        path = parsed_url.path
        if not host or not port or not path:
            raise ValueError("Invalid P2P URL")
        with socket.create_connection((host, port), timeout=timeout) as s:
            request = f"YOUR_CUSTOM_REQUEST {path}\r\nHost: {host}\r\n\r\n"
            s.sendall(request.encode())
            response = s.recv(1024)
            if b"SOME_EXPECTED_RESPONSE" in response:
                return True
    except Exception as e:
        print(f"Error checking {url}: {e}")
    return False

################################################# 处理单行文本并检测URL
def process_line(line):
    if "#genre#" in line:
        return line.strip()
    parts = line.split(',')
    if len(parts) == 2:
        name, url = parts
        elapsed_time, is_valid = check_url(url.strip())
        if is_valid:
            return line.strip()  # 修改这里，输出原始行
    return None

################################################# 多线程处理文本并检测URL
def process_urls_multithreaded(lines, max_workers=30):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_line, line): line for line in lines}
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
    return results

################################################# 写入文件
def write_list(file_path, data_list):
    with open(file_path, 'w', encoding='utf-8') as file:
        for item in data_list:
            file.write(item + '\n')

if __name__ == "__main__":
    input_file_path = "y.txt"  # 替换为你的输入文件路径
    output_file_path = "y.txt"  # 替换为你的输出文件路径
    lines = read_txt_file(input_file_path)
    results = process_urls_multithreaded(lines)
    write_list(output_file_path, results)
