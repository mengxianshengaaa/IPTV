import requests
import re
from lxml import etree
import os

import requests
import re
from lxml import etree
import os

# 定义代理
proxy = {
    'http': 'http://139.9.119.20:80',
    'https': 'http://139.9.119.20:80',
}

# 定义请求头
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

# 验证tonkiang可用IP
def via_tonking(url):
    headers = {
        'Referer': 'http://tonkiang.us/hotellist.html',
        'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)',
    }
    url = f'http://tonkiang.us/alllist.php?s={url}&c=false&y=false'
    response = requests.get(
        url=url,
        headers=headers,
        verify=False,
        proxies=proxy,
        timeout=10
    )
    et = etree.HTML(response.text)
    div_text = et.xpath('//div[@class="result"]/div/text()')[1]
    return "暂时失效" not in div_text

# 从tonkiang获取可用IP
def get_tonkiang(keyword):
    # 构造POST数据
    data = {
        "saerch": f"{keyword}",
        "Submit": " "
    }
    resp = requests.post(
        "http://tonkiang.us/hoteliptv.php",
        headers=header,
        data=data,
        timeout=10,
        proxies=proxy
    )
    resp.encoding = 'utf-8'
    et = etree.HTML(resp.text)
    divs = et.xpath('//div[@class="tables"]/div')
    result_urls = []
    for div in divs:
        try:
            status = div.xpath('./div[3]/div/text()')[0]
            if "暂时失效" not in status:
                ip = div.xpath('./div[1]/a/b/text()')[0].strip()
                if via_tonking(ip):
                    result_urls.append(f'http://{ip}')
        except (IndexError, ValueError):
            continue
    return result_urls

# 生成文件
def gen_files(valid_ips, province, isp):
    udp_filename = f'rtp/{province}_{isp}.txt'
    txt_filename = f'playlist/{province}{isp}.txt'
    try:
        with open(udp_filename, 'r', encoding='utf-8') as file:
            data = file.read()
        with open(txt_filename, 'a', encoding='utf-8') as new_file:  # 修改为'a'以追加文件
            for url in valid_ips:
                new_data = data.replace("rtp://", f"{url}/rtp/")
                new_file.write(new_data)
    except FileNotFoundError:
        print(f"文件 '{udp_filename}' 不存在.")
    except Exception as e:
        print(f"生成文件时发生错误: {e}")

# 遍历rtp文件夹中的所有文件
rtp_folder = 'rtp'
playlist_folder = 'playlist'

for filename in os.listdir(rtp_folder):
    if filename.endswith(".txt") and "_" in filename:
        province, isp = filename[:-4].split("_")  # 假设文件名格式为"省份_运营商.txt"
        key_word = f"{province}{isp}"  # 构造关键词
        valid_ips = get_tonkiang(key_word)  # 搜索有效IP
        if valid_ips:
            print(f"找到有效IP，正在生成播放列表: {province}{isp}")
            gen_files(valid_ips, province, isp)  # 生成播放列表文件
        else:
            print(f"未找到有效IP: {province} {isp}")
