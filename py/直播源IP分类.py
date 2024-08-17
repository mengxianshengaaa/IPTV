import re
from collections import defaultdict

# 正则表达式匹配IP地址和genre标签
ip_pattern = re.compile(r'http://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):\d+/')
genre_pattern = re.compile(r'^# (.+),#genre#$')

# 用于存储按IP分类的直播源，以及genre标签的原始顺序索引
sources_by_ip = defaultdict(list)
genre_order = []

# 读取文件并分类
def classify_sources(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if line.startswith('#') and genre_pattern.match(line):
                # 处理genre行
                genre_name = genre_pattern.match(line).group(1).strip()
                genre_order.append((line_number, genre_name))
            else:
                match = ip_pattern.search(line)
                if match:
                    ip = match.group(1)
                    sources_by_ip[ip].append((line_number, line))

# 写入结果到新文件，保持genre标签的原始顺序
def write_to_file(output_file_path, sources_by_ip, genre_order):
    with open(output_file_path, 'w', encoding='utf-8') as file:
        for ip, sources in sources_by_ip.items():
            # 按原始顺序写入genre标签
            for _, genre_name in genre_order:
                file.write(f"# {genre_name},#genre#\n")
                
            # 写入该IP的直播源列表
            for line_number, source in sorted(sources, key=lambda x: x[0]):
                file.write(source + '\n')
            file.write("\n")  # 添加空行以便分隔不同IP的列表

# 主程序
if __name__ == "__main__":
    input_file_path = '1.txt'  # 直播源文件路径
    output_file_path = 'sorted_live_sources.txt'  # 输出文件路径

    classify_sources(input_file_path)
    write_to_file(output_file_path, sources_by_ip, genre_order)
