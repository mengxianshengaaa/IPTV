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

print('对playlist文件夹里面的所有txt文件进行去重处理')
def remove_duplicates_keep_order(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            lines = set()
            unique_lines = []
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    if line not in lines:
                        unique_lines.append(line)
                        lines.add(line)
            # 将保持顺序的去重后的内容写回原文件
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(unique_lines)
# 使用示例
folder_path = 'playlist'  # 替换为你的文件夹路径
remove_duplicates_keep_order(folder_path)
print('文件去重完成！移除存储的旧文件！')

###############检测playlist文件夹内所有txt文件内的组播
###############检测playlist文件夹内所有txt文件内的组播
###############检测playlist文件夹内所有txt文件内的组播

import os
import cv2
import time
from tqdm import tqdm
import sys

# 初始化字典以存储IP检测结果
detected_ips = {}

def get_ip_key(url):
    """从URL中提取IP地址，并构造一个唯一的键"""
    start = url.find('://') + 3
    end = url.find('/', start)
    if end == -1:
        end = len(url)
    return url[start:end].strip()

# 设置固定的文件夹路径
folder_path = 'playlist'

# 确保文件夹路径存在
if not os.path.isdir(folder_path):
    print("指定的文件夹不存在。")
    sys.exit()

# 遍历文件夹中的所有.txt文件
for filename in os.listdir(folder_path):
    if filename.endswith('.txt'):
        file_path = os.path.join(folder_path, filename)
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # 准备写回文件
        with open(file_path, 'w', encoding='utf-8') as output_file:
            # 使用 tqdm 显示进度条
            for line in tqdm(lines, total=len(lines), desc=f"Processing {filename}"):
                parts = line.split(',', 1)
                if len(parts) >= 2:
                    channel_name, url = parts
                    channel_name = channel_name.strip()
                    url = url.strip()
                    ip_key = get_ip_key(url)
                    
                    # 检查IP是否已经被检测过
                    if ip_key in detected_ips:
                        # 如果之前检测成功，则写入该行
                        if detected_ips[ip_key]['status'] == 'ok':
                            output_file.write(line)
                        continue  # 无论之前检测结果如何，都不重新检测
                    
                    # 初始化帧计数器和成功标志
                    frame_count = 0
                    success = False
                    # 尝试打开视频流
                    cap = cv2.VideoCapture(url)
                    start_time = time.time()
                    while (time.time() - start_time) < 5:
                        ret, frame = cap.read()
                        if not ret:
                            break
                        frame_count += 1
                        # 如果在3秒内读取到60帧以上，设置成功标志
                        if frame_count >= 5:
                            success = True
                            break
                    cap.release()
                    
                    # 根据检测结果更新字典
                    if success:
                        detected_ips[ip_key] = {'status': 'ok'}
                        output_file.write(line)
                    else:
                        detected_ips[ip_key] = {'status': 'fail'}

# 打印检测结果
for ip_key, result in detected_ips.items():
    print(f"IP Key: {ip_key}, Status: {result['status']}")
