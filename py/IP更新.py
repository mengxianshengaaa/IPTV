import requests
import re
import cv2  # 导入OpenCV库

# 更新广东组播定义fofa链接列表
fofa_urls = [
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJmb3NoYW4i',   # 佛山市
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJHdWFuZ3pob3Ui',   # 广州市
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJzaGFudG91IiA%3D',  # 广东汕头
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJ6aGFvcWluZyI%3D',  # 广东肇庆
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJtYW9taW5nIg%3D%3D',  # 广东茂名
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJ6aHVoYWki',  # 广东珠海
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJzaGVuemhlbiI%3D',  # 广东深圳
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJodWl6aG91Ig%3D%3D',   # 惠州市
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJqaWFuZ21lbiI%3D'    # 江门市
]
# 尝试从fofa链接提取IP地址和端口号，并去除重复项
def extract_unique_ip_ports(fofa_urls):
    all_unique_ips_ports = set()
    for fofa_url in fofa_urls:
        try:
            response = requests.get(fofa_url, timeout=10)
            html_content = response.text
            # 使用正则表达式匹配IP地址和端口号
            ips_ports = re.findall(r'(\d+\.\d+\.\d+\.\d+:\d+)', html_content)
            all_unique_ips_ports.update(ips_ports)  # 将IP和端口号添加到集合中
        except requests.RequestException as e:
            print(f"请求 {fofa_url} 时发生错误: {e}")
    return list(all_unique_ips_ports)
# 检查视频流的可达性
def check_video_stream_connectivity(ip_port, urls_udp):
    video_url = f"http://{ip_port}{urls_udp}"
    cap = cv2.VideoCapture(video_url)
    if cap.isOpened():
        cap.release()
        return ip_port  # 如果打开成功，返回IP和端口号
    else:
        cap.release()
        return None
# 从本地文件读取内容
def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
    return None
# 更新文件中的IP地址并将每个IP追加写入
def update_and_write_ips(file_path, valid_ips_ports):
    try:
        original_content = read_file_content(file_path)
        if original_content:
            # 假设原文件中的IP地址格式为 http://IP:PORT
            ip_port_pattern = r'http://(\d+\.\d+\.\d+:\d+)'
            new_lines = []
            for line in original_content.splitlines():
                match = re.search(ip_port_pattern, line)
                if match:
                    # 找到一个IP地址，替换为有效的IP地址列表
                    for valid_ip_port in valid_ips_ports:
                        new_line = re.sub(ip_port_pattern, f'http://{valid_ip_port}', line)
                        new_lines.append(new_line)
            # 将更新后的内容追加到文件末尾
            with open(file_path, 'a', encoding='utf-8') as file:
                file.write("\n".join(new_lines) + "\n")
            print(f"文件 {file_path} 已更新并追加保存。")
    except Exception as e:
        print(f"更新文件 {file_path} 时发生错误: {e}")
# 定义组播地址和端口
urls_udp = "/rtp/239.77.1.19:5146"
# 提取唯一的IP地址和端口号
unique_ips_ports = extract_unique_ip_ports(fofa_urls)
# 存储所有有效的IP地址和端口号
valid_ips_ports = [ip_port for ip_port in unique_ips_ports if check_video_stream_connectivity(ip_port, urls_udp)]
if valid_ips_ports:
    print("找到的可访问视频流服务的IP地址和端口号：")
    for valid_ip_port in valid_ips_ports:
        print(valid_ip_port)
    # 指定需要更新的本地文件路径
    local_file_path = '广东电信.txt'
    # 更新文件中的IP地址并将每个IP写入新行
    update_and_write_ips(local_file_path, valid_ips_ports)
else:
    print("没有找到可访问的视频流服务或者没有提取到IP地址和端口号。")




# 更新四川电信组播定义fofa链接列表
fofa_urls = [
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJjaGVuZ2R1Ig%3D%3D',   # 成都
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJYaWNoYW5nIg%3D%3D',   # 西昌
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJtaWFueWFuZyI%3D',  # 绵阳
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJsdXpob3Ui',  # 泸州
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJkYXpob3Ui',  # 达州
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJuYW5jaG9uZyI%3D'  # 南充
]

# 尝试从fofa链接提取IP地址和端口号，并去除重复项
def extract_unique_ip_ports(fofa_urls):
    all_unique_ips_ports = set()
    for fofa_url in fofa_urls:
        try:
            response = requests.get(fofa_url, timeout=10)
            html_content = response.text
            # 使用正则表达式匹配IP地址和端口号
            ips_ports = re.findall(r'(\d+\.\d+\.\d+\.\d+:\d+)', html_content)
            all_unique_ips_ports.update(ips_ports)  # 将IP和端口号添加到集合中
        except requests.RequestException as e:
            print(f"请求 {fofa_url} 时发生错误: {e}")
    return list(all_unique_ips_ports)
# 检查视频流的可达性
def check_video_stream_connectivity(ip_port, urls_udp):
    video_url = f"http://{ip_port}{urls_udp}"
    cap = cv2.VideoCapture(video_url)
    if cap.isOpened():
        cap.release()
        return ip_port  # 如果打开成功，返回IP和端口号
    else:
        cap.release()
        return None
# 从本地文件读取内容
def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
    return None
# 更新文件中的IP地址并将每个IP追加写入
def update_and_write_ips(file_path, valid_ips_ports):
    try:
        original_content = read_file_content(file_path)
        if original_content:
            # 假设原文件中的IP地址格式为 http://IP:PORT
            ip_port_pattern = r'http://(\d+\.\d+\.\d+:\d+)'
            new_lines = []
            for line in original_content.splitlines():
                match = re.search(ip_port_pattern, line)
                if match:
                    # 找到一个IP地址，替换为有效的IP地址列表
                    for valid_ip_port in valid_ips_ports:
                        new_line = re.sub(ip_port_pattern, f'http://{valid_ip_port}', line)
                        new_lines.append(new_line)
            # 将更新后的内容追加到文件末尾
            with open(file_path, 'a', encoding='utf-8') as file:
                file.write("\n".join(new_lines) + "\n")
            print(f"文件 {file_path} 已更新并追加保存。")
    except Exception as e:
        print(f"更新文件 {file_path} 时发生错误: {e}")
# 定义组播地址和端口
urls_udp = "/rtp/239.93.0.58:5140"
# 提取唯一的IP地址和端口号
unique_ips_ports = extract_unique_ip_ports(fofa_urls)
# 存储所有有效的IP地址和端口号
valid_ips_ports = [ip_port for ip_port in unique_ips_ports if check_video_stream_connectivity(ip_port, urls_udp)]
if valid_ips_ports:
    print("找到的可访问视频流服务的IP地址和端口号：")
    for valid_ip_port in valid_ips_ports:
        print(valid_ip_port)
    # 指定需要更新的本地文件路径
    local_file_path = '四川电信.txt'
    # 更新文件中的IP地址并将每个IP写入新行
    update_and_write_ips(local_file_path, valid_ips_ports)
else:
    print("没有找到可访问的视频流服务或者没有提取到IP地址和端口号。")




# 更新湖北电信组播定义fofa链接列表
fofa_urls = [
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJ3dWhhbiI%3D',   # 武汉
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJodWFuZ3NoaSI%3D',   # 黄石
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJ4aWFuZ3lhbmci',  # 襄阳
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJqaW5nemhvdSI%3D',  # 荆州
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJodWFuZ2dhbmci',  # 黄冈
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJ4aWFvZ2FuIg%3D%3D',  # 孝感
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJKaW5nbWVuIg%3D%3D',  # 荆门
    'https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjaXR5PSJ4aWFubmluZyI%3D'  # 咸宁
]

# 尝试从fofa链接提取IP地址和端口号，并去除重复项
def extract_unique_ip_ports(fofa_urls):
    all_unique_ips_ports = set()
    for fofa_url in fofa_urls:
        try:
            response = requests.get(fofa_url, timeout=10)
            html_content = response.text
            # 使用正则表达式匹配IP地址和端口号
            ips_ports = re.findall(r'(\d+\.\d+\.\d+\.\d+:\d+)', html_content)
            all_unique_ips_ports.update(ips_ports)  # 将IP和端口号添加到集合中
        except requests.RequestException as e:
            print(f"请求 {fofa_url} 时发生错误: {e}")
    return list(all_unique_ips_ports)
# 检查视频流的可达性
def check_video_stream_connectivity(ip_port, urls_udp):
    video_url = f"http://{ip_port}{urls_udp}"
    cap = cv2.VideoCapture(video_url)
    if cap.isOpened():
        cap.release()
        return ip_port  # 如果打开成功，返回IP和端口号
    else:
        cap.release()
        return None
# 从本地文件读取内容
def read_file_content(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到。")
    return None
# 更新文件中的IP地址并将每个IP追加写入
def update_and_write_ips(file_path, valid_ips_ports):
    try:
        original_content = read_file_content(file_path)
        if original_content:
            # 假设原文件中的IP地址格式为 http://IP:PORT
            ip_port_pattern = r'http://(\d+\.\d+\.\d+:\d+)'
            new_lines = []
            for line in original_content.splitlines():
                match = re.search(ip_port_pattern, line)
                if match:
                    # 找到一个IP地址，替换为有效的IP地址列表
                    for valid_ip_port in valid_ips_ports:
                        new_line = re.sub(ip_port_pattern, f'http://{valid_ip_port}', line)
                        new_lines.append(new_line)
            # 将更新后的内容追加到文件末尾
            with open(file_path, 'a', encoding='utf-8') as file:
                file.write("\n".join(new_lines) + "\n")
            print(f"文件 {file_path} 已更新并追加保存。")
    except Exception as e:
        print(f"更新文件 {file_path} 时发生错误: {e}")
# 定义组播地址和端口
urls_udp = "/rtp/239.254.96.96:8550"
# 提取唯一的IP地址和端口号
unique_ips_ports = extract_unique_ip_ports(fofa_urls)
# 存储所有有效的IP地址和端口号
valid_ips_ports = [ip_port for ip_port in unique_ips_ports if check_video_stream_connectivity(ip_port, urls_udp)]
if valid_ips_ports:
    print("找到的可访问视频流服务的IP地址和端口号：")
    for valid_ip_port in valid_ips_ports:
        print(valid_ip_port)
    # 指定需要更新的本地文件路径
    local_file_path = '湖北电信.txt'
    # 更新文件中的IP地址并将每个IP写入新行
    update_and_write_ips(local_file_path, valid_ips_ports)
else:
    print("没有找到可访问的视频流服务或者没有提取到IP地址和端口号。")



fofa_url = 'https://fofa.info/result?qbase64=InVkcHh5IiAmJiByZWdpb249IkhlYmVpIg%3D%3D'   #河北
# 尝试从fofa链接提取IP地址和端口号，并去除重复项
def extract_unique_ip_ports(fofa_url):
    try:
        response = requests.get(fofa_url, timeout=13)
        html_content = response.text
        # 使用正则表达式匹配IP地址和端口号
        ips_ports = re.findall(r'(\d+\.\d+\.\d+\.\d+:\d+)', html_content)
        unique_ips_ports = list(set(ips_ports))  # 去除重复的IP地址和端口号
        return unique_ips_ports if unique_ips_ports else None
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return None

# 检查视频流的可达性
def check_video_stream_connectivity(ip_port, urls_udp):
    try:
        # 构造完整的视频URL
        video_url = f"http://{ip_port}{urls_udp}"
        # 用OpenCV读取视频
        cap = cv2.VideoCapture(video_url)
        
        # 检查视频是否成功打开
        if not cap.isOpened():
            print(f"视频URL {video_url} 无效")
            return None
        else:
            # 读取视频的宽度和高度
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"视频URL {video_url} 的分辨率为 {width}x{height}")
            # 检查分辨率是否大于0
            if width > 0 and height > 0:
                return ip_port  # 返回有效的IP和端口
            # 关闭视频流
            cap.release()
    except Exception as e:
        print(f"访问 {ip_port} 失败: {e}")
    return None

# 更新文件中的IP地址和端口号
def update_files(accessible_ip_port, files_to_update):
    for file_info in files_to_update:
        try:
            # 读取原始文件内容
            response = requests.get(file_info['url'])
            file_content = response.text

            # 替换文件中的IP地址和端口号
            # 假设文件中的IP地址和端口号格式为 http://IP:PORT
            ip_port_pattern = r'(http://\d+\.\d+\.\d+\.\d+:\d+)'
            updated_content = re.sub(ip_port_pattern, f'http://{accessible_ip_port}', file_content)

            # 保存更新后的内容到新文件
            with open(file_info['filename'], 'w', encoding='utf-8') as file:
                file.write(updated_content)

            print(f"文件 {file_info['filename']} 已更新并保存。")
        except requests.RequestException as e:
            print(f"无法更新文件 {file_info['filename']}，错误: {e}")

# 定义组播地址和端口
urls_udp = "/udp/239.254.200.45:8008"

# 提取唯一的IP地址和端口号
unique_ips_ports = extract_unique_ip_ports(fofa_url)

if unique_ips_ports:
    print("提取到的唯一IP地址和端口号：")
    for ip_port in unique_ips_ports:
        print(ip_port)
    
    # 测试每个IP地址和端口号，直到找到一个可访问的视频流
    valid_ip = None
    for ip_port in unique_ips_ports:
        valid_ip = check_video_stream_connectivity(ip_port, urls_udp)
        if valid_ip:
            break  # 找到有效的IP后，不再继续循环

    if valid_ip:
        print(f"找到可访问的视频流服务: {valid_ip}")
        # 定义需要更新的文件列表
        files_to_update = [
            {'url': 'https://raw.githubusercontent.com/frxz751113/IPTVzb/main/河北电信.txt', 'filename': '河北电信.txt'} #,
            #{'url': 'https://raw.githubusercontent.com/frxz751113/IPTVzb/main/广东电信.m3u', 'filename': '广东电信.m3u'}
        ]

        # 更新文件中的IP地址和端口号
        update_files(valid_ip, files_to_update)
    else:
        print("没有找到可访问的视频流服务。")
else:
    print("没有提取到IP地址和端口号。")



fofa_url = 'https://fofa.info/result?qbase64=InVkcHh5IiAmJiByZWdpb249Ikh1bmFuIg%3D%3D'   #湖南
# 尝试从fofa链接提取IP地址和端口号，并去除重复项
def extract_unique_ip_ports(fofa_url):
    try:
        response = requests.get(fofa_url, timeout=13)
        html_content = response.text
        # 使用正则表达式匹配IP地址和端口号
        ips_ports = re.findall(r'(\d+\.\d+\.\d+\.\d+:\d+)', html_content)
        unique_ips_ports = list(set(ips_ports))  # 去除重复的IP地址和端口号
        return unique_ips_ports if unique_ips_ports else None
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return None

# 检查视频流的可达性
def check_video_stream_connectivity(ip_port, urls_udp):
    try:
        # 构造完整的视频URL
        video_url = f"http://{ip_port}{urls_udp}"
        # 用OpenCV读取视频
        cap = cv2.VideoCapture(video_url)
        
        # 检查视频是否成功打开
        if not cap.isOpened():
            print(f"视频URL {video_url} 无效")
            return None
        else:
            # 读取视频的宽度和高度
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(f"视频URL {video_url} 的分辨率为 {width}x{height}")
            # 检查分辨率是否大于0
            if width > 0 and height > 0:
                return ip_port  # 返回有效的IP和端口
            # 关闭视频流
            cap.release()
    except Exception as e:
        print(f"访问 {ip_port} 失败: {e}")
    return None

# 更新文件中的IP地址和端口号
def update_files(accessible_ip_port, files_to_update):
    for file_info in files_to_update:
        try:
            # 读取原始文件内容
            response = requests.get(file_info['url'])
            file_content = response.text

            # 替换文件中的IP地址和端口号
            # 假设文件中的IP地址和端口号格式为 http://IP:PORT
            ip_port_pattern = r'(http://\d+\.\d+\.\d+\.\d+:\d+)'
            updated_content = re.sub(ip_port_pattern, f'http://{accessible_ip_port}', file_content)

            # 保存更新后的内容到新文件
            with open(file_info['filename'], 'w', encoding='utf-8') as file:
                file.write(updated_content)

            print(f"文件 {file_info['filename']} 已更新并保存。")
        except requests.RequestException as e:
            print(f"无法更新文件 {file_info['filename']}，错误: {e}")

# 定义组播地址和端口
urls_udp = "/udp/239.76.253.151:9000"

# 提取唯一的IP地址和端口号
unique_ips_ports = extract_unique_ip_ports(fofa_url)

if unique_ips_ports:
    print("提取到的唯一IP地址和端口号：")
    for ip_port in unique_ips_ports:
        print(ip_port)
    
    # 测试每个IP地址和端口号，直到找到一个可访问的视频流
    valid_ip = None
    for ip_port in unique_ips_ports:
        valid_ip = check_video_stream_connectivity(ip_port, urls_udp)
        if valid_ip:
            break  # 找到有效的IP后，不再继续循环

    if valid_ip:
        print(f"找到可访问的视频流服务: {valid_ip}")
        # 定义需要更新的文件列表
        files_to_update = [
            {'url': 'https://raw.githubusercontent.com/frxz751113/IPTVzb/main/湖南电信.txt', 'filename': '湖南电信.txt'} #,
            #{'url': 'https://raw.githubusercontent.com/frxz751113/IPTVzb/main/广东电信.m3u', 'filename': '广东电信.m3u'}
        ]

        # 更新文件中的IP地址和端口号
        update_files(valid_ip, files_to_update)
    else:
        print("没有找到可访问的视频流服务。")
else:
    print("没有提取到IP地址和端口号。")
