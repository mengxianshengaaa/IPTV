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
from translate import Translator

url = "https://raw.githubusercontent.com/Fairy8o/IPTV/main/PDX-V4.txt"          #源采集地址
r = requests.get(url)
open('源.txt','wb').write(r.content)   



# 使用with语句打开输入文件进行读取
with open("源.txt", 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 使用列表推导式过滤行
filtered_lines = [
    line for line in lines 
    if any(substr.lower() in line.lower() for substr in ['CCTV', '卫视', '4K', '4k', '8K', '影', '剧', '经典', 'TVB', '澳门', '龙华', '民视', '中视', '华视', 'AXN', 'MOMO', '采昌', '耀才', \
                                                         '靖天', '镜新闻', '靖洋', '莲花', '年代', '爱尔达', '好莱坞', '华丽', '非凡', '公视', '寰宇', '无线', 'EVEN', 'MoMo', '爆谷', '面包', 'momo', '唐人', \
                                                         '中华小', '三立', 'CNA', 'FOX', 'RTHK', 'Movie', '八大', '中天', '中视', '东森', '凤凰', '天映', '美亚', '环球', '翡翠', '亚洲', '大爱', '大愛', '明珠', \
                                                         '半岛', 'AMC', '龙祥', '台视', '1905', '纬来', '神话', '经典都市', '视界', '番薯', '私人', '酒店', 'TVB', '凤凰', '半岛', '星光视界', '番薯', '大愛', \
                                                         '新加坡', '星河', '明珠', '环球', '翡翠台', ' ELTV', '大立', 'elta', '好消息', '美国中文', '神州', '天良', '18台', 'BLOOMBERG', 'Bloomberg', 'CMUSIC', \
                                                         'CN卡通', 'CNBC', 'CNBC', 'CinemaWorld', 'Cinemax', 'DMAX', 'Dbox', 'Dreamworks', 'ESPN', 'Euronews', 'Eurosports1', 'FESTIVAL', 'GOOD2', 'HBO家庭', \
                                                         'HBO', 'HISTORY', 'HOY国际财经', 'HakkaTV', 'J2', 'KOREA', 'LISTENONSPOTIFY', 'LUXE', 'MCE', 'MTV', 'Now', 'PremierSports', 'ROCK', 'SPOTV', 'TiTV', \
                                                         'VOA', 'ViuTV', 'ViuTV6', 'WSport', 'WWE', '八度', '博斯', '达文西', '迪士尼', '动物星球', '港石金曲', '红牛', '互动英语', '华纳影视', '华语剧台', 'ELTV', \
                                                         '欢喜台', '旅游', '美食星球', 'nhkworld', 'nickjr', '千禧', '全球财经', '探案', '探索', '小尼克', '幸福空间', '影剧', '粤语片台', '智林', '猪哥亮']) 
    and not any(substr.lower() in line.lower() for substr in ['epg', 'mitv', 'udp', 'rtp', '[', 'P2P', 'p2p', 'P3P'])
]

# 使用with语句打开输出文件进行写入
with open("源.txt", 'w', encoding='utf-8') as output_file:
    output_file.writelines(filtered_lines)

print("文件过滤完成。")
#################################################### 对整理好的频道列表测试HTTP连接
def test_connectivity(url, max_attempts=1): #定义测试HTTP连接的次数
    # 尝试连接指定次数    
   for _ in range(max_attempts):  
    try:
        response = requests.head(url, timeout=1)  # 发送HEAD请求,仅支持V4,修改此行数字可定义链接超时##////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        #response = requests.get(url, timeout=0.3)  # 发送get请求,支持V6,修改此行数字可定义链接超时##############################//////////////////////////////////////////////////////////////////////////////////////
        return response.status_code == 200  # 返回True如果状态码为200
    except requests.RequestException:  # 捕获requests引发的异常
        pass  # 发生异常时忽略
   #return False  # 如果所有尝试都失败,返回False
   pass   
# 使用队列来收集结果的函数
def process_line(line, result_queue):
    parts = line.strip().split(",")  # 去除行首尾空白并按逗号分割
    if len(parts) == 2 and parts[1]:  # 确保有URL,并且URL不为空
        channel_name, channel_url = parts  # 分别赋值频道名称和URL
        if test_connectivity(channel_url):  # 测试URL是否有效
            result_queue.put((channel_name, channel_url, "有效"))  # 将结果放入队列
        else:
            result_queue.put((channel_name, channel_url, "无效"))  # 将结果放入队列
    else:
        # 格式不正确的行不放入队列
        pass
# 主函数
def main(source_file_path, output_file_path):
    with open(source_file_path, "r", encoding="utf-8") as source_file:  # 打开源文件
        lines = source_file.readlines()  # 读取所有行s     
    result_queue = queue.Queue()  # 创建队列
    threads = []  # 初始化线程列表
    for line in tqdm(lines, desc="检测进行中"):  # 显示进度条
        thread = threading.Thread(target=process_line, args=(line, result_queue))  # 创建线程
        thread.start()  # 启动线程
        threads.append(thread)  # 将线程加入线程列表
    for thread in threads:  # 等待所有线程完成
        thread.join()
    # 初始化计数器
    valid_count = 0
    invalid_count = 0
    with open(output_file_path, "w", encoding="utf-8") as output_file:  # 打开输出文件
        for _ in range(result_queue.qsize()):  # 使用队列的大小来循环
            item = result_queue.get()  # 获取队列中的项目
            # 只有在队列中存在有效的项目时才写入文件
            if item[0] and item[1]:  # 确保channel_name和channel_url都不为None
                output_file.write(f"{item[0]},{item[1]},{item[2]}\n")  # 写入文件
                if item[2] == "有效":  # 统计有效源数量
                    valid_count += 1
                else:  # 统计无效源数量
                    invalid_count += 1
    print(f"任务完成, 有效源数量: {valid_count}, 无效源数量: {invalid_count}")  # 打印结果
if __name__ == "__main__":
    try:
        source_file_path = "源.txt"  # 输入源文件路径
        output_file_path = "源1.txt"  # 设置输出文件路径
        main(source_file_path, output_file_path)  # 调用main函数
    except Exception as e:
        print(f"程序发生错误: {e}")  # 打印错误信息

#########################################################################提取源1中的有效行
def filter_lines(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:  # 打开文件
        lines = file.readlines()  # 读取所有行
    filtered_lines = []  # 初始化过滤后的行列表
    for line in lines:  # 遍历所有行
        if 'genre' in line or '有效' in line:  # 如果行中包含'genre'或'有效'
            filtered_lines.append(line)  # 将行添加到过滤后的行列表
    return filtered_lines  # 返回过滤后的行列表
def write_filtered_lines(output_file_path, filtered_lines):
    with open(output_file_path, 'w', encoding='utf-8') as output_file:  # 打开输出文件
        output_file.writelines(filtered_lines)  # 写入过滤后的行
if __name__ == "__main__":
    input_file_path = "源1.txt"  # 设置输入文件路径
    output_file_path = "源1.txt"  # 设置输出文件路径
    filtered_lines = filter_lines(input_file_path)  # 调用filter_lines函数
    write_filtered_lines(output_file_path, filtered_lines)  # 调用write_filtered_lines函数
###################################################################################定义替换规则的字典,对整行内的内容进行替换
replacements = {
    ",有效": "",  # 将",有效"替换为空字符串
    "#genre#,无效": "#genre#",  # 将"#genre#,无效"替换为"#genre#"
}
# 打开原始文件读取内容,并写入新文件
with open('源1.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()
# 创建新文件并写入替换后的内容
with open('源1.txt', 'w', encoding='utf-8') as new_file:
    for line in lines:
        for old, new in replacements.items():  # 遍历替换规则字典
            line = line.replace(old, new)  # 替换行中的内容
        new_file.write(line)  # 写入新文件
print("新文件已保存。")  # 打印完成信息
# 初始化优选字典
detected_ips = {}
# 存储文件路径
file_path = "源1.txt"
output_file_path = "优选.txt"
def get_ip_key(url):
    """从URL中提取IP地址,并构造一个唯一的键"""
    # 找到'//'到第三个'.'之间的字符串
    start = url.find('://') + 3  # '://'.length 是 3
    end = start
    dot_count = 0
    while dot_count < 3:
        end = url.find('.', end)
        if end == -1:  # 如果没有找到第三个'.',就结束
            break
        dot_count += 1
    return url[start:end] if dot_count == 3 else None
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
                # 尝试捕获5秒内的帧
                while frame_count < 220 and (time.time() - start_time) < 10:#//////////////////////////////////////////////////////////////////////////////////////###########
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frame_count += 1
                # 释放资源
                cap.release()
                # 根据捕获的帧数判断状态并记录结果#////////////////////////////////////////////////////////////////////////////////////////////////////////////////###########
                if frame_count >= 220:  #5秒内超过100帧则写入#/////////////////////////////////////////////////////////////////////////////////////////////////////###########
                    detected_ips[ip_key] = {'status': 'ok'}
                    output_file.write(line)  # 写入检测通过的行
                else:
                    detected_ips[ip_key] = {'status': 'fail'}
# 打印优选
for ip_key, result in detected_ips.items():
    print(f"IP Key: {ip_key}, Status: {result['status']}")

###############################################################################文本排序
# 打开原始文件读取内容，并写入新文件
with open('优选.txt', 'r', encoding='utf-8') as file:
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
with open('优选.txt', "w", encoding="utf-8") as file:
    for line in sorted_lines:
        file.write(line)
print(f"文件已排序并保存为新文件")

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
# 按类别提取关键词并写入文件
check_and_write_file('优选.txt',  'a0.txt',  keywords="央视频道, 8K, 4K, 4k")
check_and_write_file('优选.txt',  'a.txt',  keywords="央视频道, CCTV")
#check_and_write_file('优选.txt',  'a1.txt',  keywords="央视频道, 文物宝库, 风云音乐, 生活时尚, 台球, 网球, 足球, 女性, 地理, 纪实科教, 纪实人文, 兵器, 北京纪实, 发现, 法治")

check_and_write_file('优选.txt',  'b0.txt',  keywords="卫视频道, 湖北卫视, 湖南卫视, 江苏卫视, 安徽卫视, 凤凰卫视, 辽宁卫视")
check_and_write_file('优选.txt',  'b.txt',  keywords="卫视频道, 卫视")

check_and_write_file('优选.txt',  'c.txt',  keywords="影视频道, 爱情喜剧, 爱喜喜剧, 惊嫊悬疑, 东北热剧, 动作电影, 无名, 都市剧场, iHOT, 海外剧场, 欢笑剧场, 重温经典, 明星大片, 中国功夫, 军旅, 东北热剧, 中国功夫, 军旅剧场, 古装剧场, \
家庭剧场, 惊悚悬疑, 欢乐剧场, 潮妈辣婆, 爱情喜剧, 精品大剧, 影, 超级电影, 黑莓动画, 黑莓电影, 海外剧场, 精彩影视, 无名影视, 潮婆辣妈, 剧, 热播精选")
check_and_write_file('优选.txt',  'c1.txt',  keywords="影视频道, 求索动物, 求索, 求索科学, 求索记录, 爱谍战, 爱动漫, 爱科幻, 爱青春, 爱自然, 爱科学, 爱浪漫, 爱历史, 爱旅行, 爱奇谈, 爱怀旧, 爱赛车, 爱都市, 爱体育, 爱经典, \
爱玩具, 爱喜剧, 爱悬疑, 爱幼教, 爱院线")
check_and_write_file('优选.txt',  'c2.txt',  keywords="影视频道, 炫舞, 健康, 农业致富, 军事评论, 农业致富, 哒啵赛事, 怡伴健康, 武博世界, 超级综艺, 哒啵, HOT, 炫舞未来, 精品体育, 精品萌宠, 精品记录, 超级体育, 金牌, 武术世界, 精品纪录")

#check_and_write_file('优选.txt',  'd.txt',  keywords="少儿频道, 少儿, 卡通, 动漫, 宝贝, 哈哈")

check_and_write_file('优选.txt',  'e.txt',  keywords="港澳频道, TVB, 澳门, 龙华, 民视, 中视, 华视, AXN, MOMO, 采昌, 耀才, 靖天, 镜新闻, 靖洋, 莲花, 年代, 爱尔达, 好莱坞, 华丽, 非凡, 公视, 寰宇, 无线, EVEN, MoMo, 爆谷, 面包, momo, 唐人, \
中华小, 三立, CNA, FOX, RTHK, Movie, 八大, 中天, 中视, 东森, 凤凰, 天映, 美亚, 环球, 翡翠, 亚洲, 大爱, 大愛, 明珠, 半岛, AMC, 龙祥, 台视, 1905, 纬来, 神话, 经典都市, 视界, 番薯, 私人, 酒店, TVB, 凤凰, 半岛, 星光视界, \
番薯, 大愛, 新加坡, 星河, 明珠, 环球, 翡翠台,  ELTV, 大立, elta, 好消息, 美国中文, 神州, 天良, 18台, BLOOMBERG, Bloomberg, CMUSIC, CN卡通, CNBC, CNBC, CinemaWorld, Cinemax, DMAX, Dbox, Dreamworks, ESPN, Euronews, \
Eurosports1, FESTIVAL, GOOD2, HBO家庭, HBO, HISTORY, HOY国际财经, HakkaTV, J2, KOREA, LISTENONSPOTIFY, LUXE, MCE, MTV, Now, PremierSports, ROCK, SPOTV, TiTV, VOA, ViuTV, ViuTV6, WSport, WWE, 八度, 博斯, 达文西, 迪士尼, \
动物星球, 港石金曲, 红牛, 互动英语, 华纳影视, 华语剧台, ELTV, 欢喜台, 旅游, 美食星球, nhkworld, nickjr, 千禧, 全球财经, 探案, 探索, 小尼克, 幸福空间, 影剧, 粤语片台, 智林, 猪哥亮")




###############################################################################################################################################################################################################################
##############################################################对生成的文件进行合并
file_contents = []
file_paths = ["a0.txt", "a.txt", "a1.txt", "b0.txt", "b.txt", "c.txt", "c1.txt", "c2.txt", "d.txt", "f0.txt", "f.txt", "f1.txt", "g0.txt", "g.txt", "g1.txt", "h0.txt", "h.txt", "h1.txt", "i.txt", \
              "i1.txt", "j.txt", "j1.txt", "k.txt", "l0.txt", "l.txt", "l1.txt", "m.txt", "m1.txt",  \
              "n0.txt","n.txt","n1.txt", "e.txt", "o1.txt", "o.txt"]  # 替换为实际的文件路径列表
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
with open('网络优选.txt', 'w', encoding="utf-8") as file:
 file.writelines(unique_lines)
#任务结束,删除不必要的过程文件
files_to_remove = ['源.txt', "源1.txt", "去重.txt", "a0.txt", "a.txt", "a1.txt", "b0.txt", "b.txt", "c.txt", "c1.txt", "c2.txt", "d.txt", "f0.txt", "f.txt", "f1.txt", "g0.txt", "g.txt", "g1.txt", "h0.txt", "h.txt", "h1.txt", "i.txt", \
              "i1.txt", "j.txt", "j1.txt", "k.txt", "l0.txt", "l.txt", "l1.txt", "m.txt", "m1.txt",  \
              "n0.txt","n.txt","n1.txt", "e.txt", "o1.txt", "o.txt", "优选.txt"]
for file in files_to_remove:
    if os.path.exists(file):
        os.remove(file)
    else:              # 如果文件不存在,则提示异常并打印提示信息
        print(f"文件 {file} 不存在,跳过删除。")
print("任务运行完毕,优选频道列表可查看文件夹内txt文件！")
