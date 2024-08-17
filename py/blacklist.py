import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime
import os
from urllib.parse import urlparse
import socket  #check p3p源 rtp源
import subprocess #check rtmp源
timestart = datetime.now()
# 读取文件内容
# 定义一个函数，用于读取文本文件并过滤出符合条件的行
def read_txt_file(file_path):
    # 定义一个列表，包含需要跳过的字符串，当前只跳过 '#genre#'
    skip_strings = ['#genre#']  
    # 定义一个列表，包含每行必须包含的字符串，当前只要求包含 '://' 即URL协议标识
    required_strings = ['://']  
    # 使用with语句打开文件，确保最后文件会被正确关闭
    with open(file_path, 'r', encoding='utf-8') as file:
        # 使用列表推导式读取文件，并对每一行进行过滤
        lines = [
            # 对于文件中的每一行line
            line for line in file
            # 只有当该行不包含跳过的字符串并且包含所有必需的字符串时才保留
            if not any(skip_str in line for skip_str in skip_strings) and all(req_str in line for req_str in required_strings)
        ]
    # 返回过滤后的行列表
    return lines
# 定义一个函数，用于检测一个URL是否可访问，并记录访问的响应时间
def check_url(url, timeout=6):
    # 记录开始检查的时间
    start_time = time.time()
    # 初始化响应时间为None
    elapsed_time = None
    # 初始化URL访问成功标志为False
    success = False
    
    try:
        # 如果URL以http开头
        if url.startswith("http"):
            # 设置请求头，模拟浏览器访问
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
            # 创建一个请求对象
            req = urllib.request.Request(url, headers=headers)
            # 使用urllib.request.urlopen打开URL，并设置超时时间
            with urllib.request.urlopen(req, timeout=timeout) as response:
                # 如果响应状态码为200，表示访问成功
                if response.status == 200:
                    success = True
        # 如果URL以p3p开头，则调用特定函数检查p3p源
        elif url.startswith("p3p"):
            success = check_p3p_url(url, timeout)
        # 类似地，如果是rtmp或rtp源，调用相应函数进行检查
        elif url.startswith("rtmp"):
            success = check_rtmp_url(url, timeout)
        elif url.startswith("rtp"):
            success = check_rtp_url(url, timeout)
        # 如果没有异常发生，计算从开始到当前的经过时间，并转换为毫秒
        elapsed_time = (time.time() - start_time) * 1000  
    except Exception as e:
        # 如果发生异常，打印错误信息
        print(f"Error checking {url}: {e}")
        # 并将elapsed_time设置为None
        elapsed_time = None
    # 返回经过时间和访问成功标志
    return elapsed_time, success

# 定义一个函数，用于检查RTMP URL是否可访问
def check_rtmp_url(url, timeout):
    try:
        # 使用subprocess.run调用ffprobe命令行工具检查RTMP流
        # ffprobe是ffmpeg工具集中用于分析视频/音频文件的工具
        result = subprocess.run(
            ['ffprobe', url],  # 执行ffprobe并传入URL作为参数
            stdout=subprocess.PIPE,  # 将标准输出重定向到管道
            stderr=subprocess.PIPE,  # 将标准错误重定向到管道
            timeout=timeout  # 设置超时时间
        )
        # 如果ffprobe命令成功执行，返回码为0，则认为RTMP流可访问
        if result.returncode == 0:
            return True
    # 捕获subprocess.TimeoutExpired异常，即ffprobe命令执行超时
    except subprocess.TimeoutExpired:
        print(f"Timeout checking {url}")  # 打印超时信息
    # 捕获其他所有异常，并打印错误信息
    except Exception as e:
        print(f"Error checking {url}: {e}")
    # 如果发生异常或ffprobe命令执行失败，则返回False
    return False
# 定义一个函数，用于检查RTP URL是否可访问
def check_rtp_url(url, timeout):
    try:
        # 使用urlparse解析URL，提取主机名和端口号
        parsed_url = urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port
        # 创建一个UDP socket连接，用于RTP协议通信
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(timeout)  # 设置socket超时时间
            s.connect((host, port))  # 连接到指定的主机和端口
            # 发送空的UDP数据包到服务器，用于探测服务是否响应
            s.sendto(b'', (host, port))
            # 尝试接收数据，这里只接收1字节，主要是为了检测端口是否开放
            s.recv(1)
        # 如果能够成功建立连接并接收数据，则认为RTP服务是可访问的
        return True
    # 捕获socket.timeout异常，即socket操作超时
    except (socket.timeout, socket.error):
        # 如果发生超时或socket错误，则认为RTP服务不可访问
        return False
# 定义一个函数，用于检查P3P URL是否可访问
def check_p3p_url(url, timeout):
    try:
        # 使用urlparse解析URL，提取主机名、端口号和路径
        parsed_url = urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port
        path = parsed_url.path
        
        # 检查解析结果是否有效，如果主机名、端口号或路径为空，则抛出异常
        if not host or not port or not path:
            raise ValueError("Invalid p3p URL")
        # 创建TCP连接
        with socket.create_connection((host, port), timeout=timeout) as s:
            # 构建一个简单的HTTP请求
            request = f"GET {path} P3P/1.0\r\nHost: {host}\r\n\r\n"
            # 发送请求到服务器
            s.sendall(request.encode())
            # 接收服务器响应，这里只接收1024字节
            response = s.recv(1024)
            
            # 如果响应中包含"P3P"，则认为P3P服务是可访问的
            if b"P3P" in response:
                return True
    # 捕获所有异常，并打印错误信息
    except Exception as e:
        print(f"Error checking {url}: {e}")
    # 如果发生异常，则返回False
    return False


# 定义一个函数，用于处理单行文本并检测其中的URL是否有效
def process_line(line):
    # 如果行中包含 "#genre#" 或者不包含 "://" 则跳过该行
    if "#genre#" in line or "://" not in line:
        return None, None
    # 使用逗号分隔行，期望得到两个部分：名称和URL
    parts = line.split(',')
    # 确认分隔后确实有两个元素，即名称和URL
    if len(parts) == 2:
        name, url = parts
        # 调用check_url函数检测URL是否可访问，并获取响应时间
        elapsed_time, is_valid = check_url(url.strip())
        # 如果URL有效，返回响应时间和原始行
        if is_valid:
            return elapsed_time, line.strip()
        # 如果URL无效，只返回原始行
        else:
            return None, line.strip()
    # 如果行格式不正确，返回None
    return None, None
# 定义一个函数，使用多线程处理文本并检测每个URL
def process_urls_multithreaded(lines, max_workers=28):
    blacklist = []  # 用于存储不可访问的URL列表
    successlist = []  # 用于存储可访问的URL列表
    # 创建一个ThreadPoolExecutor，它是concurrent.futures模块中用于多线程的接口
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 使用字典推导式为每一行创建一个future，并启动process_line函数
        futures = {executor.submit(process_line, line): line for line in lines}
        # 遍历所有完成的futures
        for future in as_completed(futures):
            # future.result()将等待线程完成并返回结果
            elapsed_time, result = future.result()
            # 如果result不为空，说明有URL返回
            if result:
                # 如果响应时间不是None，说明URL是可访问的，添加到successlist
                if elapsed_time is not None:
                    successlist.append(f"{elapsed_time:.2f}ms,{result}")
                # 否则，URL不可访问，添加到blacklist
                else:
                    blacklist.append(result)
    # 返回可访问和不可访问的URL列表
    return successlist, blacklist
# 定义一个函数，用于将数据列表写入到文件
def write_list(file_path, data_list):
    # 使用with语句打开文件，确保最后文件会被正确关闭
    with open(file_path, 'w', encoding='utf-8') as file:
        # 遍历数据列表
        for item in data_list:
            # 写入每一行数据到文件，每个item后面添加换行符
            file.write(item + '\n')

            
# 增加外部url到检测清单，同时支持检测m3u格式url
# urls里所有的源都读到这里。
urls_all_lines = []
def get_url_file_extension(url):
    # 解析URL
    parsed_url = urlparse(url)
    # 获取路径部分
    path = parsed_url.path
    # 提取文件扩展名
    extension = os.path.splitext(path)[1]
    return extension
def convert_m3u_to_txt(m3u_content):
    # 分行处理
    lines = m3u_content.split('\n')
    
    # 用于存储结果的列表
    txt_lines = []
    
    # 临时变量用于存储频道名称
    channel_name = ""
    
    for line in lines:
        # 过滤掉 #EXTM3U 开头的行
        if line.startswith("#EXTM3U"):
            continue
        # 处理 #EXTINF 开头的行
        if line.startswith("#EXTINF"):
            # 获取频道名称（假设频道名称在引号后）
            channel_name = line.split(',')[-1].strip()
        # 处理 URL 行
        elif line.startswith("http"):
            txt_lines.append(f"{channel_name},{line.strip()}")
    
    # 将结果合并成一个字符串，以换行符分隔
    return '\n'.join(txt_lines)

def process_url(url):
    try:
        # 打开URL并读取内容
        with urllib.request.urlopen(url) as response:
            # 以二进制方式读取数据
            data = response.read()
            # 将二进制数据解码为字符串
            text = data.decode('utf-8')
            if get_url_file_extension(url)==".m3u" or get_url_file_extension(url)==".m3u8":
                urls_all_lines.append(convert_m3u_to_txt(text))
            elif get_url_file_extension(url)==".txt":
                lines = text.split('\n')
                for line in lines:
                    if  "#genre#" not in line and "," in line and "://" in line:
                        #channel_name=line.split(',')[0].strip()
                        #channel_address=line.split(',')[1].strip()
                        urls_all_lines.append(line.strip())
    
    except Exception as e:
        print(f"处理URL时发生错误：{e}")

# 去重复源 2024-08-06 (检测前剔除重复url，提高检测效率)
def remove_duplicates_url(lines):
    urls =[]
    newlines=[]
    for line in lines:
        if "," in line and "://" in line:
            # channel_name=line.split(',')[0].strip()
            channel_url=line.split(',')[1].strip()
            if channel_url not in urls: # 如果发现当前url不在清单中，则假如newlines
                urls.append(channel_url)
                newlines.append(line)
    return newlines
# 处理带$的URL，把$之后的内容都去掉（包括$也去掉） 【2024-08-08 22:29:11】
#def clean_url(url):
#    last_dollar_index = url.rfind('$')  # 安全起见找最后一个$处理
#    if last_dollar_index != -1:
#        return url[:last_dollar_index]
#    return url
def clean_url(lines):
    urls =[]
    newlines=[]
    for line in lines:
        if "," in line and "://" in line:
            last_dollar_index = line.rfind('$')
            if last_dollar_index != -1:
                line=line[:last_dollar_index]
            newlines.append(line)
    return newlines
# 处理带#的URL  【2024-08-09 23:53:26】
def split_url(lines):
    newlines=[]
    for line in lines:
        # 拆分成频道名和URL部分
        channel_name, channel_address = line.split(',', 1)
        #需要加处理带#号源=予加速源
        if  "#" not in channel_address:
            newlines.append(line)
        elif  "#" in channel_address and "://" in channel_address: 
            # 如果有“#”号，则根据“#”号分隔
            url_list = channel_address.split('#')
            for url in url_list:
                if "://" in url: 
                    newline=f'{channel_name},{url}'
                    newlines.append(line)
    return newlines
# 判断是否是直接运行此脚本
if __name__ == "__main__":
    # 定义一个URL列表，这些URL将被用来获取直播源数据
    urls = [
        # 直播源数据的GitHub仓库URL，它们提供m3u格式的直播源列表
        'https://raw.githubusercontent.com/mengxianshengaaa/IPTV/main/iptv_list.txt',
        'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/cn.m3u',
        # 其他直播源URL，可以是直接的m3u文件或包含直播源的网页
        'http://gg.gg/cctvgg'   # 一个直播源的URL，添加于特定日期
    ]
    
    # 遍历URL列表并处理每个URL
    for url in urls:
        print(f"处理URL: {url}")
        process_url(url)   # 调用process_url函数读取直播源并存储到urls_all_lines列表
    # 获取当前脚本文件所在的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取当前脚本文件所在目录的上一级目录
    parent_dir = os.path.dirname(current_dir)
    # 定义输入文件路径，它们包含之前处理得到的数据
    input_file1 = os.path.join(parent_dir, 'merged_output.txt')  
    input_file2 = os.path.join(current_dir, 'blacklist_auto.txt')  
    # 定义成功清单文件路径，存储有效直播源
    success_file = os.path.join(current_dir, 'whitelist_auto.txt')  
    # 定义另一个成功清单文件路径，存储可以直接引用的直播源
    success_file_tv = os.path.join(current_dir, 'whitelist_auto_tv.txt')  
    # 定义黑名单文件路径，存储无效直播源
    blacklist_file = os.path.join(current_dir, 'blacklist_auto.txt')  
    # 读取输入文件内容并存储到lines1和lines2
    lines1 = read_txt_file(input_file1)
    lines2 = read_txt_file(input_file2)
    # 将从URL获取的直播源、input_file1和input_file2中的行合并到lines
    lines = urls_all_lines + lines1 + lines2 
    # 计算合并后的直播源总数
    urls_hj_before = len(lines)
    # 分级处理带#号的直播源地址，这可能意味着处理不同的直播源质量或选项
    lines=split_url(lines)
    # 计算处理后直播源的数量
    urls_hj_before2 = len(lines)
    # 清除直播源URL中的$符号，这可能是为了规范化URL
    lines=clean_url(lines)
    # 计算清除$符号后直播源的数量
    urls_hj_before3 = len(lines)
    # 去除重复的直播源URL
    lines=remove_duplicates_url(lines)
    # 计算去重后的直播源数量
    urls_hj = len(lines)
    # 使用多线程处理直播源并生成有效和无效的直播源列表
    successlist, blacklist = process_urls_multithreaded(lines)
    
    # 定义排序函数，根据响应时间排序
    def successlist_sort_key(item):
        time_str = item.split(',')[0].replace('ms', '')
        return float(time_str)
    
    # 根据响应时间对成功列表进行排序
    successlist=sorted(successlist, key=successlist_sort_key)
    # 对黑名单进行排序
    blacklist=sorted(blacklist)
    # 计算有效和无效直播源的数量
    urls_ok = len(successlist)
    urls_ng = len(blacklist)
    # 整理successlist，生成可以直接引用的直播源列表
    def remove_prefix_from_lines(lines):
        result = []
        for line in lines:
            if  "#genre#" not in line and "," in line and "://" in line:
                parts = line.split(",")
                result.append(",".join(parts[1:]))
        return result
    # 添加时间戳和其他信息到成功和黑名单
    version = datetime.now().strftime("%Y%m%d-%H-%M-%S") + ",url"
    successlist_tv = ["更新时间,#genre#"] + [version] + ['\n'] + ["whitelist,#genre#"] + remove_prefix_from_lines(successlist)
    successlist = ["更新时间,#genre#"] + [version] + ['\n'] + ["RespoTime,whitelist,#genre#"] + successlist
    blacklist = ["更新时间,#genre#"] + [version] + ['\n'] + ["blacklist,#genre#"] + blacklist
    # 将整理后的直播源列表写入文件
    write_list(success_file, successlist)
    write_list(success_file_tv, successlist_tv)
    # 将黑名单写入文件
    write_list(blacklist_file, blacklist)
    # 打印成功清单和黑名单文件的生成信息
    print(f"成功清单文件已生成: {success_file}")
    print(f"成功清单文件已生成(tv): {success_file_tv}")
    print(f"黑名单文件已生成: {blacklist_file}")
    # 写入历史记录文件
    timenow = datetime.now().strftime("%Y%m%d_%H_%M_%S")
    history_success_file = f'history/blacklist/{timenow}_whitelist_auto.txt'
    history_blacklist_file = f'history/blacklist/{timenow}_blacklist_auto.txt'
    write_list(history_success_file, successlist)
    write_list(history_blacklist_file, blacklist)
    # 打印历史记录文件的生成信息
    print(f"history成功清单文件已生成: {history_success_file}")
    print(f"history黑名单文件已生成: {history_blacklist_file}")
    # 计算脚本执行结束时间
    timeend = datetime.now()
    # 计算脚本执行所用的总时间
    elapsed_time = timeend - timestart
    total_seconds = elapsed_time.total_seconds()
    # 将总时间转换为分钟和秒
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    # 格式化脚本开始和结束的时间字符串
    timestart_str = timestart.strftime("%Y%m%d_%H_%M_%S")
    timeend_str = timeend.strftime("%Y%m%d_%H_%M_%S")

    # 打印脚本开始、结束和执行时间信息
    print(f"开始时间: {timestart_str}")
    print(f"结束时间: {timeend_str}")
    print(f"执行时间: {minutes} 分 {seconds} 秒")
    # 打印处理前后的直播源数量信息
    print(f"urls_hj最初: {urls_hj_before} ")
    print(f"urls_hj分解井号源后: {urls_hj_before2} ")
    print(f"urls_hj去$后: {urls_hj_before3} ")
    print(f"urls_hj去重后: {urls_hj} ")
    print(f"  urls_ok: {urls_ok} ")
    print(f"  urls_ng: {urls_ng} ")
