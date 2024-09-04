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
    #"https://fofa.info/result?qbase64=IlpIR1hUViIgJiYgcmVnaW9uPSJndWFuZ2Rvbmci", #广东
    "https://fofa.info/result?qbase64=IlpIR1hUViIgJiYgcmVnaW9uPSJIZW5hbiI%3D" ,   #河南
    #“https://fofa.info/result?qbase64=IlpIR1hUViIg”，#ZHGX
    "https://fofa.info/result?qbase64=IlpIR1hUViIgJiYgcmVnaW9uPSJoZW5hbiIgJiYgcG9ydD0iODA5MCI=" ,   #河南8090
    #"https://fofa.info/result?qbase64=IlpIR1hUViIgJiYgcmVnaW9uPSJoZWJlaSI%3D", #河北
]

def modify_urls(url):
    # 创建一个空列表用于存储修改后的 URL
    modified_urls = []
    # 找到 URL 中 IP 地址开始的索引位置，"//" 后两个字符开始为 IP 地址起始位置
    ip_start_index = url.find("//") + 2
    # 找到 URL 中 IP 地址结束的索引位置，从 ip_start_index 开始查找第一个 ":" 的位置
    ip_end_index = url.find(":", ip_start_index)
    # 找到 URL 中 IP 地址结束的索引位置，从 ip_start_index 开始查找第一个 ":" 的位置
    base_url = url[:ip_start_index]
    # 获取 URL 中的 IP 地址部分
    ip_address = url[ip_start_index:ip_end_index]
    # 获取 URL 中的端口部分
    port = url[ip_end_index:]
    # 定义一个字符串，表示 IP 地址的结尾部分
    ip_end = "/ZHGXTV/Public/json/live_interface.txt"
    # 遍历 1 到 255 的数字
    for i in range(1, 256):
        # 修改 IP 地址的最后一位数字
        modified_ip = f"{ip_address[:-1]}{i}"
        # 组合成新的 URL
        modified_url = f"{base_url}{modified_ip}{port}{ip_end}"
        # 将新的 URL 添加到列表中
        modified_urls.append(modified_url)
    # 返回修改后的 URL 列表
    return modified_urls

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

# 创建一个空列表用于存储结果
results = []
for url in urls:
    # 发送 GET 请求获取 URL 的内容
    response = requests.get(url)
    # 获取响应的文本内容
    page_content = response.text

    # 查找所有符合指定格式的网址
    pattern = r"http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"   # 设置匹配的格式,如 http://8.8.8.8:8888
    # 使用正则表达式在页面内容中查找所有符合格式的 URL
    urls_all = re.findall(pattern, page_content)
    # urls = list(set(urls_all))  # 去重得到唯一的URL列表
    urls = set(urls_all)  # 去重得到唯一的URL列表
    x_urls = []
    for url in urls:  # 对urls进行处理,ip第四位修改为1,并去重
        url = url.strip()
        # 找到 URL 中 IP 地址开始的索引位置，"//" 后两个字符开始为 IP 地址起始位置
        ip_start_index = url.find("//") + 2
        # 找到 URL 中 IP 地址结束的索引位置，从 ip_start_index 开始查找第一个 ":" 的位置
        ip_end_index = url.find(":", ip_start_index)
        # 找到 IP 地址中第一个 "." 的位置
        ip_dot_start = url.find(".") + 1
        # 找到 IP 地址中第二个 "." 的位置
        ip_dot_second = url.find(".", ip_dot_start) + 1
        # 找到 IP 地址中第三个 "." 的位置
        ip_dot_three = url.find(".", ip_dot_second) + 1
        # 获取 URL 的基础部分，即从开头到 IP 地址开始的部分
        base_url = url[:ip_start_index]  # http:// or https://
        # 获取 URL 中的 IP 地址部分，截取到第三个 "." 的位置
        ip_address = url[ip_start_index:ip_dot_three]
        # 获取 URL 中的端口部分
        port = url[ip_end_index:]
        # 定义一个字符串，表示 IP 地址的结尾部分为 "1"
        ip_end = "1"
        # 修改 IP 地址的最后一位为 "1"
        modified_ip = f"{ip_address}{ip_end}"
        # 组合成新的 URL
        x_url = f"{base_url}{modified_ip}{port}"
        # 将新的 URL 添加到列表中
        x_urls.append(x_url)
    urls = set(x_urls)  # 去重得到唯一的URL列表
    valid_urls = []
    #   多线程获取可用url
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = []
        for url in urls:
            url = url.strip()
            # 获取修改后的 URL 列表
            modified_urls = modify_urls(url)
            for modified_url in modified_urls:
                # 提交任务，检查每个修改后的 URL 是否可访问
                futures.append(executor.submit(is_url_accessible, modified_url))
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                # 如果 URL 可访问，将其添加到有效 URL 列表中
                valid_urls.append(result)
    for url in valid_urls:
        print(url)
    # 遍历网址列表,获取JSON文件并解析
    for url in valid_urls:
        try:
            # 发送GET请求获取JSON文件,设置超时时间为0.5秒
            json_url = f"{url}"
            response = requests.get(json_url, timeout=3)################################
            json_data = response.content.decode('utf-8')
            try:
                    # 按行分割数据
             lines = json_data.split('\n')
             excluded_keywords = ['udp', 'rtp']   
             for line in lines:
                 if 'hls' in line and all(keyword not in line for keyword in excluded_keywords):
                        line = line.strip()
                        if line:
                            name, channel_url = line.split(',')
                            urls = channel_url.split('/', 3)
                            url_data = json_url.split('/', 3)
                            if len(urls) >= 3:
                                urld = (f"{urls[0]}//{url_data[2]}/{urls[3]}")
                            else:
                                urld = (f"{urls}")
                            #print(f"{name},{urld}")  #关闭频道名称和频道地址打印，缩短运行时间

 #####################################################################################################################################                               
                        if name and urld:
                            name = name.replace("", "")
                            urld = urld.replace("index.m3u8", "index.m3u8?$智慧光迅听说名字越长越好看")
                            results.append(f"{name},{urld}")
            except:
                continue
        except:
            continue
channels = []
for result in results:
    line = result.strip()
    if result:
        channel_name, channel_url = result.split(',')
        channels.append((channel_name, channel_url))
with open("iptv.txt", 'w', encoding='utf-8') as file:
    for result in results:
        file.write(result + "\n")
        print(result)  #关闭频道名称和频道地址打印，缩短运行时间
print("频道列表文件iptv.txt获取完成！")




######################################################################################################################
#定义智慧桌面采集地址
urls = [
    #"https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0i5rKz5YyXIg%3D%3D",  #河北
    #"https://fofa.info/result?qbase64=Ym9keV9oYXNoPSI0OTQ5NTY3NTki",   #body_hash="494956759"
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0ic2ljaHVhbiIgJiYgY2l0eT0ibWlhbnlhbmci",  #四川绵阳
    #"https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHJlZ2lvbj0i5rKz5Y2XIg%3D%3D",  # 河南
    #"https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHBvcnQ9IjgwOTYi",  # 8096
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHBvcnQ9Ijk5MDEi",  # 9901
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHBvcnQ9Ijk5MDIi",  # 9902
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIGNpdHk9Inl1bGluIg==",  #玉林
    "https://fofa.info/result?qbase64=ImlwdHYvbGl2ZS96aF9jbi5qcyIgJiYgY291bnRyeT0iQ04iICYmIHBvcnQ9IjgxODEii",#8181
]
def modify_urls(url):
    modified_urls = []
    ip_start_index = url.find("//") + 2
    ip_end_index = url.find(":", ip_start_index)
    base_url = url[:ip_start_index]
    ip_address = url[ip_start_index:ip_end_index]
    port = url[ip_end_index:]
    ip_end = "/iptv/live/1000.json?key=txiptv"
    for i in range(1, 256):
        modified_ip = f"{ip_address[:-1]}{i}"
        modified_url = f"{base_url}{modified_ip}{port}{ip_end}"
        modified_urls.append(modified_url)
    return modified_urls

def is_url_accessible(url):
    try:
        response = requests.get(url, timeout=3)
        if 200 <= response.status_code <= 401:
            return url
    except requests.exceptions.RequestException:
        pass
    return None

results = []
for url in urls:
    response = requests.get(url)
    page_content = response.text
    # 查找所有符合指定格式的网址
    pattern = r"http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"  # 设置匹配的格式,如http://8.8.8.8:8888
    urls_all = re.findall(pattern, page_content)
    # urls = list(set(urls_all))  # 去重得到唯一的URL列表
    urls = set(urls_all)  # 去重得到唯一的URL列表
    x_urls = []
    for url in urls:  # 对urls进行处理,ip第四位修改为1,并去重
        url = url.strip()
        ip_start_index = url.find("//") + 2
        ip_end_index = url.find(":", ip_start_index)
        ip_dot_start = url.find(".") + 1
        ip_dot_second = url.find(".", ip_dot_start) + 1
        ip_dot_three = url.find(".", ip_dot_second) + 1
        base_url = url[:ip_start_index]  # http:// or https://
        ip_address = url[ip_start_index:ip_dot_three]
        port = url[ip_end_index:]
        ip_end = "1"
        modified_ip = f"{ip_address}{ip_end}"
        x_url = f"{base_url}{modified_ip}{port}"
        x_urls.append(x_url)
    urls = set(x_urls)  # 去重得到唯一的URL列表
    valid_urls = []
    #   多线程获取可用url
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = []
        for url in urls:
            url = url.strip()
            modified_urls = modify_urls(url)
            for modified_url in modified_urls:
                futures.append(executor.submit(is_url_accessible, modified_url))
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                valid_urls.append(result)
    for url in valid_urls:
        print(url)

    # 遍历网址列表,获取JSON文件并解析
    for url in valid_urls:
        try:
            ip_start_index = url.find("//") + 2
            # 找到URL中"//"的位置，并从该位置的下一个字符开始截取，直到找到第一个"/"字符
            ip_dot_start = url.find(".") + 1
            # 从URL中找到第一个"."的位置，并从该位置的下一个字符开始截取，直到找到第二个"/"字符
            ip_index_second = url.find("/", ip_dot_start)
            base_url = url[:ip_start_index]  # 截取URL中的协议部分，例如"http://"或"https://"
            # 截取从"//"之后到第一个"/"之前的部分，这通常是IP地址或域名
            ip_address = url[ip_start_index:ip_index_second]
            # 构造一个新的URL，由基本URL和IP地址组成
            url_x = f"{base_url}{ip_address}"
            # 将原始URL赋值给json_url变量
            json_url = f"{url}"
            # 使用requests库发起一个GET请求到json_url，超时时间设置为3秒
            response = requests.get(json_url, timeout=3)
            # 将响应的内容解析为JSON格式
            json_data = response.json()
            try:
            # 尝试执行以下代码块，如果发生错误则跳转至except部分
                # 解析JSON文件，获取'data'键对应的列表中的每个元素
                for item in json_data['data']:
                    # 检查每个元素是否为字典类型
                    if isinstance(item, dict):
                        # 从字典中获取'name'键的值，如果键不存在则返回None
                        name = item.get('name')
                        # 从字典中获取'url'键的值，如果键不存在则返回None
                        urlx = item.get('url')
                        # 如果urlx包含'udp'或'rtp'字符串，则跳过当前循环的剩余部分
                        if 'udp' in urlx or 'rtp' in urlx:
                            continue  # 跳过包含'udp'或'rtp'的url
                        # 如果urlx以'http'开头，则直接使用这个url
                        if 'http' in urlx:
                            urld = f"{urlx}"
                        # 如果urlx不以'http'开头，则在前面添加一个前缀（注意：这里的url_x变量未在代码中定义）
                        else:
                            urld = f"{url_x}{urlx}"
                        #print(f"{name},{urld}")  #关闭频道名称和频道地址打印，缩短运行时间
                        if name and urld:
                            urld = urld.replace("key", "$不见黄河心不死") #key=txiptv&playlive=1&down=1  key=txiptv&playlive=0&authid=0  key=txiptv&playlive=1&authid=0
                            results.append(f"{name},{urld}")
            except:
                continue
        except:
            continue
channels = []
for result in results:
    line = result.strip()
    if result:
        channel_name, channel_url = result.split(',')
        channels.append((channel_name, channel_url))
with open("iptv.txt", 'a', encoding='utf-8') as file:
    for result in results:
        file.write(result + "\n")
        print(result)  #关闭频道名称和频道地址打印，缩短运行时间
print("频道列表文件iptv.txt追加写入成功！")




################################################按网址去除重复行#####
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
            urls = re.findall(r'[https]?[http]?[P2p]?[mitv]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', line)
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
remove_duplicates('iptv.txt', 'iptv.txt')



