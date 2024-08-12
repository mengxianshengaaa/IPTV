#本程序只对酒店源进行了720p以上分辨率过滤，IP段去重。组播和自定义源请自行从源文件过滤
import time
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import re
import os
import threading
from queue import Queue
import queue
from datetime import datetime
import replace
import fileinput
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from pypinyin import lazy_pinyin
from opencc import OpenCC
import base64
import cv2
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from translate import Translator  # 导入Translator类，用于文本翻译






##########################################################IP段去重,保留最后一个IP段，防止高峰拥堵，也减少不必要的检测行

def deduplicate_lines(input_file_path, output_file_path):
    seen_combinations = {}
    unique_lines = []
    with open(input_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 使用正则表达式查找行中的所有URL，并捕获IP地址、端口号和端口号之后的部分
            urls = re.findall(r'http://([\d.]+):(\d+)(/.*)?', line)
            # 为每个URL生成一个去重键
            for full_url in urls:
                ip, port, path = full_url
                ip_parts = ip.split('.')
                if len(ip_parts) < 3:
                    continue
                # 使用IP的前三个字段和端口号之后的部分生成去重键
                combination_key = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}-{port}-{path or ''}"
                # 检查这个组合是否已经出现过
                if combination_key not in seen_combinations:
                    # 如果没有出现过，记录当前行和去重键
                    seen_combinations[combination_key] = line.strip()
                else:
                    # 如果已经出现过，更新为最后出现的行
                    seen_combinations[combination_key] = line.strip()
    # 将去重后的所有唯一行写入新文件
    with open(output_file_path, 'w', encoding='utf-8') as file:
        for line in seen_combinations.values():
            file.write(line + '\n')
print(f"IP段去重完成")            
# 调用函数
input_file_path = '酒店源.txt'
output_file_path = '酒店源.txt'
deduplicate_lines(input_file_path, output_file_path)
################################################################################


#################################################### 对整理好的频道列表测试HTTP连接
# 函数：获取视频分辨率
def get_video_resolution(video_path, timeout=1):
    # 使用OpenCV创建视频捕获对象
    cap = cv2.VideoCapture(video_path)
    # 检查视频是否成功打开
    if not cap.isOpened():
        return None
    # 获取视频的宽度和高度
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # 释放视频捕获对象
    cap.release()
    # 返回视频的分辨率
    return (width, height)

# 函数：处理每一行
def process_line(line, output_file, order_list, valid_count, invalid_count, total_lines):
    # 去除行尾的空白字符并按逗号分割行
    parts = line.strip().split(',')
    # 如果行包含特定的标签'#genre#'，则直接写入新文件
    if '#genre#' in line:
        with threading.Lock():  # 使用线程锁保证写入操作的原子性
            output_file.write(line)
            print(f"已写入genre行：{line.strip()}")
    # 如果分割后的部分数量为2，则继续处理
    elif len(parts) == 2:
        channel_name, channel_url = parts
        # 获取视频的分辨率
        resolution = get_video_resolution(channel_url, timeout=2)
        # 如果分辨率有效且高度大于等于720p
        if resolution and resolution[1] >= 720:
            with threading.Lock():  # 使用线程锁
                output_file.write(f"{channel_name}[{resolution[1]}p],{channel_url}\n")
                # 将频道名、分辨率和URL添加到列表中
                order_list.append((channel_name, resolution[1], channel_url))
                # 有效计数增加
                valid_count[0] += 1
                print(f"Channel '{channel_name}' accepted with resolution {resolution[1]}p at URL {channel_url}.")
        else:
            # 如果分辨率不满足条件，无效计数增加
            invalid_count[0] += 1
    # 打印当前处理进度
    with threading.Lock():
        print(f"有效: {valid_count[0]}, 无效: {invalid_count[0]}, 总数: {total_lines}, 进度: {(valid_count[0] + invalid_count[0]) / total_lines * 100:.2f}%")

# 函数：多线程工作
def worker(task_queue, output_file, order_list, valid_count, invalid_count, total_lines):
    # 循环直到队列为空
    while True:
        try:
            # 从队列中获取任务，超时时间为1秒
            line = task_queue.get(timeout=0.5)
            # 处理获取的任务
            process_line(line, output_file, order_list, valid_count, invalid_count, total_lines)
        except Queue.Empty:  # 如果队列为空，捕获异常
            break
        finally:
            # 标记任务已完成
            task_queue.task_done()

# 主函数
def main(source_file_path, output_file_path):
    # 初始化列表和计数器
    order_list = []
    valid_count = [0]
    invalid_count = [0]
    task_queue = Queue()
    # 使用with语句打开源文件并读取所有行
    with open(source_file_path, 'r', encoding='utf-8') as source_file:
        lines = source_file.readlines()
    # 使用with语句打开输出文件准备写入
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        # 创建线程池，最大工作线程数为64
        with ThreadPoolExecutor(max_workers=64) as executor:
            # 为线程池中的每个线程提交worker函数
            for _ in range(64):
                executor.submit(worker, task_queue, output_file, order_list, valid_count, invalid_count, len(lines))
            # 将所有行放入任务队列
            for line in lines:
                task_queue.put(line)
            # 等待队列中的所有任务完成
            task_queue.join()
    # 打印任务完成的统计信息
    print(f"任务完成，有效频道数：{valid_count[0]}, 无效频道数：{invalid_count[0]}, 总频道数：{len(lines)}")

# 程序入口点
if __name__ == "__main__":
    # 定义源文件和输出文件的路径
    source_file_path = '酒店源.txt'  # 替换为你的源文件路径
    output_file_path = '检测结果.txt'  # 替换为你的输出文件路径
    # 调用主函数
    main(source_file_path, output_file_path)




###############################################################################文本排序
# 打开原始文件读取内容，并写入新文件
with open('检测结果.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()
# 定义一个函数，用于提取每行的第一个数字
def extract_first_number(line):
    match = re.search(r'\d+', line)
    return int(match.group()) if match else float('inf')
# 对列表中的行进行排序
# 按照第一个数字的大小排列，如果不存在数字则按中文拼音排序
sorted_lines = sorted(lines, key=lambda x: (not 'CCTV' in x, extract_first_number(x) if 'CCTV' in x else lazy_pinyin(x.strip())))
# 将排序后的行写入新的utf-8编码的文本文件，文件名基于原文件名
output_file_path = "sorted_" + os.path.basename(file_path)
# 写入新文件
with open('酒店源.txt', "w", encoding="utf-8") as file:
    for line in sorted_lines:
        file.write(line)
print(f"文件已排序并保存为新文件")


########################################################################定义关键词分割规则,分类提取
def check_and_write_file(input_file, output_file, keywords):
    # 使用 split(', ') 而不是 split(',') 来分割关键词
    keywords_list = keywords.split(', ')
    first_keyword = keywords_list[0]  # 获取第一个关键词作为头部信息
    pattern = '|'.join(re.escape(keyword) for keyword in keywords_list)
    extracted_lines = False
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    with open(output_file, 'w', encoding='utf-8') as out_file:
        out_file.write(f'{first_keyword},#genre#\n')  # 使用第一个关键词作为头部信息
        for line in lines:
            if 'genre' not in line and 'epg' not in line:
                if re.search(pattern, line):
                    out_file.write(line)
                    extracted_lines = True
    # 如果没有提取到任何关键词，则不保留输出文件
    if not extracted_lines:
        os.remove(output_file)  # 删除空的输出文件        
        print(f"未提取到关键词，{output_file} 已被删除。")
    else:
        print(f"文件已提取关键词并保存为: {output_file}")


# 按类别提取关键词并写入文件
check_and_write_file('酒店源.txt',  'a.txt',  keywords="央视频道, CCTV")
check_and_write_file('酒店源.txt',  'b.txt',  keywords="卫视频道, 卫视")
check_and_write_file('酒店源.txt',  'c.txt',  keywords="影视频道, 影, 剧, 大片")
check_and_write_file('酒店源.txt',  'e.txt',  keywords="港澳频道, TVB, 珠江台, 澳门, 龙华, 广场舞, 动物杂技, 民视, 中视, 华视, AXN, MOMO, 采昌, 耀才, 靖天, 镜新闻, 靖洋, 莲花, 年代, 爱尔达, 好莱坞, 华丽, 非凡, 公视, \
寰宇, 无线, EVEN, MoMo, 爆谷, 面包, momo, 唐人, 中华小, 三立, CNA, FOX, RTHK, Movie, 八大, 中天, 中视, 东森, 凤凰, 天映, 美亚, 环球, 翡翠, 亚洲, 大爱, 大愛, 明珠, 半岛, AMC, 龙祥, 台视, 1905, 纬来, 神话, 经典都市, 视界, \
番薯, 私人, 酒店, TVB, 凤凰, 半岛, 星光视界, 大愛, 新加坡, 星河, 明珠, 环球, 翡翠台")


#对生成的文件进行合并
file_contents = []
file_paths = ["e.txt", "a.txt", "b.txt", "c.txt"]  # 替换为实际的文件路径列表
for file_path in file_paths:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding="utf-8") as file:
            content = file.read()
            file_contents.append(content)
    else:                # 如果文件不存在，则提示异常并打印提示信息
        print(f"文件 {file_path} 不存在，跳过")
# 写入合并后的文件
with open("去重.txt", "w", encoding="utf-8") as output:
    output.write('\n'.join(file_contents))


##################################################################### 打开文档并读取所有行 ，对提取后重复的频道去重
with open('去重.txt', 'r', encoding="utf-8") as file:
 lines = file.readlines()
# 使用列表来存储唯一的行的顺序 
 unique_lines = [] 
 seen_lines = set() 
# 遍历每一行，如果是新的就加入unique_lines 
for line in lines:
 if line not in seen_lines:
  unique_lines.append(line)
  seen_lines.add(line)
# 将唯一的行写入新的文档 
with open('酒店源.txt', 'w', encoding="utf-8") as file:
 file.writelines(unique_lines)


#任务结束，删除不必要的过程文件
files_to_remove = ['去重.txt', "2.txt", "iptv.txt", "iptv1.txt", "e.txt", "a.txt", "b.txt", "c.txt", "检测结果.txt"]
for file in files_to_remove:
    if os.path.exists(file):
        os.remove(file)
    else:              # 如果文件不存在，则提示异常并打印提示信息
        print(f"文件 {file} 不存在，跳过删除。")
print("任务运行完毕，酒店源频道列表可查看文件夹内txt文件！")

