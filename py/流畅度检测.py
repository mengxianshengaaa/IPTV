from pypinyin import lazy_pinyin
import re
import os
from opencc import OpenCC
import fileinput

# 获取playlist目录下的文件名
files1 = 'playlist'
# 过滤TXT文件
file_contents = []
for file_path in filter_files(files1, '.txt'):
    with open('playlist/' + file_path, 'r', encoding="utf-8") as file:
        content = file.read()
        file_contents.append(content)
# 写入合并后的txt文件
with open("playlist/3.txt", "w", encoding="utf-8") as output:
    output.write('\n'.join(file_contents))


# 合并自定义频道文件#
file_contents = []
file_paths = ["playlist/3.txt", "酒店源.txt", "综合源.txt"]  # 替换为实际的文件路径列表
for file_path in file_paths:
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding="utf-8") as file:
            content = file.read()
            file_contents.append(content)
    else:                # 如果文件不存在，则提示异常并打印提示信息
        print(f"文件 {file_path} 不存在，跳过")
# 写入合并后的文件
with open("4.txt", "w", encoding="utf-8") as output:
    output.write('\n'.join(file_contents))


import cv2
import time
from tqdm import tqdm

# 初始化检测结果字典
detected_ips = {}

# 存储文件路径
file_path = "4.txt"
output_file_path = "2.txt"

def get_ip_key(url):
    """从URL中提取IP地址，并构造一个唯一的键"""
    # 找到'//'到第三个'.'之间的字符串
    start = url.find('://') + 3  # '://'.length 是 3
    end = start
    dot_count = 0
    while dot_count < 3:
        end = url.find('.', end)
        if end == -1:  # 如果没有找到第三个'.'，就结束
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

        # 分割频道名称和URL，并去除空白字符
        parts = line.split(',', 1)
        if len(parts) == 2:
            channel_name, url = parts
            channel_name = channel_name.strip()
            url = url.strip()

            # 构造IP键
            ip_key = get_ip_key(url)
            if ip_key and ip_key in detected_ips:
                # 如果IP键已存在，根据之前的结果决定是否写入新文件
                if detected_ips[ip_key]['status'] == 'ok':
                    output_file.write(line)
            elif ip_key:  # 新IP键，进行检测
                # 进行检测
                cap = cv2.VideoCapture(url)
                start_time = time.time()
                frame_count = 0

                # 尝试捕获5秒内的帧
                while frame_count < 80 and (time.time() - start_time) < 5:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frame_count += 1

                # 释放资源
                cap.release()

                # 根据捕获的帧数判断状态并记录结果
                if frame_count >= 80:
                    detected_ips[ip_key] = {'status': 'ok'}
                    output_file.write(line)  # 写入检测通过的行
                else:
                    detected_ips[ip_key] = {'status': 'fail'}

# 打印检测结果
for ip_key, result in detected_ips.items():
    print(f"IP Key: {ip_key}, Status: {result['status']}")


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
#check_and_write_file('2.txt',  'a1.txt',  keywords="央视频道, 剧场, 影院, 电影, 女性, 地理")

check_and_write_file('2.txt',  'b.txt',  keywords="卫视频道, 卫视")

check_and_write_file('2.txt',  'c.txt',  keywords="影视频道, 爱情喜剧, 爱喜喜剧, 惊嫊悬疑, 东北热剧, 动作电影, 无名, 都市剧场, iHOT, 海外剧场, 欢笑剧场, 重温经典, 明星大片, 中国功夫, 军旅, 东北热剧, 中国功夫, 军旅剧场, 古装剧场, \
家庭剧场, 惊悚悬疑, 欢乐剧场, 潮妈辣婆, 爱情喜剧, 精品大剧, 超级影视, 超级电影, 黑莓动画, 黑莓电影, 海外剧场, 精彩影视, 无名影视, 潮婆辣妈, 超级剧, 热播精选")

check_and_write_file('2.txt',  'd.txt',  keywords="少儿频道, 少儿, 卡通, 动漫, 宝贝, 哈哈")

check_and_write_file('2.txt',  'e.txt',  keywords="港澳频道, TVB, 澳门, 龙华, 民视, 中视, 华视, AXN, MOMO, 采昌, 耀才, 靖天, 镜新闻, 靖洋, 莲花, 年代, 爱尔达, 好莱坞, 华丽, 非凡, 公视, 寰宇, 无线, EVEN, MoMo, 爆谷, 面包, momo, 唐人, \
中华小, 三立, CNA, FOX, RTHK, Movie, 八大, 中天, 中视, 东森, 凤凰, 天映, 美亚, 环球, 翡翠, 亚洲, 大爱, 大愛, 明珠, 半岛, AMC, 龙祥, 台视, 1905, 纬来, 神话, 经典都市, 视界, 番薯, 私人, 酒店, TVB, 凤凰, 半岛, 星光视界, \
番薯, 大愛, 新加坡, 星河, 明珠, 环球, 翡翠台,  ELTV, 大立, elta, 好消息, 美国中文, 神州, 天良, 18台, BLOOMBERG, Bloomberg, CMUSIC, CN卡通, CNBC, CNBC, CinemaWorld, Cinemax, DMAX, Dbox, Dreamworks, ESPN, Euronews, \
Eurosports1, FESTIVAL, GOOD2, HBO家庭, HBO, HISTORY, HOY国际财经, HakkaTV, J2, KOREA, LISTENONSPOTIFY, LUXE, MCE, MTV, Now, PremierSports, ROCK, SPOTV, TiTV, VOA, ViuTV, ViuTV6, WSport, WWE, 八度, 博斯, 达文西, 迪士尼, \
动物星球, 港石金曲, 红牛, 互动英语, 华纳影视, 华语剧台, ELTV, 欢喜台, 旅游, 美食星球, nhkworld, nickjr, 千禧, 全球财经, 探案, 探索, 小尼克, 幸福空间, 影剧, 粤语片台, 智林, 猪哥亮")

#check_and_write_file('2.txt',  'f0.txt',  keywords="湖北湖南, 湖北, 湖南")
check_and_write_file('2.txt',  'f.txt',  keywords="省市频道, 湖北, 武汉, 松滋, 十堰, 咸宁, 远安, 崇阳, 黄石, 荆州, 当阳, 恩施, 五峰, 来凤, 枝江, 黄冈, 随州, 荆门, 秭归, 宜昌, 长阳, 大悟, 孝感, 鄂州, 垄上, 宜都")
check_and_write_file('2.txt',  'f1.txt',  keywords="省市频道, 湖南, 长沙, 常德, 郴州, 垂钓, 金鹰纪实, 衡阳, 怀化, 茶, 吉首, 娄底, 邵阳, 湘潭, 益阳, 永州, 岳阳, 张家界, 株洲, 城步, 崇左, 洪雅, 涟水, 灵石, 隆回, 罗城, 溆浦, 邵阳")

#check_and_write_file('2.txt',  'g0.txt',  keywords="浙江上海, 浙江, 上海")
check_and_write_file('2.txt',  'g.txt',  keywords="浙江上海, 浙江, 杭州, 宁波, 平湖, 庆元, 缙云, 嵊, 义乌, 东阳, 文成, 云和, 象山, 衢江, 萧山, 龙游, 武义, 兰溪, 开化, 丽水, 上虞, NBTV, 舟山, 新密, 衢州, 嘉兴, 绍兴, 温州, \
湖州, 永嘉, 诸暨, 钱江, 松阳, 苍南, 遂昌, 青田, 龙泉, 余杭, 新昌, 杭州, 余杭, 丽水, 龙泉, 青田, 松阳, 遂昌, 宁波, 余姚, 上虞, 新商都, 绍兴, 温州, 永嘉, 诸暨, 钱江, 金华, 苍南, 临平")
check_and_write_file('2.txt',  'g1.txt',  keywords="浙江上海, 上海, 东方, 普陀, 东方财经, 五星体育, 第一财经, 七彩, 崇明")

#check_and_write_file('2.txt',  'h0.txt',  keywords="河南河北, 河南, 河北")
check_and_write_file('2.txt',  'h.txt',  keywords="河南河北, 河南, 焦作, 封丘, 郏县, 获嘉, 巩义, 邓州, 宝丰, 开封, 卢氏, 洛阳, 孟津, 安阳, 渑池, 南阳, 林州, 滑县, 栾川, 襄城, 宜阳, 长垣, 内黄, 鹿邑, 新安, 平顶山, 淇县, \
杞县, 汝阳, 三门峡, 卫辉, 淅川, 新密, 新乡, 信阳, 新郑, 延津, 叶县, 义马, 永城, 禹州, 原阳, 镇平, 郑州, 周口, 泌阳, 郸城, 登封, 扶沟, 潢川, 辉县, 济源, 浚县, 临颍, 灵宝, 鲁山, 罗山, 沁阳, 汝州, 唐河, 尉氏")
check_and_write_file('2.txt',  'h1.txt',  keywords="河南河北, 河北, 石家庄, 承德, 丰宁, 临漳, 井陉, 井陉矿区, 保定, 元氏, 兴隆, 内丘, 南宫, 吴桥, 唐县, 唐山, 安平, 定州, 大厂, 张家口, 徐水, 成安, 故城, 康保, 廊坊, 晋州, \
景县, 武安, 枣强, 柏乡, 涉县, 涞水, 涞源, 涿州, 深州, 深泽, 清河, 秦皇岛, 衡水, 遵化, 邢台, 邯郸, 邱县, 隆化, 雄县, 阜平, 高碑店, 高邑, 魏县, 黄骅, 饶阳, 赵县, 睛彩河北, 滦南, 玉田, 崇礼, 平泉, \
容城, 文安, 三河, 清河, 潞城, 迁安, 迁西, 清苑, 确山")

#check_and_write_file('2.txt',  'j.txt',  keywords="广东广西, 广东, 广西")
check_and_write_file('2.txt',  'j.txt',  keywords="广东广西, 广东, 潮州, 东莞, 佛山, 广州, 河源, 惠州, 江门, 揭阳, 茂名, 梅州, 清远, 汕头, 汕尾, 韶关, 深圳, 阳江, 云浮, 湛江, 肇庆, 中山, 珠海, 番禺")
check_and_write_file('2.txt',  'j1.txt',  keywords="广东广西, 广西, 百色, 北海, 防城港, 桂林, 河池, 贺州, 柳州, 南宁, 钦州, 梧州, 玉林, 宾阳")

#check_and_write_file('2.txt',  'l0.txt',  keywords="安徽四川, 安徽, 四川")
check_and_write_file('2.txt',  'l.txt',  keywords="安徽四川, 安徽, 安庆, 蚌埠, 亳州, 巢湖, 池州, 岳西, 滁州, 阜阳, 合肥, 淮北, 淮南, 黄山, 六安, 马鞍山, 宿州, 铜陵, 芜湖, 宣城, 固始, 光山")
check_and_write_file('2.txt',  'l1.txt',  keywords="安徽四川, 四川, 阿坝, 巴中, 成都, 达州, 德阳, 甘孜, 广安, 广元, 乐山, 凉山, 泸州, 眉山, 绵阳, 内江, 南充, 攀枝花, 遂宁, 雅安, 宜宾, 资阳, 自贡, 黑水, 金川, 乐至, 双流, \
万源, 马尔康, 泸县, 文山, 什邡, 西青, 长宁, 达州, 红河")



check_and_write_file('2.txt',  'o1.txt',  keywords="其他频道, 新闻, 综合, 文艺, 电视, 公共, 科教, 教育, 民生, 轮播, 套, 法制, 文化, 经济, 生活")
check_and_write_file('2.txt',  'o.txt',  keywords="其他频道, , ")




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
with open('分类.txt', 'w', encoding="utf-8") as file:
 file.writelines(unique_lines)





################################################################################################任务结束，删除不必要的过程文件
files_to_remove = ['去重.txt', "2.txt", "4.txt", "playlist/3.txt", "a0.txt", "a.txt", "a1.txt", "b0.txt", "b.txt", "c.txt", "c1.txt", "c2.txt", "d.txt", "e.txt", "f0.txt", "f.txt", "f1.txt", "g0.txt", "g.txt", "g1.txt", "h0.txt", "h.txt", "h1.txt", "i.txt", \
              "i1.txt", "j.txt", "j1.txt", "k.txt", "l0.txt", "l.txt", "l1.txt", "m.txt", "m1.txt",  \
              "n0.txt","n.txt","n1.txt", "o1.txt", "o.txt", "p.txt"]

for file in files_to_remove:
    if os.path.exists(file):
        os.remove(file)
    else:              # 如果文件不存在，则提示异常并打印提示信息
        print(f"文件 {file} 不存在，跳过删除。")

print("任务运行完毕，分类频道列表可查看文件夹内综合源.txt文件！")




