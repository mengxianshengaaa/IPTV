import requests
from tqdm import tqdm

# 要检测的文件和结果文件的文件名
input_file = '综合源.txt'
output_file = 'valid_sources.txt'


def is_link_valid(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        # 检查HTTP状态码是否表示成功
        return 200 <= response.status_code < 308
    except requests.RequestException as e:
        # 打印错误信息，但继续执行
        print(f"请求错误: {e}")
        return False

def process_file(input_filename, output_filename):
    with open(input_filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 使用tqdm管理进度条
    with tqdm(total=len(lines), desc="Processing lines") as progress:
        with open(output_filename, 'w', encoding='utf-8') as output_file:
            for line in lines:
                # 忽略空行和以#开头的注释行
                if line.strip() and not line.startswith('#'):
                    parts = line.split(',', 1)  # 只分割第一部分
                    if len(parts) == 2:
                        channel_name, url = parts
                        url = url.strip()  # 移除URL两端的空白字符
                        if is_link_valid(url):
                            output_file.write(line)
                        progress.update(1)  # 更新进度条

# 执行函数
process_file(input_file, output_file)
print(f"有效链接已写入到 {output_file}")
