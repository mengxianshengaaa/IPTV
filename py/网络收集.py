from lxml import etree
import time
import datetime
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
       'https://dimaston.github.io/live.m3u',  #假m3u
       'http://rihou.cc:555/gggg.nzk',
       'https://raw.githubusercontent.com/gaotianliuyun/gao/master/list.txt',   #暂时保留
       'http://117.72.68.25:9230/latest.txt',
       'http://ttkx.live:55/lib/kx2024.txt',
       'https://raw.githubusercontent.com/kimwang1978/tvbox/main/%E5%A4%A9%E5%A4%A9%E5%BC%80%E5%BF%83/lives/%E2%91%AD%E5%BC%80%E5%BF%83%E7%BA%BF%E8%B7%AF.txt',
       'https://raw.githubusercontent.com/Fairy8o/IPTV/main/PDX-V4.txt',
       'http://gg.gg/cctvgg',
       'https://raw.githubusercontent.com/ddhola/file/d7afb504b1ba4fef31813e1166cb892215a9c063/0609test',
       'https://raw.githubusercontent.com/vbskycn/iptv/2738b3bec8c298f57e0e2052b155846ab6ea3787/dsyy/hd.txt',
       'https://raw.githubusercontent.com/frxz751113/AAAAA/main/IPTV/TW.txt',
       'https://github.com/ljlfct01/ljlfct01.github.io/blob/20d15728f71ab9dfca83e18593c0e3235c5a92b2/list.%E8%87%AA%E7%94%A8#L674',
       '',
       '',
       '',
       '',
       '',
       '',
       '',
       '',
       '',
       '',
       '',
       '',
       '',
       '',
       '',
       '',
       '',
       '',
       '',
       '',
       '',
       '',
       '',
       '',
       '',
       '',
       '',
       '',
       '',
       ''
]
# 合并文件的函数
def merge_txt_files(urls, output_filename='汇总.txt'):
    try:
        with open(output_filename, 'w', encoding='utf-8') as outfile:
            for url in urls:
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    outfile.write(response.text + '\n')
                except requests.RequestException as e:
                    print(f'Error downloading {url}: {e}')
    except IOError as e:
        print(f'Error writing to file: {e}')
# 调用函数
merge_txt_files(urls)







#简体转繁体
# 创建一个OpenCC对象,指定转换的规则为繁体字转简体字
converter = OpenCC('t2s.json')#繁转简
#converter = OpenCC('s2t.json')#简转繁
# 打开txt文件
with open('汇总.txt', 'r', encoding='utf-8') as file:
    traditional_text = file.read()
# 进行繁体字转简体字的转换
simplified_text = converter.convert(traditional_text)
# 将转换后的简体字写入txt文件
with open('汇总.txt', 'w', encoding='utf-8') as file:
    file.write(simplified_text)

