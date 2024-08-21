import requests
import re
from lxml import etree
import os

# 定义代理
proxy = {
    'http': 'http://139.9.119.20:80',
    'https': 'http://139.9.119.20:80',  # 注意：根据实际代理是否支持https进行设置
}
# 验证tonkiang可用IP
def via_tonking(url):
    headers = {
        'Referer': 'http://tonkiang.us/hotellist.html',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }
    url = f'http://tonkiang.us/alllist.php?s={url}&c=false&y=false'
    response = requests.get(
        url=url,
        headers=headers,
        verify=False,  # 注意：verify=False会忽略SSL证书验证
        proxies=proxy,   # 这里使用之前定义的代理
        timeout=10
    )
    et = etree.HTML(response.text)
    div_text = et.xpath('//div[@class="result"]/div/text()')[1]
    return "暂时失效" not in div_text

# 从tonkiang获取可用IP
def get_tonkiang(key_words):
    result_urls = []
    data = {
        "saerch": f"{key_words}",
        "Submit": " "
    }
    url = "http://tonkiang.us/hoteliptv.php"
    resp = requests.post(
        url=url,
        headers=header,
        data=data,
        timeout=10,
        proxies=proxy  # 这里使用之前定义的代理
    )
    resp.encoding = 'utf-8'
    et = etree.HTML(resp.text)
    divs = et.xpath('//div[@class="tables"]/div')
    for div in divs:
        try:
            status = div.xpath('./div[3]/div/text()')[0]
            if "暂时失效" not in status:
                url = div.xpath('./div[1]/a/b/text()')[0]
                url = url.strip()
                if via_tonking(url):
                    result_urls.append(f'http://{url}')
        except:
            pass
    return result_urls

# 生成文件
def gen_files(valid_ips, province, isp):
    udp_filename = f'rtp/{province}_{isp}.txt'
    with open(udp_filename, 'r', encoding='utf-8') as file:
        data = file.read()
    txt_filename = f'playlist/{province}{isp}.txt'
    with open(txt_filename, 'a', encoding='utf-8') as new_file:
        new_file.write(f'{province}{isp},#genre#\n')
        for url in valid_ips:
            new_data = data.replace("rtp://", f"{url[0]}/rtp/")
            new_file.write(new_data)
            new_file.write('\n')
    print(f'已生成播放列表，保存至{txt_filename}')
