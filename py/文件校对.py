def extract_unique_lines(file1_path, file2_path, output_path):
    # 用于存储两个文件中所有行的集合
    all_lines_set = set()
    # 用于存储两个文件中重复行的集合
    duplicate_lines_set = set()

    # 读取第一个文件的每一行，添加到集合中
    with open(file1_path, 'r', encoding='utf-8') as file1:
        for line in file1:
            line = line.strip()
            all_lines_set.add(line)
            if line in duplicate_lines_set:
                continue
            duplicate_lines_set.add(line)

    # 读取第二个文件的每一行，检查是否在第一个文件中出现过，处理后添加到相应集合
    with open(file2_path, 'r', encoding='utf-8') as file2:
        for line in file2:
            line = line.strip()
            if line in all_lines_set:
                duplicate_lines_set.add(line)
            else:
                all_lines_set.add(line)

    # 找到不重复的行
    unique_lines = all_lines_set - duplicate_lines_set

    # 将不重复的行写入新文件
    with open(output_path, 'w', encoding='utf-8') as output_file:
        for line in unique_lines:
            output_file.write(line + '\n')

# 示例用法
file1_path = '无效IP.txt'
file2_path = '网络收集.txt'
output_path = '无效IP.txt'
extract_unique_lines(file1_path, file2_path, output_path)

import re

def extract_ips_and_domains(input_file_path, output_file_path):
    # 正则表达式模式，用于匹配IP地址和域名
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    domain_pattern = r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b'

    # 集合用于存储提取到的IP地址和域名，确保唯一性
    ips_and_domains = set()

    # 打开输入文件并读取内容
    with open(input_file_path, 'r', encoding='utf-8') as input_file:
        content = input_file.read()

        # 查找IP地址并添加到集合
        ips = re.findall(ip_pattern, content)
        ips_and_domains.update(ips)

        # 查找域名并添加到集合
        domains = re.findall(domain_pattern, content)
        ips_and_domains.update(domains)

    # 打开输出文件并写入提取到的IP地址和域名
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        for item in ips_and_domains:
            output_file.write(item + '\n')

# 示例用法
input_file_path = '无效IP.txt'
output_file_path = '无效IP.txt'
extract_ips_and_domains(input_file_path, output_file_path)

