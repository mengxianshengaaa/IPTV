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

urls = [
    "https://fofa.info/result?qbase64=IlpIR1hUViIgJiYgcmVnaW9uPSJndWFuZ2Rvbmci",  # 广东
    "https://fofa.info/result?qbase64=IlpIR1hUViIgJiYgcmVnaW9uPSJIdW5hbiI%3D",  # 湖南
    "https://fofa.info/result?qbase64=Ym9keT0i5pm65oWn5YWJ6L%2BFIg%3D%3D",  # body="智慧光迅"
    "https://fofa.info/result?qbase64=c2VydmVyPSJuZ2lueCI%3D",  # 河南
    "https://fofa.info/result?qbase64=IlpIR1hUViIgJiYgcmVnaW9uPSJoZWJlaSI%3D",  # 河北
]


# 定义网址替换规则
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


# 定义超时时间以及是否返回正确的状态码
def is_url_accessible(url):
    try:
        response = requests.get(url, timeout=1)
        if 200 <= response.status_code <= 401:
            return url
    except requests.exceptions.RequestException as e:
        print(f"Error checking {url}: {e}")
    return None


results = []
for url in urls:
    # 创建一个 Chrome WebDriver 实例
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    try:
        # 使用 WebDriver 访问网页
        driver.get(url)
        time.sleep(10)
        # 获取网页内容
        page_content = driver.page_source
        # 关闭 WebDriver
        driver.quit()
        # 查找所有符合指定格式的网址
        pattern = r"http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+"
        urls_all = re.findall(pattern, page_content)
        urls = set(urls_all)
        x_urls = []
        for url in urls:
            url = url.strip()
            ip_start_index = url.find("//") + 2
            ip_end_index = url.find(":", ip_start_index)
            ip_dot_start = url.find(".") + 1
            ip_dot_second = url.find(".", ip_dot_start) + 1
            ip_dot_three = url.find(".", ip_dot_second) + 1
            base_url = url[:ip_start_index]
            ip_address = url[ip_start_index:ip_dot_three]
            port = url[ip_end_index:]
            ip_end = "1"
            modified_ip = f"{ip_address}{ip_end}"
            x_url = f"{base_url}{modified_ip}{port}"
            x_urls.append(x_url)
        urls = set(x_urls)
        valid_urls = []
        # 多线程获取可用 url
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
        # 遍历网址列表，获取 JSON 文件并解析
        for url in valid_urls:
            try:
                json_url = f"{url}"
                response = requests.get(json_url, timeout=1)
                json_data = response.content.decode('utf-8')
                try:
                    lines = json_data.split('\n')
                    for line in lines:
                        if 'hls' in line and ('udp' not in line or 'rtp' not in line):
                            line = line.strip()
                            if line:
                                name, channel_url = line.split(',')
                                urls = channel_url.split('/', 3)
                                url_data = json_url.split('/', 3)
                                ip_port = url_data[2]
                                urls[2] = urls[2].replace(urls[2].split('/')[2].split(':')[0], ip_port.split(':')[0])
                                urls[2] = urls[2].replace(urls[2].split('/')[2].split(':')[1], ip_port.split(':')[1])
                                if len(urls) >= 4:
                                    urld = (f"{urls[0]}//{urls[2]}/{urls[3]}")
                                else:
                                    urld = (f"{urls[0]}//{urls[2]}")
                                with open('iptv.txt', 'a', encoding='utf-8') as outfile:
                                    outfile.write(f"{name},{urld}\n")
                except Exception as e:
                    print(f"Error processing line in JSON: {e}")
            except Exception as e:
                print(f"Error fetching JSON from {json_url}: {e}")
    except Exception as e:
        print(f"Error with URL {url}: {e}")

print("频道列表文件 iptv.txt 获取完成！")



