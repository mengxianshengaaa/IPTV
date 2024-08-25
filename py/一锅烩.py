from lxml import etree
import time
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
    'https://raw.githubusercontent.com/kimwang1978/tvbox/main/%E5%A4%A9%E5%A4%A9%E5%BC%80%E5%BF%83/lives/%E2%91%AD%E5%BC%80%E5%BF%83%E7%BA%BF%E8%B7%AF.txt',#################
    'https://raw.githubusercontent.com/pxiptv/live/main/iptv.txt', #ADD 【2024-08-02 16:48:40】#每日更新1次
    'https://notabug.org/vnjd/yydu/raw/master/yyfug.txt', #ADD 【2024-08-06】
    'https://tvkj.top/tvlive.txt', #ADD 【2024-08-06】
    'https://pan.beecld.com/f/OXMcA/%E6%98%A5%E8%B5%A2%E5%A4%A9%E4%B8%8B.txt', #ADD 【2024-08-06】
    'http://kxrj.site:55/lib/kx2024.txt',   #ADD 【2024-08-07】
    'https://raw.githubusercontent.com/yuanzl77/IPTV/main/live.txt',   #ADD 2024-08-05 每天更新一次，量太多转到blacklist处理
    'https://wzsvip.github.io/ipv4.txt',   #ADD 【2024-08-08】
    'http://wz.42web.io/ipv4.txt',   #ADD 【2024-08-08】
    'http://ttkx.live:55/lib/kx2024.txt',   #ADD 【2024-08-10】每日更新3次，移动到main.py
    'http://mywlkj.ddns.net:5212/f/EErCL/%E5%8F%B0%E6%B9%BE%E7%94%B5%E8%A7%86TV.txt',   #ADD 【2024-08-10】
    'https://raw.githubusercontent.com/Guovin/TV/gd/result.txt', #每天自动更新1次
    'https://raw.githubusercontent.com/ssili126/tv/main/itvlist.txt', #每天自动更新1次
    'https://raw.githubusercontent.com/mlvjfchen/TV/main/iptv_list.txt', #每天早晚各自动更新1次 2024-06-03 17:50
    'https://raw.githubusercontent.com/fenxp/iptv/main/live/ipv6.txt',  #1小时自动更新1次11:11 2024/05/13
    'https://raw.githubusercontent.com/fenxp/iptv/main/live/tvlive.txt', #1小时自动更新1次11:11 2024/05/13
    'https://raw.githubusercontent.com/zwc456baby/iptv_alive/master/live.txt',  #每天自动更新1次 2024-06-24 16:37
    'http://ttkx.live:55/lib/kx2024.txt', #ADD 2024-08-11 每天更新3次
    'https://raw.githubusercontent.com/vbskycn/iptv/master/tv/iptv4.txt', #ADD 2024-08-12 每天更新3次
]
# 合并文件的函数
def merge_txt_files(urls, output_filename='汇总.txt'):
    try:
        # 打开文件准备写入
        with open(output_filename, 'w', encoding='utf-8') as outfile:
            for url in urls:
                try:
                    # 发送HTTP GET请求
                    response = requests.get(url)
                    # 检查请求是否成功
                    response.raise_for_status()
                    # 读取内容并写入输出文件
                    outfile.write(response.text + '\n')
                except requests.RequestException as e:
                    # 打印错误信息并继续下一个循环
                    print(f'Error downloading {url}: {e}')
    except IOError as e:
        # 处理文件写入错误
        print(f'Error writing to file: {e}')
# 调用函数
merge_txt_files(urls)



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
            urls = re.findall(r'[https]?[http]?[rtsp]?[rtmp]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', line)
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
remove_duplicates('汇总.txt', '汇总.txt')   

# 导入fileinput模块
import fileinput
# 定义替换规则的字典
replacements = {
    	"CCTV-1高清测试": "",
    	"CCTV-2高清测试": "",
    	"CCTV-7高清测试": "",
    	"CCTV-10高清测试": "",
    	"中央": "CCTV",
    	"高清""": "",
    	"HD": "",
    	"标清": "",
    	"-": "",
    	"超清": "",
    	"频道": "",
    	"CCTV-": "CCTV",
    	"CCTV_": "CCTV",
    	" ": "",
    	"CCTV风云剧场": "风云剧场",
    	"CCTV第一剧场": "第一剧场",
    	"CCTV怀旧剧场": "怀旧剧场",
    	"熊猫影院": "熊猫电影",
    	"熊猫爱生活": "熊猫生活",
    	"爱宠宠物": "宠物生活",
    	"[ipv6]": "",
    	"专区": "",
    	"卫视超": "卫视",
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
    	"测试cctv": "CCTV",
    	"CCTV1综合": "CCTV1",
    	"CCTV2财经": "CCTV2",
    	"CCTV3综艺": "CCTV3",
    	"CCTV4国际": "CCTV4",
    	"CCTV4中文国际": "CCTV4",
    	"CCTV4欧洲": "CCTV4",
    	"CCTV5体育": "CCTV5",
    	"CCTV5+体育": "CCTV5+",
    	"CCTV6电影": "CCTV6",
    	"CCTV7军事": "CCTV7",
    	"CCTV7军农": "CCTV7",
    	"CCTV7农业": "CCTV7",
    	"CCTV7国防军事": "CCTV7",
    	"CCTV8电视剧": "CCTV8",
    	"CCTV8影视": "CCTV8",
    	"CCTV8纪录": "CCTV9",
    	"CCTV9记录": "CCTV9",
    	"CCTV9纪录": "CCTV9",
    	"CCTV10科教": "CCTV10",
    	"CCTV11戏曲": "CCTV11",
    	"CCTV12社会与法": "CCTV12",
    	"CCTV13新闻": "CCTV13",
    	"CCTV新闻": "CCTV13",
    	"CCTV14少儿": "CCTV14",
    	"央视14少儿": "CCTV14",
    	"CCTV少儿超": "CCTV14",
    	"CCTV15音乐": "CCTV15",
    	"CCTV音乐": "CCTV15",
    	"CCTV16奥林匹克": "CCTV16",
    	"CCTV17农业农村": "CCTV17",
    	"CCTV17军农": "CCTV17",
    	"CCTV17农业": "CCTV17",
    	"CCTV5+体育赛视": "CCTV5+",
    	"CCTV5+赛视": "CCTV5+",
    	"CCTV5+体育赛事": "CCTV5+",
    	"CCTV5+赛事": "CCTV5+",
    	"CCTV5+体育": "CCTV5+",
    	"CCTV5赛事": "CCTV5+",
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
# 打开原始文件读取内容，并写入新文件
with open('汇总.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()
# 创建新文件并写入替换后的内容
with open('汇总.txt', 'w', encoding='utf-8') as new_file:
    for line in lines:
        for old, new in replacements.items():
            line = line.replace(old, new)
        new_file.write(line)
print("替换完成，新文件已保存。")




import re
from pypinyin import lazy_pinyin
# 打开一个utf-8编码的文本文件
with open("汇总.txt", "r", encoding="utf-8") as file:
    # 读取所有行并存储到列表中
    lines = file.readlines()
# 定义一个函数，用于提取每行的第一个数字
def extract_first_number(line):
    match = re.search(r'\d+', line)
    return int(match.group()) if match else float('inf')
# 对列表中的行进行排序，按照第一个数字的大小排列，其余行按中文排序
sorted_lines = sorted(lines, key=lambda x: (not 'CCTV' in x, extract_first_number(x) if 'CCTV' in x else lazy_pinyin(x.strip())))
# 将排序后的行写入新的utf-8编码的文本文件
with open("2.txt", "w", encoding="utf-8") as file:
    for line in sorted_lines:
        file.write(line)


import re
import os
def filter_lines(file_path):
    with open(input_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    filtered_lines = []
    for line in lines:
        if ',' in line:
         if 'epg' not in line and 'mitv' not in line and 'udp' not in line and 'rtp' not in line and 'tsfile' not in line and '/hls/' not in line and '[2409' not in line \
            and 'P2p' not in line and 'p2p' not in line and 'p3p' not in line and 'P2P' not in line and 'P3p' not in line and 'P3P' not in line:
          filtered_lines.append(line)
    return filtered_lines
def write_filtered_lines(output_file_path, filtered_lines):
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.writelines(filtered_lines)
if __name__ == "__main__":
    input_file_path = "2.txt"
    output_file_path = "2.txt"
    filtered_lines = filter_lines(input_file_path)
    write_filtered_lines(output_file_path, filtered_lines)
print(f"文件已过滤完成")

#################################################### 对整理好的频道列表测试HTTP连接
def test_connectivity(url, max_attempts=2): #定义测试HTTP连接的次数
    # 尝试连接指定次数    
   for _ in range(max_attempts):  
    try:
        response = requests.head(url, timeout=0.5)  # 发送HEAD请求,仅支持V4,修改此行数字可定义链接超时##////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        #response = requests.get(url, timeout=1)  # 发送get请求,支持V6,修改此行数字可定义链接超时##############################//////////////////////////////////////////////////////////////////////////////////////
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
        source_file_path = "2.txt"  # 输入源文件路径
        output_file_path = "2.txt"  # 设置输出文件路径
        main(source_file_path, output_file_path)  # 调用main函数
    except Exception as e:
        print(f"程序发生错误: {e}")  # 打印错误信息
        
#########################################################################提取2中的有效行
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
    input_file_path = "2.txt"  # 设置输入文件路径
    output_file_path = "2.txt"  # 设置输出文件路径
    filtered_lines = filter_lines(input_file_path)  # 调用filter_lines函数
    write_filtered_lines(output_file_path, filtered_lines)  # 调用write_filtered_lines函数
###################################################################################定义替换规则的字典,对整行内的内容进行替换
replacements = {
    ",有效": "",  # 将",有效"替换为空字符串
    "#genre#,无效": "#genre#",  # 将"#genre#,无效"替换为"#genre#"
}
# 打开原始文件读取内容,并写入新文件
with open('2.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()
# 创建新文件并写入替换后的内容
with open('2.txt', 'w', encoding='utf-8') as new_file:
    for line in lines:
        for old, new in replacements.items():  # 遍历替换规则字典
            line = line.replace(old, new)  # 替换行中的内容
        new_file.write(line)  # 写入新文件
print("新文件已保存。")  # 打印完成信息



########################################################################################################################################################################################
################################################################定义关键词分割规则
def check_and_write_file(input_file, output_file, keywords):
    # 使用 split(', ') 来分割关键词
    keywords_list = keywords.split(', ')
    pattern = '|'.join(re.escape(keyword) for keyword in keywords_list)

    # 读取输入文件并提取包含关键词的行
    extracted_lines = []
    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
          if "genre" not in line:
            if re.search(pattern, line):
                extracted_lines.append(line)

    # 如果至少提取到一行，写入头部信息和提取的行到输出文件
    if extracted_lines:
        with open(output_file, 'w', encoding='utf-8') as out_file:
            out_file.write(f"{keywords_list[0]},#genre#\n")  # 写入头部信息
            out_file.writelines(extracted_lines)  # 写入提取的行

        # 获取头部信息的大小
        header_size = len(f"{keywords_list[0]},#genre#\n")
        
        # 检查文件的总大小
        file_size = os.path.getsize(output_file)
        
        # 如果文件大小小于30字节（假设的最小文件大小），删除文件
        if file_size < 800:
            os.remove(output_file)
            print(f"文件只包含头部信息，{output_file} 已被删除。")
        else:
            print(f"文件已提取关键词并保存为: {output_file}")
    else:
        print(f"未提取到关键词，不创建输出文件 {output_file}。")
# 按类别提取关键词并写入文件
check_and_write_file('2.txt',  'a0.txt',  keywords="央视频道, 8K, 4K, 4k")
check_and_write_file('2.txt',  'a.txt',  keywords="央视频道, CCTV")
check_and_write_file('2.txt',  'a1.txt',  keywords="央视频道, 第一剧场, 风云剧场, 怀旧剧场, 家庭影院, 高清电影, 影迷, 动作电影, 峨眉电影, 世界地理")

check_and_write_file('2.txt',  'b0.txt',  keywords="卫视频道, 湖北卫视, 湖南卫视, 江苏卫视, 安徽卫视, 凤凰卫视, 辽宁卫视")
check_and_write_file('2.txt',  'b.txt',  keywords="卫视频道, 卫视")

check_and_write_file('2.txt',  'c.txt',  keywords="影视频道, 爱情喜剧, 爱喜喜剧, 惊嫊悬疑, 东北热剧, 动作电影, 无名, 都市剧场, iHOT, 海外剧场, 欢笑剧场, 重温经典, 明星大片, 中国功夫, 军旅, 东北热剧, 中国功夫, 军旅剧场, 古装剧场, \
家庭剧场, 惊悚悬疑, 欢乐剧场, 潮妈辣婆, 爱情喜剧, 精品大剧, 超级影视, 超级电影, 黑莓动画, 黑莓电影, 海外剧场, 精彩影视, 无名影视, 潮婆辣妈, 超级剧, 热播精选")
check_and_write_file('2.txt',  'c1.txt',  keywords="影视频道, 求索动物, 求索, 求索科学, 求索记录, 爱谍战, 爱动漫, 爱科幻, 爱青春, 爱自然, 爱科学, 爱浪漫, 爱历史, 爱旅行, 爱奇谈, 爱怀旧, 爱赛车, 爱都市, 爱体育, 爱经典, \
爱玩具, 爱喜剧, 爱悬疑, 爱幼教, 爱院线")

check_and_write_file('2.txt',  'e.txt',  keywords="港澳频道, TVB, 澳门, 龙华, 民视, 中视, 华视, AXN,  AMC, MOMO, 采昌, 耀才, 靖天, 镜新闻, 靖洋, 莲花, 年代, 爱尔达, 好莱坞, 华丽, 非凡, 公视, 寰宇, 无线, EVEN, MoMo, 爆谷, 面包, momo, 唐人, \
中华小, 三立, CNA, FOX, RTHK, Movie, 八大, 中天, 中视, 东森, 凤凰, 天映, 美亚, 环球, 翡翠, 亚洲, 大爱, 大愛, 明珠, 半岛, AMC, 龙祥, 台视, 1905, 纬来, 神话, 经典都市, 视界, 番薯, 私人, 酒店, TVB, 凤凰, 半岛, 星光视界, \
番薯, 大愛, 新加坡, 星河, 明珠, 环球, 翡翠台, 大立, 好消息, 美国中文, 神州, 天良, 18台, HBO家庭, HBO, HISTORY, HOY国际财经, 八度, 博斯, 达文西, 迪士尼, \
动物星球, 港石金曲, 红牛, 互动英语, 华纳影视, 华语剧台, ELTV, 欢喜台, 旅游, 美食星球, 千禧, 全球财经, 探案, 探索, 小尼克, 幸福空间, 影剧, 粤语片台, 智林, 猪哥亮")

check_and_write_file('2.txt',  'f0.txt',  keywords="湖北湖南, 湖北, 湖南")
check_and_write_file('2.txt',  'f.txt',  keywords="省市频道, 湖北, 武汉, 松滋, 十堰, 咸宁, 远安, 崇阳, 黄石, 荆州, 当阳, 恩施, 五峰, 来凤, 枝江, 黄冈, 随州, 荆门, 秭归, 宜昌, 长阳, 大悟, 孝感, 鄂州, 垄上, 宜都")
check_and_write_file('2.txt',  'f1.txt',  keywords="省市频道, 湖南, 长沙, 常德, 郴州, 垂钓, 金鹰纪实, 衡阳, 怀化, 茶, 吉首, 娄底, 邵阳, 湘潭, 益阳, 永州, 岳阳, 张家界, 株洲, 城步, 崇左, 洪雅, 涟水, 灵石, 隆回, 罗城, 溆浦, 邵阳")


#check_and_write_file('2.txt',  'h0.txt',  keywords="河南河北, 河南, 河北")
check_and_write_file('2.txt',  'h.txt',  keywords="河南河北, 河南, 焦作, 封丘, 郏县, 获嘉, 巩义, 邓州, 宝丰, 开封, 卢氏, 洛阳, 孟津, 安阳, 渑池, 南阳, 林州, 滑县, 栾川, 襄城, 宜阳, 长垣, 内黄, 鹿邑, 新安, 平顶山, 淇县, \
杞县, 汝阳, 三门峡, 卫辉, 淅川, 新密, 新乡, 信阳, 新郑, 延津, 叶县, 义马, 永城, 禹州, 原阳, 镇平, 郑州, 周口, 泌阳, 郸城, 登封, 扶沟, 潢川, 辉县, 济源, 浚县, 临颍, 灵宝, 鲁山, 罗山, 沁阳, 汝州, 唐河, 尉氏")
check_and_write_file('2.txt',  'h1.txt',  keywords="河南河北, 河北, 石家庄, 承德, 丰宁, 临漳, 井陉, 井陉矿区, 保定, 元氏, 兴隆, 内丘, 南宫, 吴桥, 唐县, 唐山, 安平, 定州, 大厂, 张家口, 徐水, 成安, 故城, 康保, 廊坊, 晋州, \
景县, 武安, 枣强, 柏乡, 涉县, 涞水, 涞源, 涿州, 深州, 深泽, 清河, 秦皇岛, 衡水, 遵化, 邢台, 邯郸, 邱县, 隆化, 雄县, 阜平, 高碑店, 高邑, 魏县, 黄骅, 饶阳, 赵县, 睛彩河北, 滦南, 玉田, 崇礼, 平泉, \
容城, 文安, 三河, 清河, 潞城, 迁安, 迁西, 清苑, 确山")





###############################################################################################################################################################################################################################
##############################################################对生成的文件进行合并
file_contents = []
file_paths = ["e.txt", "a0.txt", "a.txt", "a1.txt", "b0.txt", "b.txt", "c.txt", "c1.txt", "c2.txt", "d.txt", "f0.txt", "f.txt", "f1.txt", "g0.txt", "g.txt", "g1.txt", "h0.txt", "h.txt", "h1.txt"]  # 替换为实际的文件路径列表
for file_path in file_paths:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding="utf-8") as file:
            content = file.read()
            file_contents.append(content)
    else:                # 如果文件不存在，则提示异常并打印提示信息
        print(f"文件 {file_path} 不存在，跳过")
# 写入合并后的文件
with open("去重.txt", "w", encoding="utf-8") as output:
    output.write('\n'.join(file_contents))

###############################################################################################################################################################################################################################
##############################################################对生成的文件进行网址及文本去重复，避免同一个频道出现在不同的类中

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
remove_duplicates('去重.txt', '分类.txt')

# 打开文档并读取所有行 
with open('分类.txt', 'r', encoding="utf-8") as file:
 lines = file.readlines()
# 使用列表来存储唯一的行的顺序 
 unique_lines = [] 
 seen_lines = set() 
# 遍历每一行，如果是新的就加入unique_lines 
for line in lines:
 if line not in seen_lines:
  unique_lines.append(line)
  seen_lines.add(line)
# 将唯一的行写入新的文档 
with open('回收站.txt', 'w', encoding="utf-8") as file:
 file.writelines(unique_lines)





################################################################################################任务结束，删除不必要的过程文件
files_to_remove = ['去重.txt', '分类.txt', "2.txt", "a0.txt", "a.txt", "a1.txt", "b0.txt", "b.txt", "c.txt", "c1.txt", "c2.txt", "d.txt", "e.txt", "f0.txt", "f.txt", "f1.txt", "g0.txt", "g.txt", "g1.txt", "h0.txt", "h.txt", "h1.txt", "i.txt", \
              "i1.txt", "j.txt", "j1.txt", "k.txt", "l0.txt", "l.txt", "l1.txt", "m.txt", "m1.txt",  \
              "n0.txt","n.txt","n1.txt", "o1.txt", "o.txt", "p.txt", "汇总.txt"]

for file in files_to_remove:
    if os.path.exists(file):
        os.remove(file)
    else:              # 如果文件不存在，则提示异常并打印提示信息
        print(f"文件 {file} 不存在，跳过删除。")

print("任务运行完毕，分类频道列表可查看文件夹内综合源.txt文件！")
