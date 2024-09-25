import re

def compare_and_write_uniques(file1_path, file2_path, output_path):
    # 正则表达式模式，用于匹配IP地址和域名
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    domain_pattern = r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b'

    # 用于存储第二个文件中的IP地址和域名集合
    file2_ips_and_domains = set()

    # 读取第二个文件，提取IP地址和域名并添加到集合
    with open(file2_path, 'r', encoding='utf-8') as file2:
        content2 = file2.read()
        # 查找IP地址并添加到集合
        ips = re.findall(ip_pattern, content2)
        file2_ips_and_domains.update(ips)
        # 查找域名并添加到集合
        domains = re.findall(domain_pattern, content2)
        file2_ips_and_domains.update(domains)

    # 用于存储要写入新文件的独特IP地址和域名
    unique_ips_and_domains = set()

    # 读取第一个文件，检查IP地址和域名是否在第二个文件集合中不存在
    with open(file1_path, 'r', encoding='utf-8') as file1:
        content1 = file1.read()
        # 查找IP地址
        ips_in_file1 = re.findall(ip_pattern, content1)
        for ip in ips_in_file1:
            if ip not in file2_ips_and_domains:
                unique_ips_and_domains.add(ip)
        # 查找域名
        domains_in_file1 = re.findall(domain_pattern, content1)
        for domain in domains_in_file1:
            if domain not in file2_ips_and_domains:
                unique_ips_and_domains.add(domain)

    # 将独特的IP地址和域名写入新文件
    with open(output_path, 'w', encoding='utf-8') as output_file:
        for item in unique_ips_and_domains:
            output_file.write(item + '\n')

# 示例用法
file1_path = '无效IP.txt'
file2_path = '网络收集.txt'
output_path = '无效IP.txt'
compare_and_write_uniques(file1_path, file2_path, output_path)
