import requests
import os
from lxml import etree

# 定义请求头
header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

# 验证tonkiang可用IP
def via_tonking(url):
    headers = {
        'Referer': 'http://tonkiang.us/hotellist.html',
        'User-Agent': header["User-Agent"],
    }
    try:
        response = requests.get(
            url=f'http://tonkiang.us/alllist.php?s={url}&c=false&y=false',
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        et = etree.HTML(response.text)
        div_text = et.xpath('//div[@class="result"]/div/text()')[1]
        return "暂时失效" not in div_text
    except Exception as e:
        print(f"验证IP时发生错误: {e}")
        return False

# 从tonkiang获取可用IP
def get_tonkiang(keyword):
    data = {
        "saerch": f"{keyword}",
        "Submit": " "
    }
    try:
        resp = requests.post(
            "http://tonkiang.us/hoteliptv.php",
            headers=header,
            data=data,
            timeout=10
        )
        resp.raise_for_status()
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
    except Exception as e:
        print(f"获取IP时发生错误: {e}")
        return []

def gen_files(valid_ips, province, isp):
    # 生成节目列表 省份运营商.txt
    index = 0
    print(valid_ips)
    udp_filename = f'rtp/{province}_{isp}.txt'
    with open(udp_filename, 'r', encoding='utf-8') as file:
        data = file.read()
    txt_filename = f'playlist/{province}{isp}.txt'
    with open(txt_filename, 'a', encoding='utf-8') as new_file:
        new_file.write(f'{province}{isp},#genre#\n')
        for url in valid_ips:
            if index < 10:
                # 确保 url 是一个完整的 URL 字符串，并且以 'http://' 开头
                base_url = "rtp://"
                if not url.startswith("http://"):
                    url = "http://" + url  # 如果 url 不是以 'http://' 开头，则添加它
                new_data = data.replace(base_url, url + "/rtp/")  # 替换并添加斜杠
                new_file.write(new_data.replace(" ", ""))  # 替换后去掉末尾的空格
                new_file.write('\n')
                index += 1
            else:
                break  # 替换 continue 为 break，因为你只需要前10个 IP
    print(f'已生成播放列表，保存至{txt_filename}')

# 遍历rtp文件夹中的所有文件
rtp_folder = 'rtp'
playlist_folder = 'playlist'

# 确保playlist目录存在
os.makedirs(playlist_folder, exist_ok=True)

for filename in os.listdir(rtp_folder):
    if filename.endswith(".txt"):
        province_isp = filename[:-4]  # 获取不包含扩展名的文件名
        keyword = province_isp.replace('_', '')  # 假设文件名格式为"省份_运营商"
        valid_ips = get_tonkiang(keyword)  # 搜索有效IP
        if valid_ips:
            print(f"找到有效IP，正在生成文本文件: {province_isp}")
            gen_files(valid_ips, province_isp.split('_')[0], province_isp.split('_')[1])  # 生成文本文件
        else:
            print(f"未找到有效IP: {province_isp}")
