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

url = "https://raw.githubusercontent.com/frxz751113/collect-tv-txt/main/merged_output.txt"          #源采集地址
r = requests.get(url)
open('源.txt','wb').write(r.content)   



# 使用with语句打开输入文件进行读取
with open("源.txt", 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 使用列表推导式过滤行
filtered_lines = [line for line in lines if ',' in line and 
                  all(substr not in line for substr in ['epg', 'mitv', 'udp', 'rtp', '[', 'P2p', 'p2p', 'p3p', 'P2P', 'P3p', 'P3P'])]

# 使用with语句打开输出文件进行写入
with open("源.txt", 'w', encoding='utf-8') as output_file:
    output_file.writelines(filtered_lines)

print("文件过滤完成。")
#################################################### 对整理好的频道列表测试HTTP连接
def test_connectivity(url, max_attempts=1): #定义测试HTTP连接的次数
    # 尝试连接指定次数    
   for _ in range(max_attempts):  
    try:
        response = requests.head(url, timeout=3)  # 发送HEAD请求,仅支持V4,修改此行数字可定义链接超时##////////////////////////////////////////////////////////////////////////////////////////////////////////////////
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
                while frame_count < 230 and (time.time() - start_time) < 10:#//////////////////////////////////////////////////////////////////////////////////////###########
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frame_count += 1
                # 释放资源
                cap.release()
                # 根据捕获的帧数判断状态并记录结果#////////////////////////////////////////////////////////////////////////////////////////////////////////////////###########
                if frame_count >= 230:  #5秒内超过100帧则写入#/////////////////////////////////////////////////////////////////////////////////////////////////////###########
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
家庭剧场, 惊悚悬疑, 欢乐剧场, 潮妈辣婆, 爱情喜剧, 精品大剧, 超级影视, 超级电影, 黑莓动画, 黑莓电影, 海外剧场, 精彩影视, 无名影视, 潮婆辣妈, 超级剧, 热播精选")
check_and_write_file('优选.txt',  'c1.txt',  keywords="影视频道, 求索动物, 求索, 求索科学, 求索记录, 爱谍战, 爱动漫, 爱科幻, 爱青春, 爱自然, 爱科学, 爱浪漫, 爱历史, 爱旅行, 爱奇谈, 爱怀旧, 爱赛车, 爱都市, 爱体育, 爱经典, \
爱玩具, 爱喜剧, 爱悬疑, 爱幼教, 爱院线")
check_and_write_file('优选.txt',  'c2.txt',  keywords="影视频道, 炫舞, 健康, 农业致富, 军事评论, 农业致富, 哒啵赛事, 怡伴健康, 武博世界, 超级综艺, 哒啵, HOT, 炫舞未来, 精品体育, 精品萌宠, 精品记录, 超级体育, 金牌, 武术世界, 精品纪录")

check_and_write_file('优选.txt',  'd.txt',  keywords="少儿频道, 少儿, 卡通, 动漫, 宝贝, 哈哈")

check_and_write_file('优选.txt',  'e.txt',  keywords="港澳频道, TVB, 澳门, 龙华, 民视, 中视, 华视, AXN, MOMO, 采昌, 耀才, 靖天, 镜新闻, 靖洋, 莲花, 年代, 爱尔达, 好莱坞, 华丽, 非凡, 公视, 寰宇, 无线, EVEN, MoMo, 爆谷, 面包, momo, 唐人, \
中华小, 三立, CNA, FOX, RTHK, Movie, 八大, 中天, 中视, 东森, 凤凰, 天映, 美亚, 环球, 翡翠, 亚洲, 大爱, 大愛, 明珠, 半岛, AMC, 龙祥, 台视, 1905, 纬来, 神话, 经典都市, 视界, 番薯, 私人, 酒店, TVB, 凤凰, 半岛, 星光视界, \
番薯, 大愛, 新加坡, 星河, 明珠, 环球, 翡翠台,  ELTV, 大立, elta, 好消息, 美国中文, 神州, 天良, 18台, BLOOMBERG, Bloomberg, CMUSIC, CN卡通, CNBC, CNBC, CinemaWorld, Cinemax, DMAX, Dbox, Dreamworks, ESPN, Euronews, \
Eurosports1, FESTIVAL, GOOD2, HBO家庭, HBO, HISTORY, HOY国际财经, HakkaTV, J2, KOREA, LISTENONSPOTIFY, LUXE, MCE, MTV, Now, PremierSports, ROCK, SPOTV, TiTV, VOA, ViuTV, ViuTV6, WSport, WWE, 八度, 博斯, 达文西, 迪士尼, \
动物星球, 港石金曲, 红牛, 互动英语, 华纳影视, 华语剧台, ELTV, 欢喜台, 旅游, 美食星球, nhkworld, nickjr, 千禧, 全球财经, 探案, 探索, 小尼克, 幸福空间, 影剧, 粤语片台, 智林, 猪哥亮")

#check_and_write_file('优选.txt',  'f0.txt',  keywords="湖北湖南, 湖北, 湖南")
check_and_write_file('优选.txt',  'f.txt',  keywords="省市频道, 湖北, 武汉, 松滋, 十堰, 咸宁, 远安, 崇阳, 黄石, 荆州, 当阳, 恩施, 五峰, 来凤, 枝江, 黄冈, 随州, 荆门, 秭归, 宜昌, 长阳, 大悟, 孝感, 鄂州, 垄上, 宜都")
check_and_write_file('优选.txt',  'f1.txt',  keywords="省市频道, 湖南, 长沙, 常德, 郴州, 垂钓, 金鹰纪实, 衡阳, 怀化, 茶, 吉首, 娄底, 邵阳, 湘潭, 益阳, 永州, 岳阳, 张家界, 株洲, 城步, 崇左, 洪雅, 涟水, 灵石, 隆回, 罗城, 溆浦, 邵阳")

#check_and_write_file('优选.txt',  'g0.txt',  keywords="浙江上海, 浙江, 上海")
check_and_write_file('优选.txt',  'g.txt',  keywords="浙江上海, 浙江, 杭州, 宁波, 平湖, 庆元, 缙云, 嵊, 义乌, 东阳, 文成, 云和, 象山, 衢江, 萧山, 龙游, 武义, 兰溪, 开化, 丽水, 上虞, NBTV, 舟山, 新密, 衢州, 嘉兴, 绍兴, 温州, \
湖州, 永嘉, 诸暨, 钱江, 松阳, 苍南, 遂昌, 青田, 龙泉, 余杭, 新昌, 杭州, 余杭, 丽水, 龙泉, 青田, 松阳, 遂昌, 宁波, 余姚, 上虞, 新商都, 绍兴, 温州, 永嘉, 诸暨, 钱江, 金华, 苍南, 临平")
check_and_write_file('优选.txt',  'g1.txt',  keywords="浙江上海, 上海, 东方, 普陀, 东方财经, 五星体育, 第一财经, 七彩, 崇明")

#check_and_write_file('优选.txt',  'h0.txt',  keywords="河南河北, 河南, 河北")
check_and_write_file('优选.txt',  'h.txt',  keywords="河南河北, 河南, 焦作, 封丘, 郏县, 获嘉, 巩义, 邓州, 宝丰, 开封, 卢氏, 洛阳, 孟津, 安阳, 渑池, 南阳, 林州, 滑县, 栾川, 襄城, 宜阳, 长垣, 内黄, 鹿邑, 新安, 平顶山, 淇县, \
杞县, 汝阳, 三门峡, 卫辉, 淅川, 新密, 新乡, 信阳, 新郑, 延津, 叶县, 义马, 永城, 禹州, 原阳, 镇平, 郑州, 周口, 泌阳, 郸城, 登封, 扶沟, 潢川, 辉县, 济源, 浚县, 临颍, 灵宝, 鲁山, 罗山, 沁阳, 汝州, 唐河, 尉氏")
check_and_write_file('优选.txt',  'h1.txt',  keywords="河南河北, 河北, 石家庄, 承德, 丰宁, 临漳, 井陉, 井陉矿区, 保定, 元氏, 兴隆, 内丘, 南宫, 吴桥, 唐县, 唐山, 安平, 定州, 大厂, 张家口, 徐水, 成安, 故城, 康保, 廊坊, 晋州, \
景县, 武安, 枣强, 柏乡, 涉县, 涞水, 涞源, 涿州, 深州, 深泽, 清河, 秦皇岛, 衡水, 遵化, 邢台, 邯郸, 邱县, 隆化, 雄县, 阜平, 高碑店, 高邑, 魏县, 黄骅, 饶阳, 赵县, 睛彩河北, 滦南, 玉田, 崇礼, 平泉, \
容城, 文安, 三河, 清河, 潞城, 迁安, 迁西, 清苑, 确山")

check_and_write_file('优选.txt',  'i.txt',  keywords="江苏江西, 江苏, 常州, 淮安, 连云港, 南京, 南通, 高邮, 苏州, 江宁, 宿迁, 泰州, 无锡, 徐州, 盐城, 扬州, 镇江, 靖江, 沭阳")
check_and_write_file('优选.txt',  'i1.txt',  keywords="江苏江西, 江西, 抚州, 赣州, 吉安, 景德镇, 九江, 南昌, 萍乡, 上饶, 新余, 宜春, 鹰潭")

#check_and_write_file('优选.txt',  'j.txt',  keywords="广东广西, 广东, 广西")
check_and_write_file('优选.txt',  'j.txt',  keywords="广东广西, 广东, 潮州, 东莞, 佛山, 广州, 河源, 惠州, 江门, 揭阳, 茂名, 梅州, 清远, 汕头, 汕尾, 韶关, 深圳, 阳江, 云浮, 湛江, 肇庆, 中山, 珠海, 番禺")
check_and_write_file('优选.txt',  'j1.txt',  keywords="广东广西, 广西, 百色, 北海, 防城港, 桂林, 河池, 贺州, 柳州, 南宁, 钦州, 梧州, 玉林, 宾阳")

check_and_write_file('优选.txt',  'k.txt',  keywords="山东山西, 山东, 滨州, 青州, 德州, 东营, 菏泽, 济南, 济宁, 莱芜, 聊城, 临沂, 青岛, 日照, 泰安, 威海, 潍坊, 烟台, 枣庄, 淄博, 山西, 长治, 大同, 晋城, 晋中, 临汾, 吕梁, 朔州, \
太原, 忻州, 阳泉, 运城, 汾西")

#check_and_write_file('优选.txt',  'l0.txt',  keywords="安徽四川, 安徽, 四川")
check_and_write_file('优选.txt',  'l.txt',  keywords="安徽四川, 安徽, 安庆, 蚌埠, 亳州, 巢湖, 池州, 岳西, 滁州, 阜阳, 合肥, 淮北, 淮南, 黄山, 六安, 马鞍山, 宿州, 铜陵, 芜湖, 宣城, 固始, 光山")
check_and_write_file('优选.txt',  'l1.txt',  keywords="安徽四川, 四川, 阿坝, 巴中, 成都, 达州, 德阳, 甘孜, 广安, 广元, 乐山, 凉山, 泸州, 眉山, 绵阳, 内江, 南充, 攀枝花, 遂宁, 雅安, 宜宾, 资阳, 自贡, 黑水, 金川, 乐至, 双流, \
万源, 马尔康, 泸县, 文山, 什邡, 西青, 长宁, 达州, 红河")

check_and_write_file('优选.txt',  'm.txt',  keywords="云南贵州, 云南, 版纳, 保山, 楚雄, 大理, 德宏, 西畴, 迪庆, 砚山, 红河, 昆明, 丽江, 麻栗坡, 临沧, 怒江, 曲靖, 思茅, 文山, 玉溪, 昭通, 西双版纳, 新平")
check_and_write_file('优选.txt',  'm1.txt',  keywords="云南贵州, 贵州, 安顺, 毕节, 都匀, 贵阳, 凯里, 六盘水, 铜仁, 兴义, 遵义")

#check_and_write_file('优选.txt',  'n0.txt',  keywords="甘肃黑龙江, 甘肃, 黑龙江")
#check_and_write_file('优选.txt',  'n.txt',  keywords="甘肃黑龙江, 黑龙江, 大庆, 大兴安岭, 哈尔滨, 鹤岗, 黑河, 鸡西, 佳木斯, 牡丹江, 七台河, 齐齐哈尔, 双鸭山, 绥化, 伊春, 延边, 偃师, 阳曲")
#check_and_write_file('优选.txt',  'n1.txt',  keywords="甘肃黑龙江, 甘肃, 兰州, 蒙古, 海南, 辽宁, 延安, 吴忠, 西宁, 吉林")


check_and_write_file('优选.txt',  'o1.txt',  keywords="其他频道, 新闻, 综合, 文艺, 电视, 公共, 科教, 教育, 民生, 轮播, 套, 法制, 文化, 经济, 生活")
check_and_write_file('优选.txt',  'o.txt',  keywords="其他频道, , ")




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
