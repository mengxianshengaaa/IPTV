# 导入必要的模块
import time
import urllib.request
import re
from urllib.error import URLError, HTTPError
import ffmpeg

# 读取文本文件到数组的函数
def read_txt_to_array(file_name):
    try:
        # 打开并读取文件，去除每行的前后空白字符
        with open(file_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            lines = [line.strip() for line in lines]
            return lines
    except FileNotFoundError:
        # 如果文件不存在，打印错误信息
        print(f"File '{file_name}' not found.")
        return []
    except Exception as e:
        # 其他异常情况，打印错误信息
        print(f"An error occurred: {e}")
        return []

# 检测URL是否可访问并记录响应时间的函数
def check_url(url, timeout=6):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    elapsed_time = None
    status_ok = False
    # resolution = None  # 保留分辨率变量，但当前不使用

    try:
        if "://" in url:
            # 记录请求开始时间
            start_time = time.time()
            req = urllib.request.Request(url, headers=headers)
            # 发送请求并接收响应
            with urllib.request.urlopen(req, timeout=timeout) as response:
                elapsed_time = (time.time() - start_time) * 1000  # 转换为毫秒
                if response.status == 200:
                    status_ok = True
                    # 尝试获取视频分辨率
                    resolution = get_video_resolution(url)
    except HTTPError as e:
        # 打印HTTP错误信息
        print(f"HTTP Error: {e.code} - {e.reason},{url}")
    except URLError as e:
        # 打印URL错误信息
        print(f"URL Error: {e.reason},{url}")
    except Exception as e:
        # 打印其他错误信息
        print(f"Error checking url: {e},{url}")

    return elapsed_time, status_ok, resolution  # 返回响应时间、状态和分辨率

# 使用ffmpeg获取视频分辨率的函数
def get_video_resolution(url):
    try:
        probe = ffmpeg.probe(url)
        video_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'video']
        if video_streams:
            width = video_streams[0]['width']
            height = video_streams[0]['height']
            return f'{width}x{height}'
    except Exception as e:
        # 打印获取分辨率时的错误信息
        print(f"Error getting resolution: {e},{url}")
    return None

# 处理单行文本并检测URL的函数
def process_line(line):
    if "#genre#" in line or "://" not in line :
        return None, None  # 跳过包含“#genre#”的行或不是URL的行
    parts = line.split(',')
    if len(parts) == 2:
        name, url = parts
        elapsed_time, is_valid, resolution = check_url(url.strip())  # 获取响应时间和分辨率
        if is_valid:
            return elapsed_time, f"{name},{url},{resolution}"  # 返回处理时间、修改后的行和分辨率
        else:
            return 0.0, line.strip()
    return  0.0, line.strip()

# 读取文本文件并处理每一行
merged_output_lines = read_txt_to_array('大杂烩.txt')
new_merged_output_lines = []

for line in merged_output_lines:
    if "#genre#" in line or "://" not in line:
        new_merged_output_lines.append(line)  # 添加跳过的行
    elif "#genre#" not in line and "," in line and "://" in line:
        elapsed_time, newline = process_line(line)  # 处理包含URL的行
        new_merged_output_lines.append(f"{elapsed_time:.2f}ms,{newline}")  # 添加处理后的行

# 将处理后的文本写入新文件
output_file = "大杂烩.txt"
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in new_merged_output_lines:
            f.write(line + '\n')
    print(f"合并后的文本已保存到文件: {output_file}")
except Exception as e:
    continue
    # 打印保存文件时的错误信息
    print(f"保存文件时发生错误：{e}")
