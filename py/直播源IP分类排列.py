import re
from collections import OrderedDict

# 正则表达式匹配IP地址
ip_pattern = re.compile(r'http://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):\d+/')

# 用于存储按IP分类的直播源
sources_by_ip = OrderedDict()

# 读取文件并分类
def classify_sources(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 忽略空行和注释行
            if line.strip() == '' or line.startswith('#'):
                continue
            match = ip_pattern.search(line)
            if match:
                ip = match.group(1)
                if ip not in sources_by_ip:
                    sources_by_ip[ip] = []
                sources_by_ip[ip].append(line)
            elif 'genre' in line:
                # 特殊处理genre行
                if 'genre' not in sources_by_ip:
                    sources_by_ip['genre'] = []
                #sources_by_ip['genre'].append(line)
                pass

# 写入结果到新文件
def write_to_file(output_file_path, sources_by_ip):
    with open(output_file_path, 'w', encoding='utf-8') as file:
        for ip, sources in sources_by_ip.items():
            #file.write(f"# 以下是IP为{ip}的直播源列表\n")
            file.write(f"{ip},#genre#\n")
            for source in sources:
                file.write(source)
            file.write("\n")  # 添加空行以便分隔不同IP的列表

# 主程序
if __name__ == "__main__":
    input_file_path = '1.txt'  # 直播源文件路径
    output_file_path = 'sorted_live_sources.txt'  # 输出文件路径

    classify_sources(input_file_path)
    write_to_file(output_file_path, sources_by_ip)
