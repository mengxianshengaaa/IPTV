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
# 扫源测绘空间地址
# 搜素关键词："iptv/live/zh_cn.js" && country="CN" && region="Hunan" && city="changsha"
# 搜素关键词："ZHGXTV" && country="CN" && region="Hunan" && city="changsha"
#"isShowLoginJs"智能KUTV管理
######################################################################################################################
######################################################################################################################
###########################################################ZHGX采集####################################################
######################################################################################################################
######################################################################################################################
urls = [
    "https://fofa.info/result?qbase64=IlpIR1hUViIgJiYgcmVnaW9uPSJndWFuZ2Rvbmci",#广东
    "https://fofa.info/result?qbase64=IlpIR1hUViIgJiYgcmVnaW9uPSJIdW5hbiI%3D",#湖南
    "https://fofa.info/result?qbase64=Ym9keT0i5pm65oWn5YWJ6L%2BFIg%3D%3D",#body="智慧光迅"
    "https://fofa.info/result?qbase64=c2VydmVyPSJuZ2lueCI%3D",#河南#
    "https://fofa.info/result?qbase64=IlpIR1hUViIgJiYgcmVnaW9uPSJoZWJlaSI%3D",#河北#
]
#定义网址替换规则
def modify_urls(url):
    modified_urls = []
    ip_start_index = url.find("//") + 2
    ip_end_index = url.find(":", ip_start_index)
    base_url = url[:ip_start_index]  # http:// or https://
    ip_address = url[ip_start_index:ip_end_index]
    port = url[ip_end_index:]
    ip_end = "/ZHGXTV/Public/json/live_interface.txt"
    for i in range(1, 256):
        modified_ip = f"{ip_address[:-1]}{i}"
        modified_url = f"{base_url}{modified_ip}{port}{ip_end}"
        modified_urls.append(modified_url)
    return modified_urls
#定义超时时间以及是否返回正确的状态码
def is_url_accessible(url):
    try:
        response = requests.get(url, timeout=1)          #//////////////////
        #if response.status_code == 200:
        if 200 <= response.status_code <= 401:
            return url
    except requests.exceptions.RequestException:
        pass
    return None
results = []
for url in urls:
    # 创建一个Chrome WebDriver实例
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    # 使用WebDriver访问网页
    driver.get(url)  # 将网址替换为你要访问的网页地址
    time.sleep(10)
    # 获取网页内容
    page_content = driver.page_source
    # 关闭WebDriver
    driver.quit()


# 查找所有符合指定格式的网址，使用正则表达式匹配页面内容中的URL
pattern = r"http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"  # 设置匹配的格式，如http://8.8.8.8:8888
urls_all = re.findall(pattern, page_content)  # 使用findall方法查找所有匹配的URL
# 使用set去除重复的URL，得到唯一的URL列表
urls = set(urls_all)
# 初始化一个空列表，用于存储处理后的URL
x_urls = []
# 遍历去重后的URL列表
for url in urls:
    # 去除URL前后的空白字符
    url = url.strip()
    # 找出URL中"http://"后面直到":"之间的部分（即IP地址部分）
    ip_start_index = url.find("//") + 2
    ip_end_index = url.find(":", ip_start_index)
    # 找出IP地址中各八位字节的位置
    ip_dot_start = url.find(".") + 1
    ip_dot_second = url.find(".", ip_dot_start) + 1
    ip_dot_three = url.find(".", ip_dot_second) + 1
    # 提取协议头部（http://或https://）
    base_url = url[:ip_start_index]
    # 提取IP地址
    ip_address = url[ip_start_index:ip_dot_three]
    # 提取端口号
    port = url[ip_end_index:]
    # 将IP地址的最后一部分修改为"1"，生成新的IP地址
    ip_end = "1"
    modified_ip = f"{ip_address[:-1]}{ip_end}"
    # 构造新的URL
    x_url = f"{base_url}{modified_ip}{port}"
    # 将新的URL添加到列表中
    x_urls.append(x_url)
# 再次使用set去除重复的URL，得到最终的唯一URL列表
urls = set(x_urls)
# 初始化一个空列表，用于存储验证后的可访问URL
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
        # 发送GET请求获取JSON文件,设置超时时间为0.5秒
        response = requests.get(url, timeout=0.5)
        json_data = response.content.decode('utf-8')

        # 按行分割数据
        lines = json_data.split('\n')
        for line in lines:
            # 行中需包含hls，但排除udp和rtp
            if 'hls' in line and ('udp' not in line and 'rtp' not in line):
                line = line.strip()
                if line:
                    # 分割行以获取频道名和原始URL
                    name, channel_url = line.split(',')
                    
                    # 解析json_url以提取IP和端口
                    parsed_json_url = urlparse(url)
                    json_ip = parsed_json_url.hostname
                    json_port = ':' + parsed_json_url.port if parsed_json_url.port else ''
                    
                    # 替换原始URL中的IP地址和端口为json_url中的IP地址和端口
                    new_channel_url = channel_url.replace(channel_url.split('/')[2], json_ip)
                    if json_port:  # 如果json_url中有端口号，也进行替换
                        new_channel_url = new_channel_url.replace(f":{channel_url.split(':')[1]}", json_port)
                    
                    # 构造新的行并打印
                    new_line = f"{name},{new_channel_url}"
                    print(new_line)  # 打印新的行
                    
                    # 写入到文件中
                    with open('iptv.txt', 'a', encoding='utf-8') as outfile:
                        outfile.write(new_line + '\n')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching or processing the JSON data: {e}")
print("频道列表文件iptv.txt获取完成！")
