from lxml import etree
import time
from datetime import datetime, timedelta  # 确保 timedelta 被导入
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor
import requests
import re
import os
import threading
from queue import Queue
import queue
from datetime import datetime
import replace
import fileinput
from tqdm import tqdm
from pypinyin import lazy_pinyin
from opencc import OpenCC
import base64
import cv2
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from translate import Translator  # 导入Translator类,用于文本翻译
# 定义txt文件的URL列表
urls = [
        '',
        '',
        'https://gitlab.com/p2v5/wangtv/-/raw/main/wang-tvlive.txt',
        'https://raw.githubusercontent.com/kimwang1978/tvbox/main/%E5%A4%A9%E5%A4%A9%E5%BC%80%E5%BF%83/lives/%E2%91%AD%E5%BC%80%E5%BF%83%E7%BA%BF%E8%B7%AF.txt',
        'https://raw.githubusercontent.com/mlvjfchen/TV/main/iptv_list.txt', 
        'https://raw.githubusercontent.com/gdstchdr1/IPTV/main/bc.txt',  # 【2024-08-01 10:40:29】
        'https://raw.githubusercontent.com/lalifeier/IPTV/main/txt/IPTV.txt',  # 【2024-08-01 10:40:29】
        'https://raw.githubusercontent.com/yoursmile66/TVBox/main/live.txt',  #【2024-08-01 10:40:29】
        'https://raw.githubusercontent.com/PizazzGY/TVBox/main/live.txt', # 【2024-08-01 10:40:29】
        'https://raw.githubusercontent.com/pxiptv/live/main/iptv.txt', # 【2024-08-02 16:48:40】#每日更新1次
        'https://notabug.org/vnjd/yydu/raw/master/yyfug.txt', # 【2024-08-06】
        'https://tvkj.top/tvlive.txt', # 【2024-08-06】
        'https://pan.beecld.com/f/OXMcA/%E6%98%A5%E8%B5%A2%E5%A4%A9%E4%B8%8B.txt', # 【2024-08-06】
        'http://kxrj.site:55/lib/kx2024.txt',   # 【2024-08-07】
        'https://raw.githubusercontent.com/yuanzl77/IPTV/main/live.txt',   # 2024-08-05 每天更新一次，量太多转到blacklist处理
        'https://wzsvip.github.io/ipv4.txt',   # 【2024-08-08】
        'http://wz.42web.io/ipv4.txt',   # 【2024-08-08】
        'http://ttkx.live:55/lib/kx2024.txt',   # 【2024-08-10】每日更新3次，移动到main.py
        'http://mywlkj.ddns.net:5212/f/EErCL/%E5%8F%B0%E6%B9%BE%E7%94%B5%E8%A7%86TV.txt',   # 【2024-08-10】
        'http://yuhuahx.com/dsj66.txt',   # 【2024-08-14】
        'https://raw.gitcode.com/xiaoqi719/yingshi/raw/main/zhibo.txt',  # 【2024-08-20】
        'http://xhztv.top/tvlive.txt',  # 【2024-08-20】
        'https://raw.githubusercontent.com/Andreayoo/ming/main/IPTV.txt', #【2024-08-24】
        'http://gg.gg/cctvgg'   # 【2024-08-10】
]
# 合并文件的函数
def merge_txt_files(urls, output_filename='汇总.txt'):
    try:
        # 打开文件准备写入
        with open(output_filename, 'w', encoding='utf-8') as outfile:
            for url in urls:
                try:
                    # 发送HTTP GET请求
                    response = requests.get(url)
                    # 检查请求是否成功
                    response.raise_for_status()
                    # 读取内容并写入输出文件
                    outfile.write(response.text + '\n')
                except requests.RequestException as e:
                    # 打印错误信息并继续下一个循环
                    print(f'Error downloading {url}: {e}')
    except IOError as e:
        # 处理文件写入错误
        print(f'Error writing to file: {e}')
# 调用函数
merge_txt_files(urls)


# 打开文本文件进行读取
def read_and_process_file(input_filename, output_filename, encodings=['utf-8', 'gbk']):
    # 尝试使用不同的编码读取文件
    for encoding in encodings:
        try:
            with open(input_filename, 'r', encoding=encoding) as file:
                lines = file.readlines()
                break  # 如果成功读取，跳出循环
        except UnicodeDecodeError:
            continue  # 如果出现编码错误，尝试下一个编码
    else:
        raise ValueError(f"文件 '{input_filename}' 的编码无法识别或不支持")
    # 使用 UTF-8 编码创建或打开输出文件
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        # 处理每一行
        for line in lines:
            if '$' in line:
                # 截取到'$'之前的部分，注意去除可能的换行符
                processed_line = line.split('$')[0].rstrip('\n')
                outfile.write(processed_line + '\n')  # 写入处理后的行到文件，并添加换行符
            else:
                # 正常写入行到文件，并添加换行符
                outfile.write(line)
# 调用函数
read_and_process_file('汇总.txt', '汇总.txt')

###################################################################去重#####################################
def remove_duplicates(input_file, output_file):
    # 用于存储已经遇到的URL和包含genre的行
    seen_urls = set()
    seen_lines_with_genre = set()
    # 用于存储最终输出的行
    output_lines = []
    # 打开输入文件并读取所有行
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        print("去重前的行数：", len(lines))
        # 遍历每一行
        for line in lines:
            # 使用正则表达式查找URL和包含genre的行,默认最后一行
            urls = re.findall(r'[https]?[http]?[rtsp]?[rtmp]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', line)
            genre_line = re.search(r'\bgenre\b', line, re.IGNORECASE) is not None
            # 如果找到URL并且该URL尚未被记录
            if urls and urls[0] not in seen_urls:
                seen_urls.add(urls[0])
                output_lines.append(line)
            # 如果找到包含genre的行，无论是否已被记录，都写入新文件
            if genre_line:
                output_lines.append(line)
    # 将结果写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
    print("去重后的行数：", len(output_lines))
# 使用方法
remove_duplicates('汇总.txt', '汇总.txt')   

###############################################################################替换#########################
# 导入fileinput模块
import fileinput
# 定义替换规则的字典
replacements = {
    	"CCTV-1高清测试": "",
    	"CCTV-2高清测试": "",
    	"CCTV-7高清测试": "",
    	"CCTV-10高清测试": "",
    	"中央": "CCTV",
    	"高清""": "",
    	"HD": "",
    	"标清": "",
    	"-": "",
    	"咪咕": "",
    	"_": "",
    	"超清": "",
    	"频道": "",
    	"CCTV-": "CCTV",
    	"CCTV_": "CCTV",
    	" ": "",
    	"CCTV风云剧场": "风云剧场",
    	"CCTV第一剧场": "第一剧场",
    	"CCTV怀旧剧场": "怀旧剧场",
    	"熊猫影院": "熊猫电影",
    	"熊猫爱生活": "熊猫生活",
    	"爱宠宠物": "宠物生活",
    	"[ipv6]": "",
    	"专区": "",
    	"卫视超": "卫视",
    	"CCTV风云剧场": "风云剧场",
    	"CCTV第一剧场": "第一剧场",
    	"CCTV怀旧剧场": "怀旧剧场",
    	"IPTV": "",
    	"PLUS": "+",
    	"＋": "+",
    	"(": "",
    	")": "",
    	"CAV": "",
    	"美洲": "",
    	"北美": "",
    	"12M": "",
    	"高清测试CCTV-1": "",
    	"高清测试CCTV-2": "",
    	"高清测试CCTV-7": "",
    	"高清测试CCTV-10": "",
    	"LD": "",
    	"HEVC20M": "",
    	"S,": ",",
    	"测试": "",
    	"CCTW": "CCTV",
    	"试看": "",
    	"测试": "",
    	"测试cctv": "CCTV",
    	"CCTV1综合": "CCTV1",
    	"CCTV2财经": "CCTV2",
    	"CCTV3综艺": "CCTV3",
    	"CCTV4国际": "CCTV4",
    	"CCTV4中文国际": "CCTV4",
    	"CCTV4欧洲": "CCTV4",
    	"CCTV5体育": "CCTV5",
    	"CCTV5+体育": "CCTV5+",
    	"CCTV6电影": "CCTV6",
    	"CCTV7军事": "CCTV7",
    	"CCTV7军农": "CCTV7",
    	"CCTV7农业": "CCTV7",
    	"CCTV7国防军事": "CCTV7",
    	"CCTV8电视剧": "CCTV8",
    	"CCTV8影视": "CCTV8",
    	"CCTV8纪录": "CCTV9",
    	"CCTV9记录": "CCTV9",
    	"CCTV9纪录": "CCTV9",
    	"CCTV10科教": "CCTV10",
    	"CCTV11戏曲": "CCTV11",
    	"CCTV12社会与法": "CCTV12",
    	"CCTV13新闻": "CCTV13",
    	"CCTV新闻": "CCTV13",
    	"CCTV14少儿": "CCTV14",
    	"央视14少儿": "CCTV14",
    	"CCTV少儿超": "CCTV14",
    	"CCTV15音乐": "CCTV15",
    	"CCTV音乐": "CCTV15",
    	"CCTV16奥林匹克": "CCTV16",
    	"CCTV17农业农村": "CCTV17",
    	"CCTV17军农": "CCTV17",
    	"CCTV17农业": "CCTV17",
    	"CCTV5+体育赛视": "CCTV5+",
    	"CCTV5+赛视": "CCTV5+",
    	"CCTV5+体育赛事": "CCTV5+",
    	"CCTV5+赛事": "CCTV5+",
    	"CCTV5+体育": "CCTV5+",
    	"CCTV5赛事": "CCTV5+",
    	"凤凰中文台": "凤凰中文",
    	"凤凰资讯台": "凤凰资讯",
    	"(CCTV4K测试）": "CCTV4K",
    	"上海东方卫视": "上海卫视",
    	"东方卫视": "上海卫视",
    	"内蒙卫视": "内蒙古卫视",
    	"福建东南卫视": "东南卫视",
    	"广东南方卫视": "南方卫视",
    	"湖南金鹰卡通": "金鹰卡通",
    	"炫动卡通": "哈哈炫动",
    	"卡酷卡通": "卡酷少儿",
    	"卡酷动画": "卡酷少儿",
    	"BRTVKAKU少儿": "卡酷少儿",
    	"优曼卡通": "优漫卡通",
    	"优曼卡通": "优漫卡通",
    	"嘉佳卡通": "佳嘉卡通",
    	"世界地理": "地理世界",
    	"CCTV世界地理": "地理世界",
    	"BTV北京卫视": "北京卫视",
    	"BTV冬奥纪实": "冬奥纪实",
    	"东奥纪实": "冬奥纪实",
    	"卫视台": "卫视",
    	"湖南电视台": "湖南卫视",
    	"少儿科教": "少儿",
    	"影视剧": "影视",
    	"电视剧": "影视",
    	"CCTV1CCTV1": "CCTV1",
    	"CCTV2CCTV2": "CCTV2",
    	"CCTV7CCTV7": "CCTV7",
    	"CCTV10CCTV10": "CCTV10"
}
# 打开原始文件读取内容，并写入新文件
with open('汇总.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()
# 创建新文件并写入替换后的内容
with open('2.txt', 'w', encoding='utf-8') as new_file:
    for line in lines:
        for old, new in replacements.items():
            line = line.replace(old, new)
        new_file.write(line)
print("替换完成，新文件已保存。")



######################################################################################提取
import re
import os
# 定义一个包含所有要排除的关键词的列表
excluded_keywords = [
    'epg', 'mitv', 'udp', 'rtp', 'P2p', 'p2p', 'p3p', 'P2P', '[', 'P3p', '/hls/', '/tsfile/', 'P3P', '腔', '曲', '/zy.', '/xgj.', '春节'
]

# 定义一个包含所有要提取的关键词的列表
extract_keywords = [
    'CCTV', '卫视', '动作电影', '风云剧场', '怀旧剧场', '影迷', '高清电影', '动作电影', '影院', '全球大片', '剧场', 'TVB', '家庭影院', '电影', '星光', '华语', '美国大片', '峨眉', '凤凰', '星空', '人间', '亚洲', '环球'
    # 在这里添加需要提取的关键词
]

# 读取文件并处理每一行
with open('2.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()

    # 创建或打开一个输出文件用于写入处理后的数据
    with open('2.txt', 'w', encoding='utf-8') as outfile:
        for line in lines:
            # 首先检查行是否包含任何提取关键词
            if any(keyword in line for keyword in extract_keywords):
                # 如果包含提取关键词，进一步检查行是否不包含任何排除关键词
                if not any(keyword in line for keyword in excluded_keywords):
                    outfile.write(line)  # 写入符合条件的行到文件


###############################################################
import re
def parse_file(input_file_path, output_file_name):
    # 正则表达式匹配从'//'开始到第一个'/'或第一个'::'结束的部分
    ip_or_domain_pattern = re.compile(r'//([^/:]*:[^/:]*::[^/:]*|[^/]*)')
    # 用于存储每个IP或域名及其对应的行列表
    ip_or_domain_to_lines = {}
    # 读取原始文件内容
    with open(input_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            # 如果行是分类标签行，则跳过
            if ",#genre#" in line:
                continue
            # 检查行是否包含IP或域名
            match = ip_or_domain_pattern.search(line)
            if match:
                # 提取匹配到的IP或域名
                matched_text = match.group(1)
                # 去除IP或域名后的剩余部分，只保留匹配到的IP或域名
                ip_or_domain = matched_text.split('://')[-1].split('/')[0].split('::')[0]
                # 将行添加到对应的IP或域名列表中
                if ip_or_domain not in ip_or_domain_to_lines:
                    ip_or_domain_to_lines[ip_or_domain] = []
                ip_or_domain_to_lines[ip_or_domain].append(line)
    ############################################################################### 过滤掉小于1500字节的IP或域名段
    filtered_ip_or_domain_to_lines = {ip_or_domain: lines for ip_or_domain, lines in ip_or_domain_to_lines.items()
                                      if sum(len(line) for line in lines) >= 1500}
    # 如果没有满足条件的IP或域名段，则不生成文件
    if not filtered_ip_or_domain_to_lines:
        print("没有满足条件的IP或域名段，不生成文件。")
        return
    # 合并所有满足条件的IP或域名的行到一个文件
    with open(output_file_name, 'w', encoding='utf-8') as output_file:
        for ip_or_domain, lines in filtered_ip_or_domain_to_lines.items():
            # 写入IP或域名及其对应的行到输出文件
            output_file.write(f"频道,#genre#\n")
            for line in lines:
                output_file.write(line + '\n')
            output_file.write('\n')  # 在每个小段后添加一个空行作为分隔
# 调用函数并传入文件路径和输出文件名
parse_file('2.txt', '2.txt')



############################################################################检测同IP第一个链接，缩小验源数量
import cv2
import time
from tqdm import tqdm
# 初始化2字典
detected_ips = {}
# 存储文件路径
file_path = "2.txt"
output_file_path = "网络收集.txt"
def get_ip_key(url):
    """从URL中提取IP地址，并构造一个唯一的键"""
    # 找到'//'到第一个'/'之间的字符串
    start = url.find('://') + 3  # '://'.length 是 3
    end = url.find('/', start)  # 找到第一个'/'的位置
    return url[start:end] if end != -1 else None
# 打开输入文件和输出文件
with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()
# 获取总行数用于进度条
total_lines = len(lines)
# 写入通过检测的行到新文件
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    # 使用tqdm显示进度条
    for i, line in tqdm(enumerate(lines), total=total_lines, desc="Processing", unit='line'):
        # 检查是否包含 'genre'
        if 'genre' in line:
            output_file.write(line)
            continue
        # 分割频道名称和URL,并去除空白字符
        parts = line.split(',', 1)
        if len(parts) == 2:
            channel_name, url = parts
            channel_name = channel_name.strip()
            url = url.strip()
            # 构造IP键
            ip_key = get_ip_key(url)
            if ip_key and ip_key in detected_ips:
                # 如果IP键已存在,根据之前的结果决定是否写入新文件
                if detected_ips[ip_key]['status'] == 'ok':
                    output_file.write(line)
            elif ip_key:  # 新IP键,进行检测
                # 进行检测
                cap = cv2.VideoCapture(url)
                start_time = time.time()
                frame_count = 0
                # 尝试捕获10秒内的帧
                while frame_count < 10 and (time.time() - start_time) < 3:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frame_count += 1
                # 释放资源
                cap.release()
                # 根据捕获的帧数判断状态并记录结果
                if frame_count >= 10:  #10秒内超过230帧则写入
                    detected_ips[ip_key] = {'status': 'ok'}
                    output_file.write(line)  # 写入检测通过的行
                else:
                    detected_ips[ip_key] = {'status': 'fail'}
# 打印2
for ip_key, result in detected_ips.items():
    print(f"IP Key: {ip_key}, Status: {result['status']}")




############################################################################全部检测，防止IP段失效
import requests
import time
import cv2
from urllib.parse import urlparse
from tqdm import tqdm

# 测试HTTP连接并尝试下载数据
def test_connectivity_and_download(url, initial_timeout=1, retry_timeout=2):
    parsed_url = urlparse(url)
    if parsed_url.scheme not in ['http', 'https']:
        # 非HTTP(s)协议，尝试RTSP检测
        return test_rtsp_connectivity(url, retry_timeout)
    else:
        # HTTP(s)协议，使用原始方法
        try:
            with requests.get(url, stream=True, timeout=initial_timeout) as response:
                if 200 <= response.status_code <= 403:
                    start_time = time.time()
                    while time.time() - start_time < initial_timeout:
                        chunk = response.raw.read(1024)  # 尝试下载1KB数据
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
    输入 =  "网络收集.txt"    #input('请输入utf-8编码的直播源文件路径:')
    输出 = "网络收集.txt"
    main(输入, 输出)






import re
from pypinyin import lazy_pinyin
# 打开一个utf-8编码的文本文件
with open("网络收集.txt", "r", encoding="utf-8") as file:
    # 读取所有行并存储到列表中
    lines = file.readlines()
# 定义一个函数，用于提取每行的第一个数字
def extract_first_number(line):
    match = re.search(r'\d+', line)
    return int(match.group()) if match else float('inf')
# 对列表中的行进行排序，按照第一个数字的大小排列，其余行按中文排序
sorted_lines = sorted(lines, key=lambda x: (not 'CCTV' in x, extract_first_number(x) if 'CCTV' in x else lazy_pinyin(x.strip())))
# 将排序后的行写入新的utf-8编码的文本文件
with open("网络收集.txt", "w", encoding="utf-8") as file:
    for line in sorted_lines:
        file.write(line)




import re

def parse_file(input_file_path, output_file_name):
    # 正则表达式匹配从'//'开始到第一个'/'或第一个'::'结束的部分
    ip_or_domain_pattern = re.compile(r'//([^/:]*:[^/:]*::[^/:]*|[^/]*)')
    # 用于存储每个IP或域名及其对应的行列表
    ip_or_domain_to_lines = {}
    # 用于生成分类名的字母和数字计数器
    alphabet_counter = 0  # 字母计数器，从0开始
    number_counter = 1     # 数字计数器，从1开始
    # 读取原始文件内容
    with open(input_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            # 如果行是分类标签行，则跳过
            if ",#genre#" in line:
                continue
            # 检查行是否包含IP或域名
            match = ip_or_domain_pattern.search(line)
            if match:
                # 提取匹配到的IP或域名
                matched_text = match.group(1)
                # 去除IP或域名后的剩余部分，只保留匹配到的IP或域名
                ip_or_domain = matched_text.split('://')[-1].split('/')[0].split('::')[0]
                # 将行添加到对应的IP或域名列表中
                if ip_or_domain not in ip_or_domain_to_lines:
                    ip_or_domain_to_lines[ip_or_domain] = []
                ip_or_domain_to_lines[ip_or_domain].append(line)
    # 过滤掉小于1000字节的IP或域名段
    filtered_ip_or_domain_to_lines = {ip_or_domain: lines for ip_or_domain, lines in ip_or_domain_to_lines.items()
                                      if sum(len(line) for line in lines) >= 800}   # 过滤掉小于1000字节的IP或域名段
    # 如果没有满足条件的IP或域名段，则不生成文件
    if not filtered_ip_or_domain_to_lines:
        print("没有满足条件的IP或域名段，不生成文件。")
        return
    # 合并所有满足条件的IP或域名的行到一个文件
    with open(output_file_name, 'w', encoding='utf-8') as output_file:
        for ip_or_domain, lines in filtered_ip_or_domain_to_lines.items():
            # 检查是否需要递增数字计数器
            if alphabet_counter >= 26:
                number_counter += 1
                alphabet_counter = 0  # 重置字母计数器
            # 生成分类名
            genre_name = chr(65 + alphabet_counter) + str(number_counter)
            output_file.write(f"{genre_name},#genre#\n")
            for line in lines:
                output_file.write(line + '\n')
            output_file.write('\n')  # 在每个小段后添加一个空行作为分隔
            alphabet_counter += 1  # 递增字母计数器
# 调用函数并传入文件路径和输出文件名
parse_file('网络收集.txt', '网络收集.txt')

################################################################################################任务结束，删除不必要的过程文件
files_to_remove = ["2.txt", "汇总.txt"]
for file in files_to_remove:
    if os.path.exists(file):
        os.remove(file)
    else:              # 如果文件不存在，则提示异常并打印提示信息
        print(f"文件 {file} 不存在，跳过删除。")
print("任务运行完毕，频道列表可查看文件夹内源.txt文件！")
