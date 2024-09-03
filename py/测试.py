#本程序只适用于酒店源的检测,请勿移植他用
import time
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
import fileinput
from tqdm import tqdm
from pypinyin import lazy_pinyin
from opencc import OpenCC
import base64
import cv2
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from translate import Translator  # 导入Translator类,用于文本翻译
# 扫源测绘空间地址
# 搜素关键词："iptv/live/zh_cn.js" && country="CN" && region="Hunan" && city="changsha"
# 搜素关键词："ZHGXTV" && country="CN" && region="Hunan" && city="changsha"
#"isShowLoginJs"智能KUTV管理
######################################################################################################################
######################################################################################################################
###########################################################ZHGX采集####################################################
######################################################################################################################
######################################################################################################################
import requests

urls = [
    "https://fofa.info/result?qbase64=IixodHRwIiAmJiAi5Yek5YewIiAmJiAi5Lic5qOuIg%3D%3D", 
]



def is_url_accessible(url):
    try:
        # 发送 GET 请求，设置超时时间为 3 秒
        response = requests.get(url, timeout=3)
        # 如果响应状态码在 200 到 401 之间（包括 200 和 401），则认为 URL 可访问
        if 200 <= response.status_code <= 401:
            return url
    except requests.exceptions.RequestException:
        # 如果请求过程中出现异常，不做任何处理，直接跳过
        pass
    return None

def get_content(url):
    try:
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        # 确保内容类型为HTML或文本
        if 'text/html' in response.headers.get('Content-Type', ''):
            return response.text
    except requests.RequestException as e:
        print(f"请求错误: {e}")
    return None

# 创建一个空列表用于存储结果
results = []
for url in urls:
    # 发送 GET 请求获取 URL 的内容
    response = requests.get(url)
    # 获取响应的文本内容
    page_content = response.text

# 遍历初始 URL 列表
for url in urls:
    # 发送 GET 请求获取 URL 的内容
    response = requests.get(url)
    # 获取响应的文本内容
    page_content = response.text

    # 查找所有符合指定格式的网址
    # 匹配纯域名，可能带有http://或https://前缀，但不包含端口
    # 匹配纯数字IP地址，后面跟着端口号
    pattern = r"(https?://[\w-]+(?:\.[\w-]+)*(?::\d+)?|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?::\d+)?)"
    # 使用正则表达式在页面内容中查找所有符合格式的 URL
    urls_all = re.findall(pattern, page_content)
    # 去重得到唯一的URL列表
    unique_urls = set(urls_all)
    # 排除包含特定子字符串的域名
    unique_urls = {u for u in unique_urls if "fofa.info" not in u}
    
    valid_urls = []
    # 多线程获取可用url
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = []
        for unique_url in unique_urls:
            # 提交任务，检查每个 URL 是否可访问
            futures.append(executor.submit(is_url_accessible, unique_url))
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                # 如果 URL 可访问，将其添加到有效 URL 列表中
                valid_urls.append(result)

# 打印有效的 URL 列表
for url in valid_urls:
    print(url)
    
results = []  # 用于存储结果的列表
for valid_url in valid_urls:  # 确保这里是 valid_urls
    print(valid_url)
    try:
        # 发送GET请求获取JSON文件,设置超时时间为3秒
        response = requests.get(valid_url, timeout=3)
        # 尝试解码响应内容为 UTF-8 格式的文本
        text_data = response.content.decode('utf-8')
        # 如果解码成功，处理 text_data
        # 例如打印或进一步处理
        print(text_data)  # 这里只是打印，你可以根据需要进行其他处理
        except:
        # 如果出现 UnicodeDecodeError，打印错误信息并跳过当前循环
        print(f"无法解码来自 {url} 的响应内容，跳过此 URL。")
        continue
        # 正则表达式匹配 #EXTINF 行
        pattern = r"#EXTINF:-1 group-title=\"([^\"]+)\","
        matches = re.finditer(pattern, json_data)

        for match in matches:
            channel_name = match.group(1)
            # 获取下一行的 URL
            next_line_index = lines.index(match.group(0)) + 1
            if next_line_index < len(lines):
                next_line = lines[next_line_index].strip()
                if next_line:
                    print(f"{channel_name},{next_line}")
                    results.append(f"{channel_name},{next_line}")

        # 正则表达式匹配频道名和频道地址在同一行的文本
        pattern = r"([^,]+),(http[s]?://[^\s]+)"
        matches = re.finditer(pattern, json_data)
        for match in matches:
            channel_name = match.group(1).strip()
            channel_url = match.group(2).strip()
            print(f"{channel_name}, {channel_url}")
            results.append(f"{channel_name},{channel_url}")

    except requests.RequestException as e:
        print(f"请求 {valid_url} 时发生错误: {e}")

    # 处理名称替换逻辑
    for result in results:
        name, urld = result.split(',')
        name = name.strip()
        if name and urld:
            name = name.replace("高清电影", "影迷电影")                            
            name = name.replace("中央", "CCTV")
            name = name.replace("高清", "")
            name = name.replace("HD", "")
            name = name.replace("标清", "")
            name = name.replace("超高", "")
            name = name.replace("频道", "")
            results.append(f"{name},{urld}")

# 将结果写入文件
with open("iptv.txt", 'w', encoding='utf-8') as file:
    for result in results:
        file.write(result + "\n")
        print(result)  # 打印每个结果

print("频道列表文件iptv.txt获取完成！")



######################################################################################################################
######################################################################################################################
######################################################################################################################
# 定义关键词替换字典
keywords_replacements = {
    '关键词1': '替换词1',
    '关键词2': '替换词2',
    '关键词3': '替换词3',
    # 添加更多关键词替换规则
}
# 读取文件内容
with open("iptv.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()
# 修改文件内容
modified_lines = []
for line in lines:
    # 对每一行中的每个关键词进行替换
    for keyword, replacement in keywords_replacements.items():
        line = line.replace(keyword, replacement)
    modified_lines.append(line)

# 将修改后的内容写回文件
with open("iptv.txt", "w", encoding="utf-8") as file:
    file.writelines(modified_lines)
print("文件内容已更新！")
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################


# 打开文档并读取所有行 
with open('iptv.txt', 'r', encoding="utf-8") as file:
    lines = file.readlines()

# 使用列表来存储唯一的行的顺序 
unique_lines = [] 
seen_lines = set() 

# 打印去重前的行数
print(f"去重前的行数: {len(lines)}")

# 遍历每一行，如果是新的就加入unique_lines 
for line in lines:
    line_stripped = line.strip()  # 去除行尾的换行符
    if line_stripped not in seen_lines:
        unique_lines.append(line)  # 保持原始行的格式，包括换行符
        seen_lines.add(line_stripped)

# 将唯一的行写入新的文档 
with open('iptv.txt', 'w', encoding="utf-8") as file:
    file.writelines(unique_lines)

# 打印去重后的行数
print(f"去重后的行数: {len(unique_lines)}")




######################################################################################################################
###################################################去除列表中的组播地址,酒店源验证整理
def filter_lines(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    filtered_lines = []
    for line in lines:
        if 'http' in line and 'rstp' in line and 'rmtp' in line:  #行中包含m3u的同时还要包含hls或者tsfile
          if 'udp' not in line and 'rtp' not in line:   # and 'CCTV' not in line and '卫视' not in line  排除组播地址
            filtered_lines.append(line)
    with open(output_file, 'w', encoding='utf-8') as output_file:
        output_file.writelines(filtered_lines)
filter_lines("iptv.txt", "酒店源.txt")



#################################################### 对整理好的频道列表测试HTTP连接
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
    输入 =  "酒店源.txt"    #input('请输入utf-8编码的直播源文件路径:')
    输出 = "酒店源.txt"
    main(输入, 输出)
#

##########################################################################################简体转繁体
# 创建一个OpenCC对象,指定转换的规则为繁体字转简体字
converter = OpenCC('t2s.json')#繁转简
#converter = OpenCC('s2t.json')#简转繁
# 打开txt文件
with open('酒店源.txt', 'r', encoding='utf-8') as file:
    traditional_text = file.read()
# 进行繁体字转简体字的转换
simplified_text = converter.convert(traditional_text)
# 将转换后的简体字写入txt文件
with open('酒店源.txt', 'w', encoding='utf-8') as file:
    file.write(simplified_text)
#






####################### 提示用户输入文件名（拖入文件操作）打开用户指定的文件对不规范频道名再次替换
file_path = '酒店源.txt'
# 检查文件是否存在
if not os.path.isfile(file_path):
    print("文件不存在，请重新输入.")
    exit(1)
with open(file_path, 'r', encoding="utf-8") as file:
    # 读取所有行并存储到列表中
    lines = file.readlines()
#定义替换规则的字典对频道名替换
replacements = {
    	"-": "",
    	"星河": "TVB星河",
    	"福建东南卫视": "东南卫视",
    	"CCTV风云音乐": "风云音乐",
    	"本港台（珠江）": "TVB星河",
    	"\n都市": "\n河南都市",
    	"": "",
    	"": "",
    	"SD": "",
    	"「": "",
    	"AA": "",
    	"XF": "",
    	"": "",
    	"": "",
    	"湖南金鹰纪实": "金鹰纪实",
    	"频道": "",
    	"CCTV-": "CCTV",
    	"CCTV_": "CCTV",
    	" ": "",
    	"CCTV高尔夫网球": "高尔夫网球",
    	"CCTV发现之旅": "发现之旅",
    	"CCTV中学生": "中学生",
    	"CCTV兵器科技": "兵器科技",
    	"CCTV地理世界": "地理世界",
    	"CCTV风云足球": "风云足球",
    	"CCTV央视台球": "央视台球",
    	"CCTV台球": "台球",
    	"CCTV高尔夫网球": "高尔夫网球",
    	"CCTV中视购物": "中视购物",
    	"CCTV发现之旅": "发现之旅",
    	"CCTV中学生": "中学生",
    	"CCTV高尔夫网球": "高尔夫网球",
    	"CCTV风云剧场": "风云剧场",
    	"CCTV第一剧场": "第一剧场",
    	"CCTV怀旧剧场": "怀旧剧场",
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
    	"NewTv": "",
    	"NEWTV": "",
    	"NewTV": "",
    	"iHOT": "",
    	"CHC": "",
    	"测试cctv": "CCTV",
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


with open('测试.txt', 'w', encoding='utf-8') as new_file:
    for line in lines:
        # 去除行尾的换行符
        line = line.rstrip('\n')
        # 分割行，获取逗号前的字符串
        parts = line.split(',', 1)
        if len(parts) > 0:
            # 替换逗号前的字符串
            before_comma = parts[0]
            for old, new in replacements.items():
                before_comma = before_comma.replace(old, new)
            # 将替换后的逗号前部分和逗号后部分重新组合成一行，并写入新文件
            new_line = f'{before_comma},{parts[1]}\n' if len(parts) > 1 else f'{before_comma}\n'
            new_file.write(new_line)

#####################################定义替换规则的字典,对整行内的多余标识内容进行替换
replacements = {
    	"（）": "",
        "湖北,": "湖北卫视,",
        "广东,": "广东卫视,",
        "安徽,": "安徽卫视,",
        "峨眉电影": "峨眉电影[50FPS]",
        "T[": "T",
        "dx[": "[",
        "g[": "[",
        "P[": "+[",
        "lt[": "[",
        "电信": "",
        "卫视高清": "卫视",
        "SCTV5": "",
        "T,": ",",
        "dx,": ",",
        "g,": ",",
        "TVBTVB": "TVB",
        "": "",
        "": "",
        "": "",
        "": "",
        "": ""
}
# 打开原始文件读取内容，并写入新文件
with open('测试.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()
# 创建新文件并写入替换后的内容
with open('测试.txt', 'w', encoding='utf-8') as new_file:
    for line in lines:
        for old, new in replacements.items():
            line = line.replace(old, new)
        new_file.write(line)
print("替换完成，新文件已保存。")


###############################################################################文本排序
# 打开原始文件读取内容，并写入新文件
with open('测试.txt', 'r', encoding='utf-8') as file:
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
print("\n\n\n\n\n\n")


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
    # 如果没有提取到任何关键词,则不保留输出文件
    if not extracted_lines:
        os.remove(output_file)  # 删除空的输出文件
        print(f"未提取到关键词,{output_file} 已被删除。")
    else:
        print(f"文件已提取关键词并保存为: {output_file}")
# 按类别提取关键词并写入文件
check_and_write_file('酒店源.txt',  'a0.txt',  keywords="央视频道, 8K, 4K, 4k")
check_and_write_file('酒店源.txt',  'a.txt',  keywords="央视频道, CCTV, 风云, 女性时尚, 地理世界, 音乐")
check_and_write_file('酒店源.txt',  'a1.txt',  keywords="央视频道")
check_and_write_file('酒店源.txt',  'b.txt',  keywords="卫视频道, 卫视, 凤凰, 星空")
check_and_write_file('酒店源.txt',  'c.txt',  keywords="影视频道, 剧, 选, 影")
check_and_write_file('酒店源.txt',  'e.txt',  keywords="港澳频道, TVB, 珠江台, 澳门, 龙华, 广场舞, 动物杂技, 民视, 中视, 华视, AXN, MOMO, 采昌, 耀才, 靖天, 镜新闻, 靖洋, 莲花, 年代, 爱尔达, 好莱坞, 华丽, 非凡, 公视, \
寰宇, 无线, EVEN, MoMo, 爆谷, 面包, momo, 唐人, 中华小, 三立, 37.27, 猪哥亮, 综艺, Movie, 八大, 中天, 中视, 东森, 凤凰, 天映, 美亚, 环球, 翡翠, ZIPP, 大爱, 大愛, 明珠, jdshipin, AMC, 龙祥, 台视, 1905, 纬来, 神话, 经典都市, 视界, \
番薯, 私人, 酒店, TVB, 凤凰, 半岛, 星光视界, 大愛, 新加坡, 星河, 明珠, 环球, 翡翠台")
check_and_write_file('酒店源.txt',  'f.txt',  keywords="省市频道, 湖北, 武汉, 河北, 广东, 河南, 陕西, 四川, 湖南, 广西, 山西, 石家庄, 南宁, 汕头, 揭阳, 普宁, 福建, 辽宁")
check_and_write_file('酒店源.txt',  'o1.txt',  keywords="其他频道, 新闻, 综合, 文艺, 电视, 公共, 科教, 教育, 民生, 轮播, 套, 法制, 文化, 经济, 生活")
check_and_write_file('酒店源.txt',  'o.txt',  keywords="其他频道, , ")
#
#对生成的文件进行合并
file_contents = []
file_paths = ["e.txt", "a0.txt", "a.txt", "a1.txt", "b.txt", "c.txt", "c1.txt", "c2.txt", "d.txt", "f.txt", "o1.txt", "o.txt"]  # 替换为实际的文件路径列表
for file_path in file_paths:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding="utf-8") as file:
            content = file.read()
            file_contents.append(content)
    else:                # 如果文件不存在,则提示异常并打印提示信息
        print(f"文件 {file_path} 不存在,跳过")
# 写入合并后的文件
with open("去重.txt", "w", encoding="utf-8") as output:
    output.write('\n'.join(file_contents))
#
##################################################################### 打开文档并读取所有行 ,对提取后重复的频道去重
with open('去重.txt', 'r', encoding="utf-8") as file:
 lines = file.readlines()
# 使用列表来存储唯一的行的顺序 
 unique_lines = [] 
 seen_lines = set() 
# 遍历每一行,如果是新的就加入unique_lines 
for line in lines:
 if line not in seen_lines:
  unique_lines.append(line)
  seen_lines.add(line)
# 将唯一的行写入新的文档 
with open('测试.txt', 'w', encoding="utf-8") as file:
 file.writelines(unique_lines)
#任务结束,删除不必要的过程文件
files_to_remove = ['去重.txt', "2.txt", "iptv.txt", "e.txt", "a0.txt", "a.txt", "a1.txt", "b.txt", "c.txt", "c1.txt", "c2.txt", "d.txt", "f.txt", "o1.txt", "o.txt", "酒店源.txt"]
for file in files_to_remove:
    if os.path.exists(file):
        os.remove(file)
    else:              # 如果文件不存在,则提示异常并打印提示信息
        print(f"文件 {file} 不存在,跳过删除。")
print("任务运行完毕,酒店源频道列表可查看文件夹内txt文件！")
